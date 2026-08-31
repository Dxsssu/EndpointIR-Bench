[CmdletBinding()]
param(
    [ValidateSet('Plan', 'Execute', 'Cleanup')]
    [string]$Mode = 'Plan',

    [string]$PathToAtomicsFolder = '',

    [switch]$ConfirmExecution
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScenarioId = 'unit42-2021-10-18-o-network-reconnaissance'
$ExpectedAtomicCommit = '6132b92779873cb0d05bef07ba0a480d47eb1cc8'
$ScenarioRoot = 'C:\ProgramData\EndpointIRBench\unit42-2021-10-18-o-network-reconnaissance'
$CanaryPath = Join-Path $ScenarioRoot 'tru.dll'
$MarkerPath = Join-Path $ScenarioRoot 'beacon-started.txt'
$C2LogPath = Join-Path $ScenarioRoot 'mock-c2.log'
$RunKeyPath = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
$RunValueName = 'EndpointIRBench_Unit42_BazarRecon'
$CanaryMessage = 'ENDPOINTIR_BENCH_UNIT42_BAZAR_CANARY'
$PersistenceCommand = 'cmd.exe /c type "{0}" > "{1}"' -f $CanaryPath, $MarkerPath

$Steps = @(
    [pscustomobject]@{ Order = 1; Technique = 'T1059.003'; Implementation = 'Atomic'; Name = 'Create harmless DLL-named canary' },
    [pscustomobject]@{ Order = 2; Technique = 'T1547.001'; Implementation = 'Custom canary'; Name = 'Create scenario-owned HKCU Run value' },
    [pscustomobject]@{ Order = 3; Technique = 'T1082'; Implementation = 'Atomic'; Name = 'Collect basic system information' },
    [pscustomobject]@{ Order = 4; Technique = 'T1016'; Implementation = 'Atomic'; Name = 'Collect local network configuration' },
    [pscustomobject]@{ Order = 5; Technique = 'T1018'; Implementation = 'Atomic'; Name = 'Inspect local ARP cache' },
    [pscustomobject]@{ Order = 6; Technique = 'T1071.001'; Implementation = 'Atomic + loopback Mock'; Name = 'Send four loopback HTTP requests' }
)

function Show-Plan {
    Write-Output "Scenario: $ScenarioId"
    Write-Output 'Target: one disposable, recoverable Windows VM'
    Write-Output 'Network boundary: loopback only (http://127.0.0.1:18088/beacon)'
    Write-Output 'Elevation: not required'
    Write-Output "Pinned Atomic commit: $ExpectedAtomicCommit"
    Write-Output ''
    Write-Output ($Steps | Format-Table Order, Technique, Implementation, Name -AutoSize | Out-String).TrimEnd()
    Write-Output ''
    Write-Output "Expected mutations: $CanaryPath, $C2LogPath, and HKCU Run value $RunValueName."
    Write-Output "Cleanup scope: only $ScenarioRoot and the exact HKCU Run value above."
    Write-Output 'Plan mode performed no host checks and made no changes.'
}

function Resolve-ValidatedAtomicsFolder {
    if ($env:OS -ne 'Windows_NT') {
        throw 'This scenario must run inside a disposable Windows VM.'
    }
    if (-not (Get-Command Invoke-AtomicTest -ErrorAction SilentlyContinue)) {
        throw 'Invoke-AtomicTest is unavailable. Install or import Invoke-AtomicRedTeam first.'
    }
    if ([string]::IsNullOrWhiteSpace($PathToAtomicsFolder)) {
        throw 'Pass -PathToAtomicsFolder with the pinned atomic-red-team\atomics directory.'
    }
    if (-not (Test-Path -LiteralPath $PathToAtomicsFolder -PathType Container)) {
        throw "Atomic folder not found: $PathToAtomicsFolder"
    }

    $resolvedAtomics = (Resolve-Path -LiteralPath $PathToAtomicsFolder).Path
    if ((Split-Path -Leaf $resolvedAtomics) -ne 'atomics') {
        throw "PathToAtomicsFolder must identify the checkout's atomics directory: $resolvedAtomics"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $resolvedAtomics 'T1059.003\T1059.003.yaml'))) {
        throw "The supplied atomics directory does not contain the required definitions: $resolvedAtomics"
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
    $actualCommit = [string]$actualCommitOutput[-1]
    $actualCommit = $actualCommit.Trim()
    if ($actualCommit -ne $ExpectedAtomicCommit) {
        throw "Atomic checkout mismatch. Expected $ExpectedAtomicCommit but found $actualCommit."
    }

    return $resolvedAtomics
}

