[CmdletBinding()]
param(
    [ValidateSet('Plan', 'Execute', 'Cleanup')]
    [string]$Mode = 'Plan',

    [string]$PathToAtomicsFolder = '',

    [switch]$ConfirmExecution
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScenarioId = 'cisa-aa23-289a-ubuntu'
$ExpectedAtomicCommit = '6132b92779873cb0d05bef07ba0a480d47eb1cc8'
$ScenarioRoot = '/tmp/endpointir-bench/cisa-aa23-289a-ubuntu'
$AuditPath = '/tmp/endpointir-bench/cisa-aa23-289a-ubuntu/confluence-audit.json'
$StagedFilePath = '/tmp/endpointir-bench/cisa-aa23-289a-ubuntu/staged-loot.txt'
$MockLogPath = '/tmp/endpointir-bench/cisa-aa23-289a-ubuntu/mock-exfil.json'
$MockUrl = 'http://127.0.0.1:18089/upload'
$FakeDataMarker = 'secrets, api keys, passwords - T1567.004 atomic test'

$Steps = @(
    [pscustomobject]@{ Order = 1; Technique = 'T1136.003'; Implementation = 'Custom canary'; Name = 'Write harmless Confluence administrator audit event' },
    [pscustomobject]@{ Order = 2; Technique = 'T1567.004'; Implementation = 'Atomic + loopback Mock'; Name = 'Stage fake text and upload it with curl' }
)

function Show-Plan {
    Write-Output "Scenario: $ScenarioId"
    Write-Output 'Target: one disposable, recoverable Ubuntu VM'
    Write-Output "Network boundary: loopback only ($MockUrl)"
    Write-Output 'Elevation: not required'
    Write-Output "Pinned Atomic commit: $ExpectedAtomicCommit"
    Write-Output ''
    Write-Output ($Steps | Format-Table Order, Technique, Implementation, Name -AutoSize | Out-String).TrimEnd()
    Write-Output ''
    Write-Output "Expected mutations: $AuditPath, $StagedFilePath, and $MockLogPath."
    Write-Output "Cleanup scope: only $ScenarioRoot."
    Write-Output 'Plan mode performed no host checks and made no changes.'
}

function Resolve-ValidatedAtomicsFolder {
    param([switch]$RequireCurl)

    $isLinuxValue = Get-Variable -Name IsLinux -ValueOnly -ErrorAction SilentlyContinue
    if (-not $isLinuxValue) {
        throw 'This scenario must run under PowerShell Core on Linux.'
    }
    if (-not (Test-Path -LiteralPath '/etc/os-release' -PathType Leaf)) {
        throw 'Unable to identify the Linux distribution because /etc/os-release is missing.'
    }
    $osRelease = (Get-Content -LiteralPath '/etc/os-release') -join "`n"
    if ($osRelease -notmatch '(?m)^ID="?ubuntu"?$') {
        throw 'This scenario is restricted to an Ubuntu target.'
    }
    if (-not (Get-Command Invoke-AtomicTest -ErrorAction SilentlyContinue)) {
        throw 'Invoke-AtomicTest is unavailable. Install or import Invoke-AtomicRedTeam first.'
    }
    if ($RequireCurl -and (-not (Get-Command curl -ErrorAction SilentlyContinue))) {
        throw 'curl is required by the selected Linux Atomic test.'
    }
    if ([string]::IsNullOrWhiteSpace($PathToAtomicsFolder)) {
        throw 'Pass -PathToAtomicsFolder with the pinned atomic-red-team/atomics directory.'
    }
    if (-not (Test-Path -LiteralPath $PathToAtomicsFolder -PathType Container)) {
        throw "Atomic folder not found: $PathToAtomicsFolder"
    }

    $resolvedAtomics = (Resolve-Path -LiteralPath $PathToAtomicsFolder).Path
    if ((Split-Path -Leaf $resolvedAtomics) -ne 'atomics') {
        throw "PathToAtomicsFolder must identify the checkout's atomics directory: $resolvedAtomics"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $resolvedAtomics 'T1567.004/T1567.004.yaml'))) {
        throw "The supplied atomics directory does not contain T1567.004: $resolvedAtomics"
    }

    $gitCommand = Get-Command git -ErrorAction SilentlyContinue
    if (-not $gitCommand) {
        throw 'git is required to verify the pinned Atomic Red Team commit before mutation.'
    }
    $atomicRepository = Split-Path -Parent $resolvedAtomics
    $actualCommitOutput = @(& $gitCommand.Source -C $atomicRepository rev-parse HEAD 2>&1)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read the Atomic checkout commit at $atomicRepository."
    }
    $actualCommit = ([string]$actualCommitOutput[-1]).Trim()
    if ($actualCommit -ne $ExpectedAtomicCommit) {
        throw "Atomic checkout mismatch. Expected $ExpectedAtomicCommit but found $actualCommit."
    }

    return $resolvedAtomics
}

