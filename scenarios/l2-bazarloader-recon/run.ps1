[CmdletBinding()]
param(
    [ValidateSet("Plan", "Execute", "Cleanup")]
    [string]$Mode = "Plan",

    [string]$PathToAtomicsFolder = "",

    [switch]$ConfirmExecution
)

$ErrorActionPreference = "Stop"
$ScenarioRoot = "C:\ProgramData\EndpointIRBench\bazarloader-recon"
$LurePath = Join-Path $ScenarioRoot "Documents new.xlsb"
$CanaryPath = Join-Path $ScenarioRoot "tru.dll"
$C2LogPath = Join-Path $ScenarioRoot "mock-c2.log"
$StatePath = Join-Path $ScenarioRoot "scenario-state.json"
$TranscriptPath = Join-Path $ScenarioRoot "execution-transcript.txt"
$VerificationPath = Join-Path $ScenarioRoot "verification.json"
$RunKey = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
$RunValueName = "Atomic Red Team"
$CanaryCommand = "cmd.exe /c type $CanaryPath > $ScenarioRoot\beacon-started.txt"

$Steps = @(
    [pscustomobject]@{ Order = 1; Technique = "T1059.003"; Guid = "127b4afe-2346-4192-815c-69042bec570e"; Name = "Canary payload creation" },
    [pscustomobject]@{ Order = 2; Technique = "T1547.001"; Guid = "e55be3fd-3521-4610-9d1a-e210e42dcf05"; Name = "Registry Run-key persistence" },
    [pscustomobject]@{ Order = 3; Technique = "T1082"; Guid = "66703791-c902-4560-8770-42b8a91f7667"; Name = "System information discovery" },
    [pscustomobject]@{ Order = 4; Technique = "T1016"; Guid = "970ab6a1-0157-4f3f-9a73-ec4166754b23"; Name = "Network configuration discovery" },
    [pscustomobject]@{ Order = 5; Technique = "T1018"; Guid = "2d5a61f5-0447-4be4-944a-1f8530ed6574"; Name = "Remote system discovery via ARP" },
    [pscustomobject]@{ Order = 6; Technique = "T1071.001"; Guid = "81c13829-f6c9-45b8-85a6-053366d55297"; Name = "Mock HTTP C2" }
)

function Show-Plan {
    Write-Host "Scenario: L2-BAZAR-RECON-001"
    Write-Host "Target: one disposable Windows VM"
    Write-Host "Network: loopback only (127.0.0.1:18088)"
    Write-Host ""
    $Steps | Format-Table Order, Technique, Guid, Name -AutoSize
    Write-Host ""
    Write-Host "Plan mode makes no changes. Execute mode requires -ConfirmExecution."
}

function Assert-WindowsEnvironment {
    if ($env:OS -ne "Windows_NT") {
        throw "This scenario must run inside a disposable Windows VM."
    }
    if (-not (Get-Command Invoke-AtomicTest -ErrorAction SilentlyContinue)) {
        throw "Invoke-AtomicTest is unavailable. Install/import Invoke-AtomicRedTeam first."
    }
    if (-not $PathToAtomicsFolder) {
        throw "Pass -PathToAtomicsFolder with the local atomic-red-team\\atomics directory."
    }
    if (-not (Test-Path $PathToAtomicsFolder)) {
        throw "Atomic folder not found: $PathToAtomicsFolder"
    }
}

function Invoke-SelectedAtomic {
    param(
        [string]$Technique,
        [string]$Guid,
        [hashtable]$InputArgs = @{},
        [switch]$Cleanup
    )
    $arguments = @{
        TestGuids          = $Guid
        PathToAtomicsFolder = $PathToAtomicsFolder
        TimeoutSeconds     = 60
        Confirm            = $false
    }
    if ($InputArgs.Count -gt 0) {
        $arguments.InputArgs = $InputArgs
    }
    if ($Cleanup) {
        $arguments.Cleanup = $true
    }
    Invoke-AtomicTest $Technique @arguments
}