function Invoke-SelectedAtomic {
    param(
        [Parameter(Mandatory)]
        [string]$Technique,

        [Parameter(Mandatory)]
        [string]$Guid,

        [Parameter(Mandatory)]
        [string]$AtomicsFolder,

        [hashtable]$InputArgs = @{},

        [switch]$Cleanup
    )

    $arguments = @{
        TestGuids           = $Guid
        PathToAtomicsFolder = $AtomicsFolder
        TimeoutSeconds      = 60
        Confirm             = $false
        NoExecutionLog      = $true
    }
    if ($InputArgs.Count -gt 0) {
        $arguments.InputArgs = $InputArgs
    }
    if ($Cleanup) {
        $arguments.Cleanup = $true
    }

    Invoke-AtomicTest $Technique @arguments
}

function Test-ExistingScenarioState {
    if (Test-Path -LiteralPath $ScenarioRoot) {
        throw "Existing scenario directory found at $ScenarioRoot. Run Cleanup before another execution."
    }
    try {
        $existing = Get-ItemPropertyValue -LiteralPath $RunKeyPath -Name $RunValueName -ErrorAction Stop
        throw "Existing scenario registry value found: $RunKeyPath\$RunValueName ($existing). Run Cleanup first."
    }
    catch [System.Management.Automation.ItemNotFoundException] {
        return
    }
    catch [System.Management.Automation.PSArgumentException] {
        return
    }
}

function New-PersistenceCanary {
    Set-ItemProperty -LiteralPath $RunKeyPath -Name $RunValueName -Value $PersistenceCommand -Type String
}

function Remove-PersistenceCanary {
    Remove-ItemProperty -LiteralPath $RunKeyPath -Name $RunValueName -Force -ErrorAction SilentlyContinue
}

function Start-MockC2 {
    param([Parameter(Mandatory)][string]$LogPath)

    return Start-Job -ArgumentList $LogPath -ScriptBlock {
        param($OutputLog)

        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 18088)
        $listener.Start()
        Write-Output 'READY'
        try {
            for ($requestNumber = 1; $requestNumber -le 4; $requestNumber++) {
                $client = $listener.AcceptTcpClient()
                try {
                    $stream = $client.GetStream()
                    $reader = [System.IO.StreamReader]::new($stream)
                    $requestLine = $reader.ReadLine()
                    $userAgent = ''
                    while ($true) {
                        $line = $reader.ReadLine()
                        if ([string]::IsNullOrEmpty($line)) {
                            break
                        }
                        if ($line.StartsWith('User-Agent:', [System.StringComparison]::OrdinalIgnoreCase)) {
                            $userAgent = $line.Substring(11).Trim()
                        }
                    }

                    $record = "{0}`t{1}`t{2}" -f (Get-Date).ToUniversalTime().ToString('o'), $requestLine, $userAgent
                    Add-Content -LiteralPath $OutputLog -Value $record -Encoding UTF8
                    $body = [System.Text.Encoding]::UTF8.GetBytes('OK')
                    $header = [System.Text.Encoding]::ASCII.GetBytes("HTTP/1.1 200 OK`r`nContent-Length: 2`r`nConnection: close`r`n`r`n")
                    $stream.Write($header, 0, $header.Length)
                    $stream.Write($body, 0, $body.Length)
                    $stream.Flush()
                }
                finally {
                    $client.Dispose()
                }
            }
        }
        finally {
            $listener.Stop()
        }
    }
}

function Wait-MockC2Ready {
    param([Parameter(Mandatory)]$Job)

    $deadline = (Get-Date).AddSeconds(10)
    while ((Get-Date) -lt $deadline) {
        $jobOutput = @(Receive-Job -Job $Job -Keep -ErrorAction SilentlyContinue)
        if ($jobOutput -contains 'READY') {
            return
        }
        if ($Job.State -in @('Failed', 'Stopped', 'Completed')) {
            throw "Mock C2 stopped before becoming ready (state: $($Job.State))."
        }
        Start-Sleep -Milliseconds 100
    }
    throw 'Mock C2 did not become ready within 10 seconds.'
}