function Invoke-SelectedAtomic {
    param(
        [Parameter(Mandatory)][string]$AtomicsFolder,
        [switch]$Cleanup
    )

    $arguments = @{
        TestGuids = '40c44d16-bb49-4d14-aafa-f9ba7e6e6c5b'
        PathToAtomicsFolder = $AtomicsFolder
        TimeoutSeconds = 60
        Confirm = $false
        NoExecutionLog = $true
        InputArgs = @{
            webhook_url = $MockUrl
            staged_file = $StagedFilePath
        }
    }
    if ($Cleanup) {
        $arguments.Cleanup = $true
    }

    Invoke-AtomicTest 'T1567.004' @arguments
}

function New-AuditCanary {
    $auditRecord = [ordered]@{
        timestamp = (Get-Date).ToUniversalTime().ToString('o')
        application = 'Confluence'
        event = 'confluence_admin_created'
        username = 'benchmark_admin'
        role = 'administrator'
        source = 'safe_canary'
    }
    $auditRecord | ConvertTo-Json | Set-Content -LiteralPath $AuditPath -Encoding utf8
}

function Remove-AuditCanary {
    Remove-Item -LiteralPath $AuditPath -Force -ErrorAction SilentlyContinue
}

function Start-MockUploadReceiver {
    param([Parameter(Mandatory)][string]$LogPath)

    return Start-Job -ArgumentList $LogPath, $FakeDataMarker -ScriptBlock {
        param($OutputLog, $ExpectedMarker)

        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 18089)
        $listener.Start()
        Write-Output 'READY'
        try {
            $client = $listener.AcceptTcpClient()
            try {
                $stream = $client.GetStream()
                $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::UTF8, $false, 4096, $true)
                $requestLine = $reader.ReadLine()
                $contentLength = 0
                $userAgent = ''
                while ($true) {
                    $line = $reader.ReadLine()
                    if ([string]::IsNullOrEmpty($line)) {
                        break
                    }
                    if ($line.StartsWith('Content-Length:', [System.StringComparison]::OrdinalIgnoreCase)) {
                        $contentLength = [int]$line.Substring(15).Trim()
                    }
                    if ($line.StartsWith('User-Agent:', [System.StringComparison]::OrdinalIgnoreCase)) {
                        $userAgent = $line.Substring(11).Trim()
                    }
                }

                $bodyBuilder = [System.Text.StringBuilder]::new()
                $remaining = $contentLength
                $buffer = [char[]]::new(4096)
                while ($remaining -gt 0) {
                    $toRead = [Math]::Min($remaining, $buffer.Length)
                    $readCount = $reader.Read($buffer, 0, $toRead)
                    if ($readCount -le 0) {
                        break
                    }
                    [void]$bodyBuilder.Append($buffer, 0, $readCount)
                    $remaining -= $readCount
                }
                $body = $bodyBuilder.ToString()
                $requestParts = @($requestLine -split ' ')
                $record = [ordered]@{
                    timestamp = (Get-Date).ToUniversalTime().ToString('o')
                    method = if ($requestParts.Count -gt 0) { $requestParts[0] } else { '' }
                    path = if ($requestParts.Count -gt 1) { $requestParts[1] } else { '' }
                    user_agent = $userAgent
                    content_length = $contentLength
                    marker_present = $body.Contains($ExpectedMarker)
                }
                $record | ConvertTo-Json -Compress | Set-Content -LiteralPath $OutputLog -Encoding utf8

                $responseBody = [System.Text.Encoding]::UTF8.GetBytes('OK')
                $responseHeader = [System.Text.Encoding]::ASCII.GetBytes("HTTP/1.1 200 OK`r`nContent-Length: 2`r`nConnection: close`r`n`r`n")
                $stream.Write($responseHeader, 0, $responseHeader.Length)
                $stream.Write($responseBody, 0, $responseBody.Length)
                $stream.Flush()
            }
            finally {
                $client.Dispose()
            }
        }
        finally {
            $listener.Stop()
        }
    }
}

