[CmdletBinding()]
param(
    [string]$OutputPath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScenarioId = 'cisa-aa23-289a-ubuntu'
$ScenarioRoot = '/tmp/endpointir-bench/cisa-aa23-289a-ubuntu'
$AuditPath = '/tmp/endpointir-bench/cisa-aa23-289a-ubuntu/confluence-audit.json'
$StagedFilePath = '/tmp/endpointir-bench/cisa-aa23-289a-ubuntu/staged-loot.txt'
$MockLogPath = '/tmp/endpointir-bench/cisa-aa23-289a-ubuntu/mock-exfil.json'
$FakeDataMarker = 'secrets, api keys, passwords - T1567.004 atomic test'
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

$auditRecord = $null
try {
    if (Test-Path -LiteralPath $AuditPath -PathType Leaf) {
        $auditRecord = Get-Content -LiteralPath $AuditPath -Raw | ConvertFrom-Json
    }
}
catch {
    $auditRecord = $null
}
$auditPassed = ($null -ne $auditRecord) -and
    ($auditRecord.application -ceq 'Confluence') -and
    ($auditRecord.event -ceq 'confluence_admin_created') -and
    ($auditRecord.username -ceq 'benchmark_admin') -and
    ($auditRecord.role -ceq 'administrator') -and
    ($auditRecord.source -ceq 'safe_canary')
Add-Check -Id 'F1' -Required $true -Passed $auditPassed -Observed $(
    if ($null -ne $auditRecord) {
        "event=$($auditRecord.event); username=$($auditRecord.username); source=$($auditRecord.source)"
    }
    else {
        "missing_or_invalid=$AuditPath"
    }
)

$stagedExists = Test-Path -LiteralPath $StagedFilePath -PathType Leaf
$stagedContent = if ($stagedExists) { (Get-Content -LiteralPath $StagedFilePath -Raw).Trim() } else { '' }
$stagedPassed = $stagedExists -and ($stagedContent -ceq $FakeDataMarker)
Add-Check -Id 'F2' -Required $true -Passed $stagedPassed -Observed $(
    if ($stagedExists) { "file=$StagedFilePath; exact_fake_marker=$stagedPassed" } else { "missing=$StagedFilePath" }
)

$mockRecord = $null
try {
    if (Test-Path -LiteralPath $MockLogPath -PathType Leaf) {
        $mockRecord = Get-Content -LiteralPath $MockLogPath -Raw | ConvertFrom-Json
    }
}
catch {
    $mockRecord = $null
}
$mockPassed = ($null -ne $mockRecord) -and
    ($mockRecord.method -ceq 'POST') -and
    ($mockRecord.path -ceq '/upload') -and
    ($mockRecord.content_length -gt 0) -and
    ($mockRecord.marker_present -eq $true)
Add-Check -Id 'F3' -Required $true -Passed $mockPassed -Observed $(
    if ($null -ne $mockRecord) {
        "method=$($mockRecord.method); path=$($mockRecord.path); content_length=$($mockRecord.content_length); marker_present=$($mockRecord.marker_present)"
    }
    else {
        "missing_or_invalid=$MockLogPath"
    }
)

$temporalPassed = $false
$temporalObserved = 'Required timestamp evidence is missing or malformed.'
if (($null -ne $auditRecord) -and $stagedExists -and ($null -ne $mockRecord)) {
    try {
        $auditTime = [datetimeoffset]::Parse(
            [string]$auditRecord.timestamp,
            [System.Globalization.CultureInfo]::InvariantCulture,
            [System.Globalization.DateTimeStyles]::RoundtripKind
        ).UtcDateTime
        $stagedTime = (Get-Item -LiteralPath $StagedFilePath).LastWriteTimeUtc
        $uploadTime = [datetimeoffset]::Parse(
            [string]$mockRecord.timestamp,
            [System.Globalization.CultureInfo]::InvariantCulture,
            [System.Globalization.DateTimeStyles]::RoundtripKind
        ).UtcDateTime
        $temporalPassed = ($auditTime -le $stagedTime) -and ($stagedTime -le $uploadTime)
        $temporalObserved = "audit_utc=$($auditTime.ToString('o')); staged_utc=$($stagedTime.ToString('o')); upload_utc=$($uploadTime.ToString('o'))"
    }
    catch {
        $temporalPassed = $false
    }
}
Add-Check -Id 'F4' -Required $true -Passed $temporalPassed -Observed $temporalObserved

$requiredFailures = @($Checks | Where-Object { $_.required -and (-not $_.passed) })
$result = [pscustomobject]@{
    scenario_id = $ScenarioId
    verified_at = (Get-Date).ToUniversalTime().ToString('o')
    passed = ($requiredFailures.Count -eq 0)
    checks = $Checks
}
$json = $result | ConvertTo-Json -Depth 6

if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
    $scenarioFullPath = [System.IO.Path]::GetFullPath($ScenarioRoot).TrimEnd([char[]]@('/', '\'))
    $outputFullPath = [System.IO.Path]::GetFullPath($OutputPath)
    $separator = [System.IO.Path]::DirectorySeparatorChar
    if (($outputFullPath -eq $scenarioFullPath) -or $outputFullPath.StartsWith($scenarioFullPath + $separator, [System.StringComparison]::Ordinal)) {
        throw 'OutputPath must be outside the investigated scenario root.'
    }
    $outputParent = Split-Path -Parent $outputFullPath
    if ($outputParent -and (-not (Test-Path -LiteralPath $outputParent))) {
        New-Item -ItemType Directory -Path $outputParent -Force | Out-Null
    }
    Set-Content -LiteralPath $outputFullPath -Value $json -Encoding utf8
}

Write-Output $json
if (-not $result.passed) {
    exit 1
}