function Assert-ExactCleanupRoot {
    $expected = [System.IO.Path]::GetFullPath($ScenarioRoot).TrimEnd('\')
    if (Test-Path -LiteralPath $ScenarioRoot) {
        $actual = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $ScenarioRoot).Path).TrimEnd('\')
        if ($actual -ne $expected) {
            throw "Refusing cleanup outside the exact scenario root: $actual"
        }
    }
}

function Invoke-ScenarioCleanup {
    param([Parameter(Mandatory)][string]$AtomicsFolder)

    Assert-ExactCleanupRoot
    try {
        Invoke-SelectedAtomic -Technique 'T1059.003' -Guid '127b4afe-2346-4192-815c-69042bec570e' -AtomicsFolder $AtomicsFolder -InputArgs @{
            file_contents_path = $CanaryPath
            message = $CanaryMessage
        } -Cleanup
    }
    catch {
        Write-Warning "Atomic canary cleanup reported an error; exact scenario cleanup will continue: $($_.Exception.Message)"
    }

    Remove-PersistenceCanary
    if (Test-Path -LiteralPath $ScenarioRoot) {
        Remove-Item -LiteralPath $ScenarioRoot -Recurse -Force
    }
    Write-Output 'Cleanup complete: only the exact scenario directory and registry value were targeted.'
}

if ($Mode -eq 'Plan') {
    Show-Plan
    exit 0
}

if (($Mode -eq 'Execute') -and (-not $ConfirmExecution)) {
    throw 'Execute mode requires the explicit -ConfirmExecution switch.'
}

$validatedAtomicsFolder = Resolve-ValidatedAtomicsFolder

if ($Mode -eq 'Cleanup') {
    Invoke-ScenarioCleanup -AtomicsFolder $validatedAtomicsFolder
    exit 0
}

Test-ExistingScenarioState
New-Item -ItemType Directory -Path $ScenarioRoot | Out-Null

$mockC2Job = $null
try {
    Invoke-SelectedAtomic -Technique 'T1059.003' -Guid '127b4afe-2346-4192-815c-69042bec570e' -AtomicsFolder $validatedAtomicsFolder -InputArgs @{
        file_contents_path = $CanaryPath
        message = $CanaryMessage
    }
    New-PersistenceCanary
    Invoke-SelectedAtomic -Technique 'T1082' -Guid '66703791-c902-4560-8770-42b8a91f7667' -AtomicsFolder $validatedAtomicsFolder
    Invoke-SelectedAtomic -Technique 'T1016' -Guid '970ab6a1-0157-4f3f-9a73-ec4166754b23' -AtomicsFolder $validatedAtomicsFolder
    Invoke-SelectedAtomic -Technique 'T1018' -Guid '2d5a61f5-0447-4be4-944a-1f8530ed6574' -AtomicsFolder $validatedAtomicsFolder

    $mockC2Job = Start-MockC2 -LogPath $C2LogPath
    Wait-MockC2Ready -Job $mockC2Job
    Invoke-SelectedAtomic -Technique 'T1071.001' -Guid '81c13829-f6c9-45b8-85a6-053366d55297' -AtomicsFolder $validatedAtomicsFolder -InputArgs @{
        domain = 'http://127.0.0.1:18088/beacon'
    }
    if (-not (Wait-Job -Job $mockC2Job -Timeout 20)) {
        throw 'Mock C2 did not receive all four expected requests within 20 seconds.'
    }
    Receive-Job -Job $mockC2Job -ErrorAction Stop | Out-Null
}
finally {
    if ($null -ne $mockC2Job) {
        Stop-Job -Job $mockC2Job -ErrorAction SilentlyContinue
        Remove-Job -Job $mockC2Job -Force -ErrorAction SilentlyContinue
    }
}

Write-Output 'Execution complete. Evidence was preserved; run verify.ps1 separately, then use explicit Cleanup after the investigation.'