function Start-MockC2 {
    param([string]$LogPath)
    return Start-Job -ArgumentList $LogPath -ScriptBlock {
        param($OutputLog)
        $listener = [System.Net.Sockets.TcpListener]::new(
            [System.Net.IPAddress]::Loopback,
            18088
        )
        $listener.Start()
        try {
            for ($requestNumber = 1; $requestNumber -le 4; $requestNumber++) {
                $client = $listener.AcceptTcpClient()
                try {
                    $stream = $client.GetStream()
                    $reader = [System.IO.StreamReader]::new($stream)
                    $requestLine = $reader.ReadLine()
                    $userAgent = ""
                    while ($true) {
                        $line = $reader.ReadLine()
                        if ([string]::IsNullOrEmpty($line)) { break }
                        if ($line.StartsWith("User-Agent:", [System.StringComparison]::OrdinalIgnoreCase)) {
                            $userAgent = $line.Substring(11).Trim()
                        }
                    }
                    $record = "{0}`t{1}`t{2}" -f (Get-Date).ToUniversalTime().ToString("o"), $requestLine, $userAgent
                    Add-Content -LiteralPath $OutputLog -Value $record -Encoding UTF8
                    $body = [System.Text.Encoding]::UTF8.GetBytes("OK")
                    $header = [System.Text.Encoding]::ASCII.GetBytes(
                        "HTTP/1.1 200 OK`r`nContent-Length: 2`r`nConnection: close`r`n`r`n"
                    )
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

function Invoke-Cleanup {
    Assert-WindowsEnvironment
    Invoke-SelectedAtomic -Technique "T1547.001" -Guid "e55be3fd-3521-4610-9d1a-e210e42dcf05" -Cleanup
    Invoke-SelectedAtomic -Technique "T1059.003" -Guid "127b4afe-2346-4192-815c-69042bec570e" -InputArgs @{
        file_contents_path = $CanaryPath
        message = "ENDPOINTIR_BENCH_BAZAR_CANARY"
    } -Cleanup

    @($LurePath, $C2LogPath, $StatePath, $TranscriptPath, $VerificationPath,
      (Join-Path $ScenarioRoot "beacon-started.txt")) | ForEach-Object {
        if (Test-Path -LiteralPath $_) {
            Remove-Item -LiteralPath $_ -Force
        }
    }
    if ((Test-Path $ScenarioRoot) -and -not (Get-ChildItem -LiteralPath $ScenarioRoot -Force)) {
        Remove-Item -LiteralPath $ScenarioRoot
    }
    Write-Host "Scenario-owned registry value and files were cleaned up."
}

if ($Mode -eq "Plan") {
    Show-Plan
    exit 0
}

if ($Mode -eq "Cleanup") {
    Invoke-Cleanup
    exit 0
}

if (-not $ConfirmExecution) {
    throw "Execute mode requires the explicit -ConfirmExecution switch."
}
Assert-WindowsEnvironment
if (Test-Path $StatePath) {
    throw "Existing scenario state found at $StatePath. Run Cleanup before another execution."
}

New-Item -ItemType Directory -Path $ScenarioRoot -Force | Out-Null
Set-Content -LiteralPath $LurePath -Value "Harmless benchmark lure; this is not an Office document." -Encoding UTF8
@{
    scenario_id = "L2-BAZAR-RECON-001"
    started_at = (Get-Date).ToUniversalTime().ToString("o")
    host = $env:COMPUTERNAME
    user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    atomic_root = $PathToAtomicsFolder
} | ConvertTo-Json | Set-Content -LiteralPath $StatePath -Encoding UTF8

Start-Transcript -LiteralPath $TranscriptPath | Out-Null
try {
    Invoke-SelectedAtomic -Technique "T1059.003" -Guid "127b4afe-2346-4192-815c-69042bec570e" -InputArgs @{
        file_contents_path = $CanaryPath
        message = "ENDPOINTIR_BENCH_BAZAR_CANARY"
    }
    Invoke-SelectedAtomic -Technique "T1547.001" -Guid "e55be3fd-3521-4610-9d1a-e210e42dcf05" -InputArgs @{
        command_to_execute = $CanaryCommand
    }
    Invoke-SelectedAtomic -Technique "T1082" -Guid "66703791-c902-4560-8770-42b8a91f7667"
    Invoke-SelectedAtomic -Technique "T1016" -Guid "970ab6a1-0157-4f3f-9a73-ec4166754b23"
    Invoke-SelectedAtomic -Technique "T1018" -Guid "2d5a61f5-0447-4be4-944a-1f8530ed6574"

    $mockC2 = Start-MockC2 -LogPath $C2LogPath
    try {
        Start-Sleep -Milliseconds 750
        Invoke-SelectedAtomic -Technique "T1071.001" -Guid "81c13829-f6c9-45b8-85a6-053366d55297" -InputArgs @{
            domain = "http://127.0.0.1:18088/beacon"
        }
        if (-not (Wait-Job -Job $mockC2 -Timeout 20)) {
            throw "Mock C2 did not receive all four expected requests."
        }
        Receive-Job -Job $mockC2 | Out-Null
    }
    finally {
        Stop-Job -Job $mockC2 -ErrorAction SilentlyContinue
        Remove-Job -Job $mockC2 -Force -ErrorAction SilentlyContinue
    }
}
finally {
    Stop-Transcript | Out-Null
}

& (Join-Path $PSScriptRoot "verify.ps1") -ScenarioRoot $ScenarioRoot
Write-Host "Execution complete. Preserve the VM for investigation, then run Cleanup explicitly."
