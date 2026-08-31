# Fidelity and safety rules for runnable scenarios

Read this reference before selecting or adapting Atomic tests.

## Four-layer separation

Keep these layers distinct in every runnable package:

1. **Source fact:** what the report directly records or attributes.
2. **Semantic interpretation:** the ATT&CK behavior represented by that fact.
3. **Simulation implementation:** the selected Atomic test, custom canary, or omitted step.
4. **Ground Truth:** evidence the implementation actually leaves in the benchmark environment.

An implementation can preserve the semantics without reproducing malware mechanics. Its evidence must not be described as evidence from the historical incident.

## Executable package boundary

- Generate code only for disposable, recoverable lab targets. The package must not assume that generation authorizes execution.
- `run.ps1 -Mode Plan` must make no changes. `Execute` requires an explicit confirmation switch and must abort before mutation when prerequisites or the pinned Atomic commit do not match.
- A package must be complete when generated: no TODO commands, placeholder GUIDs, unresolved paths, missing cleanup, or operator copy/paste from narrative text.
- Keep execution and cleanup narrowly scoped. Cleanup must be idempotent and safe after a partially completed run.
- Do not automatically clean after execution; preserve evidence until the investigation episode is complete.
- Do not store Ground Truth, expected answers, execution transcripts, or verification results inside the investigated scenario directory. Verification prints JSON to the controller or an explicit path outside the target evidence tree.
- Generation-time validation may run parsers and Plan mode only. It must never run Execute or Cleanup.

## Source confidence labels

- `observed`: the report states the analysts observed the behavior or provides direct telemetry.
- `reported`: the report states the behavior as part of the incident narrative but does not expose direct telemetry in the archived text.
- `inferred`: the report uses language such as likely, assess, appears, may, or probably.
- `unknown`: a transition is missing or cannot be established from the report.

Only `observed` and `reported` steps should normally enter the executable chain. An `inferred` step may be retained only when its uncertainty is displayed and it is not required for scoring.

## Safe substitution matrix

| Report behavior | Default benchmark implementation | Required disclosure |
|---|---|---|
| Malicious document or user execution | Harmless lure plus user simulator or canary file creation | Mark as semantic substitution if Office/macros are not actually executed |
| Malware/DLL/implant | Text or signed canary in a scenario-owned directory | State that the extension does not represent a real payload |
| Public download or C2 | Loopback or isolated Mock HTTP/DNS service | Record the substituted endpoint and prohibit report IOCs |
| Credential theft or LSASS access | Fake credential corpus or an explicitly non-secret canary | Do not claim real credential access; score only canary evidence |
| Exploit execution | Preconditioned transition or benign harness | Do not claim the CVE was reproduced unless it actually was in an isolated lab |
| Process injection | Prefer omission or a reviewed benign Atomic in a disposable VM | Treat memory-only evidence as optional unless capture is guaranteed |
| Ransomware/impact | Rename or transform files only inside a dedicated disposable test directory | No user files, shadow copies, backups, or security controls may be changed |
| Lateral movement | Use only an explicitly authorized isolated multi-VM lab | Separate orchestration/control traffic from simulated attack evidence |
| Defender/security weakening | Omit by default | Include only with explicit user authorization and guaranteed cleanup |

## Atomic selection order

Prefer candidates in this order:

1. Same ATT&CK technique and matching platform.
2. Read-only or scenario-owned mutation.
3. No elevation.
4. No external dependency or download.
5. Deterministic evidence that survives until investigation.
6. Built-in cleanup, or a narrow custom cleanup for exact scenario-owned artifacts.

Reject a candidate when its actual command has materially different semantics, touches broad host state, depends on uncontrolled internet services, lacks a verifiable artifact, or cannot be cleaned safely.

## Adaptation rules

- Input overrides may change file names, paths, usernames, task names, ports, and endpoints while preserving technique semantics.
- Put artifacts under a scenario-owned directory such as `C:\ProgramData\EndpointIRBench\<chain-id>` or `/tmp/endpointir-bench/<chain-id>`.
- For network tests, allow only `127.0.0.1`, `localhost`, or an isolated address explicitly supplied by the user.
- Record the original Atomic GUID and every override. Do not edit the vendored Atomic YAML merely to make validation pass.
- If an Atomic command embeds a public URL or has a dependency downloader, treat it as unsafe unless the chosen test is replaced or the dependency is already vendored and hash-verified.
- Implement every `custom_canary` directly in the generated runner with a paired cleanup function. Do not leave prose-only substitutions in executable steps.

## Evidence rules

For every required finding specify:

- entity and exact expected value;
- evidence surface, such as registry, file, process, event log, browser history, network, or Mock service log;
- time relationship to adjacent actions;
- independent verification method;
- whether evidence is required or optional.

Do not score volatile evidence such as a live process or connection unless the episode freezes the host while it is present. Controller success, stdout, or an Atomic return code alone is not proof that endpoint evidence exists.

For process or command evidence, require Sysmon, Windows 4688 auditing, PowerShell Operational logging, or another independently configured telemetry source. A runner transcript is not a substitute.
