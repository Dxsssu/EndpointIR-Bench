[CmdletBinding()]
param(
    [string]$OutputPath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScenarioId = 'unit42-2021-10-18-o-network-reconnaissance'
$ScenarioRoot = 'C:\ProgramData\EndpointIRBench\unit42-2021-10-18-o-network-reconnaissance'
$CanaryPath = Join-Path $ScenarioRoot 'tru.dll'
$C2LogPath = Join-Path $ScenarioRoot 'mock-c2.log'
$RunKeyPath = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
$RunValueName = 'EndpointIRBench_Unit42_BazarRecon'
$CanaryMessage = 'ENDPOINTIR_BENCH_UNIT42_BAZAR_CANARY'
$MarkerPath = Join-Path $ScenarioRoot 'beacon-started.txt'
$ExpectedPersistenceCommand = 'cmd.exe /c type "{0}" > "{1}"' -f $CanaryPath, $MarkerPath
$Checks = [System.Collections.Generic.List[object]]::new()

function Add-Check {
    param(
        [Parameter(Mandatory)][string]$Id,
        [Parameter(Mandatory)][bool]$Required,
        [Parameter(Mandatory)][bool]$Passed,
        [Parameter(Mandatory)][string]$Observed
    )

    $Checks.Add([pscustomobject]@{
        id = $Id
        required = $Required
        passed = $Passed
        observed = $Observed
    })
}

$canaryExists = Test-Path -LiteralPath $CanaryPath -PathType Leaf
$canaryContent = if ($canaryExists) { Get-Content -LiteralPath $CanaryPath -Raw } else { '' }
$canaryPassed = $canaryExists -and $canaryContent.Contains($CanaryMessage)
Add-Check -Id 'F1' -Required $true -Passed $canaryPassed -Observed $(
    if ($canaryExists) { "file=$CanaryPath; marker_present=$canaryPassed" } else { "missing=$CanaryPath" }
)

$runValue = ''
try {
    $runValue = [string](Get-ItemPropertyValue -LiteralPath $RunKeyPath -Name $RunValueName -ErrorAction Stop)
}
catch {
    $runValue = ''
}
$persistencePassed = $runValue -ceq $ExpectedPersistenceCommand
Add-Check -Id 'F2' -Required $true -Passed $persistencePassed -Observed $(
    if ($runValue) { "value=$runValue" } else { "missing=$RunKeyPath\$RunValueName" }
)

$telemetryAvailable = $false
$matchedCommands = @()
try {
    $sysmonLog = Get-WinEvent -ListLog 'Microsoft-Windows-Sysmon/Operational' -ErrorAction Stop
    if ($sysmonLog.IsEnabled) {
        $telemetryAvailable = $true
        $startTime = if ($canaryExists) { (Get-Item -LiteralPath $CanaryPath).LastWriteTime.AddMinutes(-2) } else { (Get-Date).AddHours(-24) }
        $events = @(Get-WinEvent -FilterHashtable @{
            LogName = 'Microsoft-Windows-Sysmon/Operational'
            Id = 1
            StartTime = $startTime
        } -MaxEvents 500 -ErrorAction Stop)
        $expectedCommands = @('systeminfo.exe', 'reg.exe', 'ipconfig.exe', 'netsh.exe', 'arp.exe', 'nbtstat.exe')
        foreach ($command in $expectedCommands) {
            if ($events.Message -match [regex]::Escape($command)) {
                $matchedCommands += $command
            }
        }
    }
}
catch {
    $telemetryAvailable = $false
}
$telemetryPassed = $telemetryAvailable -and ($matchedCommands.Count -ge 5)
Add-Check -Id 'F3' -Required $false -Passed $telemetryPassed -Observed $(
    if ($telemetryAvailable) { "matched=$($matchedCommands -join ',')" } else { 'Sysmon Event ID 1 telemetry is unavailable; optional finding not scored.' }
)

$requestLines = if (Test-Path -LiteralPath $C2LogPath -PathType Leaf) { @(Get-Content -LiteralPath $C2LogPath) } else { @() }
$parsedRequests = @()
foreach ($line in $requestLines) {
    $parts = @($line -split "`t", 3)
    if ($parts.Count -eq 3) {
        $parsedRequests += [pscustomobject]@{
            timestamp = $parts[0]
            request = $parts[1]
            user_agent = $parts[2]
        }
    }
}
$expectedAgents = @(
    'HttpBrowser/1.0',
    'Wget/1.9+cvs-stable (Red Hat modified)',
    'Opera/8.81 (Windows NT 6.0; U; en)',
    '*<|>*'
)
$allAgentsPresent = $true
foreach ($agent in $expectedAgents) {
    if ($parsedRequests.user_agent -cnotcontains $agent) {
        $allAgentsPresent = $false
    }
}
$allPathsExpected = ($parsedRequests.Count -eq 4) -and -not ($parsedRequests.request | Where-Object { $_ -notmatch '^GET /beacon(?:\?| )' })
$mockLogPassed = ($parsedRequests.Count -eq 4) -and $allAgentsPresent -and $allPathsExpected
Add-Check -Id 'F4' -Required $true -Passed $mockLogPassed -Observed "records=$($parsedRequests.Count); expected_agents=$allAgentsPresent; expected_path=$allPathsExpected"

$temporalPassed = $false
$temporalObserved = 'Required timestamp evidence is missing or malformed.'
if ($canaryExists -and ($parsedRequests.Count -gt 0)) {
    $firstRequestTime = [datetime]::MinValue
    if ([datetime]::TryParse(
        $parsedRequests[0].timestamp,
        [System.Globalization.CultureInfo]::InvariantCulture,
        [System.Globalization.DateTimeStyles]::RoundtripKind,
        [ref]$firstRequestTime
    )) {
        $canaryTime = (Get-Item -LiteralPath $CanaryPath).LastWriteTimeUtc
        $firstRequestUtc = $firstRequestTime.ToUniversalTime()
        $temporalPassed = $canaryTime -le $firstRequestUtc
        $temporalObserved = "canary_utc=$($canaryTime.ToString('o')); first_http_utc=$($firstRequestUtc.ToString('o'))"
    }
}
Add-Check -Id 'F5' -Required $true -Passed $temporalPassed -Observed $temporalObserved

$requiredFailures = @($Checks | Where-Object { $_.required -and (-not $_.passed) })
$result = [pscustomobject]@{
    scenario_id = $ScenarioId
    verified_at = (Get-Date).ToUniversalTime().ToString('o')
    passed = ($requiredFailures.Count -eq 0)
    checks = $Checks
}
$json = $result | ConvertTo-Json -Depth 6

if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
    $scenarioFullPath = [System.IO.Path]::GetFullPath($ScenarioRoot).TrimEnd('\')
    $outputFullPath = [System.IO.Path]::GetFullPath($OutputPath)
    if (($outputFullPath -ieq $scenarioFullPath) -or $outputFullPath.StartsWith($scenarioFullPath + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'OutputPath must be outside the investigated scenario root.'
    }
    $outputParent = Split-Path -Parent $outputFullPath
    if ($outputParent -and (-not (Test-Path -LiteralPath $outputParent))) {
        New-Item -ItemType Directory -Path $outputParent -Force | Out-Null
    }
    Set-Content -LiteralPath $outputFullPath -Value $json -Encoding UTF8
}

Write-Output $json
if (-not $result.passed) {
    exit 1
}
