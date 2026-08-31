[CmdletBinding()]
param(
    [string]$ScenarioRoot = "C:\ProgramData\EndpointIRBench\bazarloader-recon"
)

$ErrorActionPreference = "Stop"
$CanaryPath = Join-Path $ScenarioRoot "tru.dll"
$LurePath = Join-Path $ScenarioRoot "Documents new.xlsb"
$C2LogPath = Join-Path $ScenarioRoot "mock-c2.log"
$TranscriptPath = Join-Path $ScenarioRoot "execution-transcript.txt"
$VerificationPath = Join-Path $ScenarioRoot "verification.json"
$RunKey = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
$RunValueName = "Atomic Red Team"

$checks = @()
function Add-Check {
    param([string]$Id, [string]$Description, [bool]$Passed, [string]$Observed)
    $script:checks += [pscustomobject]@{
        id = $Id
        description = $Description
        passed = $Passed
        observed = $Observed
    }
}

$canaryExists = Test-Path -LiteralPath $CanaryPath
$canaryContent = if ($canaryExists) { Get-Content -LiteralPath $CanaryPath -Raw } else { "" }
Add-Check "F1" "Canary DLL-named file exists" ($canaryExists -and $canaryContent.Contains("ENDPOINTIR_BENCH_BAZAR_CANARY")) $CanaryPath

$lureExists = Test-Path -LiteralPath $LurePath
Add-Check "F1-context" "Harmless XLSB-named lure exists" $lureExists $LurePath

$runValue = ""
try {
    $runValue = (Get-ItemProperty -LiteralPath $RunKey -Name $RunValueName -ErrorAction Stop).$RunValueName
}
catch {
    $runValue = ""
}
Add-Check "F2" "HKCU Run-key persistence points to the scenario" ($runValue -like "*$ScenarioRoot*") $runValue

$requests = if (Test-Path -LiteralPath $C2LogPath) { @(Get-Content -LiteralPath $C2LogPath) } else { @() }
$expectedAgents = @("HttpBrowser/1.0", "Wget/1.9", "Opera/8.81", "*<|>*")
$agentMatches = 0
foreach ($agent in $expectedAgents) {
    if ($requests -match [regex]::Escape($agent)) { $agentMatches++ }
}
Add-Check "F4" "Mock C2 received four requests with four User-Agent families" (($requests.Count -eq 4) -and ($agentMatches -eq 4)) "requests=$($requests.Count); user_agent_families=$agentMatches"

$transcriptExists = Test-Path -LiteralPath $TranscriptPath
Add-Check "F3" "Atomic execution transcript exists for volatile discovery activity" $transcriptExists $TranscriptPath

$result = [pscustomobject]@{
    scenario_id = "L2-BAZAR-RECON-001"
    verified_at = (Get-Date).ToUniversalTime().ToString("o")
    passed = -not ($checks | Where-Object { -not $_.passed })
    checks = $checks
}
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $VerificationPath -Encoding UTF8
$result | ConvertTo-Json -Depth 5
if (-not $result.passed) {
    exit 1
}