function Wait-MockReceiverReady {
    param([Parameter(Mandatory)]$Job)

    $deadline = (Get-Date).AddSeconds(10)
    while ((Get-Date) -lt $deadline) {
        $jobOutput = @(Receive-Job -Job $Job -Keep -ErrorAction SilentlyContinue)
        if ($jobOutput -contains 'READY') {
            return
        }
        if ($Job.State -in @('Failed', 'Stopped', 'Completed')) {
            throw "Mock receiver stopped before becoming ready (state: $($Job.State))."
        }
        Start-Sleep -Milliseconds 100
    }
    throw 'Mock receiver did not become ready within 10 seconds.'
}

function Assert-ExactCleanupRoot {
    $expected = [System.IO.Path]::GetFullPath($ScenarioRoot).TrimEnd('/')
    if (Test-Path -LiteralPath $ScenarioRoot) {
        $item = Get-Item -LiteralPath $ScenarioRoot -Force
        if ($item.LinkType) {
            throw "Refusing to recursively clean a symbolic link: $ScenarioRoot"
        }
        $actual = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $ScenarioRoot).Path).TrimEnd('/')
        if ($actual -ne $expected) {
            throw "Refusing cleanup outside the exact scenario root: $actual"
        }
    }
}

function Invoke-ScenarioCleanup {
    param([Parameter(Mandatory)][string]$AtomicsFolder)

    Assert-ExactCleanupRoot
    try {
        Invoke-SelectedAtomic -AtomicsFolder $AtomicsFolder -Cleanup
    }
    catch {
        Write-Warning "Atomic staged-file cleanup reported an error; exact scenario cleanup will continue: $($_.Exception.Message)"
    }
    Remove-AuditCanary
    if (Test-Path -LiteralPath $ScenarioRoot) {
        Remove-Item -LiteralPath $ScenarioRoot -Recurse -Force
    }
    Write-Output 'Cleanup complete: only the exact scenario directory was targeted.'
}

if ($Mode -eq 'Plan') {
    Show-Plan
    exit 0
}

if (($Mode -eq 'Execute') -and (-not $ConfirmExecution)) {
    throw 'Execute mode requires the explicit -ConfirmExecution switch.'
}

$validatedAtomicsFolder = Resolve-ValidatedAtomicsFolder -RequireCurl:($Mode -eq 'Execute')

if ($Mode -eq 'Cleanup') {
    Invoke-ScenarioCleanup -AtomicsFolder $validatedAtomicsFolder
    exit 0
}

if (Test-Path -LiteralPath $ScenarioRoot) {
    throw "Existing scenario directory found at $ScenarioRoot. Run Cleanup before another execution."
}
New-Item -ItemType Directory -Path $ScenarioRoot -Force | Out-Null
New-AuditCanary

$mockReceiverJob = $null
try {
    $mockReceiverJob = Start-MockUploadReceiver -LogPath $MockLogPath
    Wait-MockReceiverReady -Job $mockReceiverJob
    Invoke-SelectedAtomic -AtomicsFolder $validatedAtomicsFolder
    if (-not (Wait-Job -Job $mockReceiverJob -Timeout 20)) {
        throw 'Mock receiver did not complete the expected upload within 20 seconds.'
    }
    Receive-Job -Job $mockReceiverJob -ErrorAction Stop | Out-Null
}
finally {
    if ($null -ne $mockReceiverJob) {
        Stop-Job -Job $mockReceiverJob -ErrorAction SilentlyContinue
        Remove-Job -Job $mockReceiverJob -Force -ErrorAction SilentlyContinue
    }
}

Write-Output 'Execution complete. Evidence was preserved; run verify.ps1 separately, then use explicit Cleanup after the investigation.'
