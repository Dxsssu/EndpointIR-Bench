---
name: ir-report-to-atomic-chain
description: Convert public incident-response and DFIR reports into source-grounded, safety-adjusted, locally validated Atomic Red Team scenario packages that can be run directly on disposable Windows lab targets. Use for single-report or batch scenario generation; do not use to execute scenarios without separate authorization.
---

# IR Report to Runnable Atomic Scenario

Turn archived DFIR narratives into directly runnable Windows investigation scenarios. The primary deliverable is executable code, not an attack-chain essay.

## Required workspace inputs

Locate the repository root. It must contain:

- `public_ir_reports/manifest.csv` and its referenced reports;
- `atomic_red_team/atomics/` as the pinned local Atomic Red Team catalog;
- a writable `scenarios/` directory.

Do not substitute remembered ATT&CK or Atomic details for local validation, and do not browse for payloads.

## Output contract

Create one self-contained directory per selected report:

```text
scenarios/<scenario-id>/
|-- scenario.json
|-- run.ps1
|-- verify.ps1
|-- validate_scenario.py
`-- README.md
```

The package must support these commands on a disposable Windows target with `Invoke-AtomicTest` available:

```powershell
.\run.ps1 -Mode Plan
.\run.ps1 -Mode Execute -ConfirmExecution -PathToAtomicsFolder <path>
.\run.ps1 -Mode Cleanup -PathToAtomicsFolder <path>
```

`Plan` must be side-effect free. `Execute` must require `-ConfirmExecution`. `Cleanup` must remove only exact scenario-owned changes. Do not generate a package that needs manual code editing before these commands work.

Read [references/output-schema.md](references/output-schema.md) before generating files. Read [references/fidelity-safety.md](references/fidelity-safety.md) before choosing or adapting tests.

## Modes

- **Single report:** generate one runnable package for the named report.
- **Filtered batch:** honor source, A/B level, date, platform, count, or report IDs.
- **Unscoped batch:** default to unprocessed A-class Windows reports. Use resumable batches and do not silently include B-class material.

Use `scripts/prepare_batch.py` for a deterministic queue. A report is already processed only when its scenario directory contains all five required files. Do not overwrite an existing package unless the user asks to regenerate it or its source changed materially.

## Workflow

1. Read the manifest row and complete normalized report. Extract the causal sequence before assigning ATT&CK IDs; label source steps `observed`, `reported`, `inferred`, or `unknown`.
2. Select the smallest useful Windows slice. Prefer L1 or single-host L2. Generate L3 only when the user has explicitly supplied an authorized isolated multi-VM topology.
3. Map retained actions to exact tests in the pinned local Atomic catalog. Verify GUID, name, platform, executor, input arguments, dependencies, elevation, command, observable effects, and cleanup from the YAML itself.
4. Reject unsafe or unreliable tests. Use inline harmless PowerShell canary functions for safe semantic substitutions; omit unsupported behavior rather than emitting a placeholder that prevents execution.
5. Generate the complete package. Embed exact Atomic GUIDs and input overrides in `run.ps1`; do not make the operator copy commands out of Markdown.
6. Make verification independent of the Atomic return code. `verify.ps1` must inspect endpoint evidence or isolated Mock-service records and emit JSON to stdout. It must not treat transcripts, scenario state, or controller success as Ground Truth.
7. Validate `scenario.json`, validate every Atomic reference against `atomic_red_team`, parse both PowerShell files with the PowerShell AST parser, and run `run.ps1 -Mode Plan`. Never run `Execute` as part of generation or validation.
8. Report generated, skipped, and failed packages, including any scenario rejected because it could not be made safe and directly runnable.

## Runtime invariants

- Preserve report causal order; do not sort by ATT&CK tactic.
- Pin and check the Atomic repository commit at runtime. Abort before mutation if it differs from the expected commit embedded during generation.
- Treat the generated directory as a control-plane asset. `run.ps1` and `verify.ps1` must each be standalone and must not require `scenario.json` at runtime; embed the pinned commit and required constants in the scripts.
- Resolve all paths from `$PSScriptRoot` or explicit parameters. Do not embed the generator machine's absolute paths.
- Keep scenario mutations under `C:\ProgramData\EndpointIRBench\<scenario-id>` and exact scenario-owned registry/task/service names.
- Use only loopback Mock services by default. A user-supplied isolated address is allowed only when recorded in `scenario.json`; public report IOCs are never execution targets.
- Start required Mock services inside `run.ps1`, wait until ready, enforce timeouts, and always stop them in `finally` blocks.
- Stop on the first failed step, preserve already-created evidence, and leave cleanup explicit. Never silently clean immediately after execution.
- Make `Cleanup` idempotent and safe after partial execution.
- Keep controller truth off the investigated endpoint. If a runner is copied into the VM, remove the runner and package files before taking the investigation snapshot without deleting the generated endpoint evidence. `verify.ps1` prints results; it writes a file only to an explicit operator-supplied output path.
- Do not generate real malware, credential theft, production exploitation, external C2, security-control weakening, user-data encryption, or unauthorized lateral movement.
- Code generation does not authorize execution. Execute only after a separate user request identifies an authorized, recoverable lab target.

## Supporting scripts

Resolve paths relative to this file:

```bash
python scripts/prepare_batch.py --repo-root <repo> --level A --platform Windows
python scenarios/<scenario-id>/validate_scenario.py --repo-root <repo>
```

The Agent remains responsible for source interpretation and safe implementation. A validator passing does not replace human review of the generated commands.
