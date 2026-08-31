# Runnable scenario package schema

Read this reference before generating a scenario. Markdown narrative is secondary; the required deliverable is code that runs without manual editing.

## Directory and naming

Write one package per report under `scenarios/<scenario-id>/`. Use a stable lowercase ASCII slug. Existing packages are immutable unless regeneration is explicitly requested.

Every package must contain these required files:

```text
scenario.json          Machine-readable provenance, safety, steps, and Ground Truth
run.ps1                Plan, Execute, and Cleanup orchestration
verify.ps1             Independent endpoint-evidence verification
validate_scenario.py   Static package and local Atomic validation
README.md              Short operator prerequisites and commands
```

Additional payloads are allowed only when they are harmless, hash-recorded, generated locally, and stored under `assets/` in the scenario package.

The package is a control-plane artifact. `run.ps1` and `verify.ps1` must each run without reading `scenario.json` or other package metadata. When the runner is copied into a target VM instead of invoked remotely, remove the copied package files before taking the investigation snapshot; this removal must not touch generated endpoint evidence.

## `scenario.json`

Use UTF-8 JSON so package metadata can be read without a YAML dependency. Required shape:

```json
{
  "schema_version": 1,
  "scenario_id": "l2-example-001",
  "title": "Example investigation scenario",
  "level": "L2",
  "platform": "windows",
  "host_count": 1,
  "source": {
    "report_id": "manifest-id",
    "publisher": "publisher",
    "published": "YYYY-MM-DD",
    "local_file": "public_ir_reports/source/report.md",
    "source_url": "https://example.invalid/report",
    "confidence_notes": ""
  },
  "atomic_repo_commit": "full git commit",
  "initial_alert": {
    "severity": "medium",
    "text": "Sparse alert that does not reveal the answer"
  },
  "safety": {
    "external_network": false,
    "requires_elevation": false,
    "allows_dependencies": false,
    "scenario_root": "C:\\ProgramData\\EndpointIRBench\\l2-example-001",
    "cleanup_required": true
  },
  "steps": [
    {
      "order": 1,
      "name": "canary creation",
      "source_confidence": "observed",
      "implementation": "atomic",
      "technique": "T1059.003",
      "atomic_guid": "00000000-0000-0000-0000-000000000000",
      "atomic_name": "Exact local Atomic test name",
      "input_args": {},
      "mutates_state": true
    }
  ],
  "expected_findings": [
    {
      "id": "F1",
      "required": true,
      "type": "file",
      "expected": "exact expected value",
      "evidence_surface": "filesystem",
      "temporal_relation": "created before step 2",
      "verifier": "verify.ps1 check name"
    }
  ],
  "omitted_behaviors": []
}
```

Use `implementation: "custom_canary"` only for code implemented directly in `run.ps1`; include a precise cleanup action. Do not include `not_simulated` items in executable `steps`; record them under `omitted_behaviors`.

## `run.ps1`

Required interface:

```powershell
[CmdletBinding()]
param(
    [ValidateSet('Plan', 'Execute', 'Cleanup')]
    [string]$Mode = 'Plan',
    [string]$PathToAtomicsFolder = '',
    [switch]$ConfirmExecution
)
```

Required behavior:

- `Plan` prints scenario ID, safety boundary, ordered steps, expected mutations, and cleanup scope, then exits without checking or changing the host.
- `Execute` checks Windows, `Invoke-AtomicTest`, the atomics directory, the pinned repository commit embedded in the script, absence of existing scenario state, and explicit confirmation before the first mutation.
- Every Atomic call supplies `-TestGuids`, `-PathToAtomicsFolder`, a timeout, `-Confirm:$false`, and all documented input overrides.
- Custom canaries are functions with paired cleanup functions; do not download code or embed report IOCs.
- Use `try/finally` for temporary listeners and jobs. A failure returns nonzero and does not automatically erase investigation evidence.
- `Cleanup` invokes matching Atomic cleanup with the same input overrides, removes exact custom artifacts, tolerates already-missing artifacts, and refuses paths outside the scenario root.
- Runtime bookkeeping may contain only non-answer-bearing execution state and should be removable before the investigation snapshot.

## `verify.ps1`

Verification must read evidence independently. It may inspect files, hashes, registry values, scheduled tasks, services, Windows event logs, DNS cache, or loopback Mock-service records. It must not use Atomic stdout, execution transcripts, or the runner's exit code as proof.

Output one JSON object to stdout:

```json
{
  "scenario_id": "l2-example-001",
  "verified_at": "ISO-8601",
  "passed": true,
  "checks": [
    {"id": "F1", "passed": true, "observed": "..."}
  ]
}
```

Accept an optional `-OutputPath`; reject output paths under the investigated scenario root. Missing optional evidence must not fail the package. Required evidence must have a stable observation surface at investigation time.

## `validate_scenario.py`

Use only Python's standard library for `scenario.json` and package checks. If PyYAML is unavailable, fail with an actionable message before Atomic YAML validation; do not silently skip it. Validate:

- required files and JSON fields;
- contiguous step ordering and unique finding IDs;
- source file containment under `public_ir_reports`;
- exact pinned Atomic commit;
- GUID, name, Windows platform, input keys, dependencies, elevation, embedded URLs, and cleanup against local Atomic YAML;
- every mutating step has Atomic or custom cleanup;
- only loopback URLs unless an isolated endpoint was explicitly supplied;
- both PowerShell files parse successfully and `run.ps1 -Mode Plan` exits zero.

## `README.md`

Keep it operational: prerequisites, exact Plan/Execute/Verify/Cleanup commands, expected mutations, control-file removal before the investigation snapshot, snapshot timing, and safety boundary. Do not duplicate the source report or produce a long attack-chain essay.

## Completion gate

A package is complete only when all five files exist, static validation passes, PowerShell parsing passes, and Plan mode succeeds. Generation must never run Execute mode.
