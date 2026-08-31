# Output schema

Read this reference before creating a chain document.

## Location and naming

- One report maps to one document: `docs/atomic-chains/<report-id>.md`.
- Use the manifest `id` as `<report-id>`, replacing only filesystem-unsafe characters.
- Rebuild the aggregate index at `docs/Atomic攻击链索引.md` after a batch.

## Required YAML frontmatter

```yaml
---
chain_id: IRCHAIN-<stable-id>
report_id: <manifest id>
title: <Chinese scenario title>
source: <publisher>
published: YYYY-MM-DD
source_report: Public_IR_Reports/<relative path>
source_url: https://...
use_level: A
scenario_level: L1 | L2 | L3
platform: windows | linux | macos | mixed
atomic_repo_commit: <git commit>
generated_at: YYYY-MM-DD
atomic_tests:
  - order: 1
    technique: T1059.003
    guid: 00000000-0000-0000-0000-000000000000
    name: Exact Atomic test name
    implementation: atomic
    source_confidence: observed
    mutates_state: true
    input_args:
      file_contents_path: 'C:\ProgramData\EndpointIRBench\<chain-id>\marker.txt'
    allow_elevation: false
    allow_dependencies: false
  - order: 2
    technique: T1204.002
    implementation: custom_canary
    source_confidence: reported
    mutates_state: true
    custom_cleanup: Remove only the scenario-owned lure and marker files.
---
```

For `implementation: atomic`, `guid` and exact `name` are required. For `custom_canary` or `not_simulated`, omit `guid` and explain the implementation in the document. Set `allow_elevation` or `allow_dependencies` to true only with an explicit, narrowly scoped justification in `## 安全与适配说明`.

## Required Chinese sections

### 1. 来源与场景范围

Link the local report and original URL. State why the report and slice were selected, the target level, host count, and platform. Mention any material source uncertainty.

### 2. 报告原始攻击链

Show the causal narrative before modification. Use a table with: order, source behavior, confidence label, report evidence or section, and whether retained.

### 3. 可执行攻击语义链

Provide one concise arrow chain showing only retained simulated behavior.

### 4. Atomic Red Team 映射

Use a table with:

| # | 语义动作 | ATT&CK | Atomic 名称/GUID | 平台与执行器 | 参数调整 | 预期证据 | Cleanup |

If a step uses `custom_canary` or `not_simulated`, say so explicitly instead of inventing a GUID.

### 5. 安全与适配说明

List removed behaviors, semantic substitutions, endpoint/path overrides, elevation or dependency exceptions, and the boundary of scenario-owned data.

### 6. Ground Truth

List required and optional findings. Each required item must include exact expected values, evidence surface, temporal relation, and a verifier independent of the Atomic controller output.

### 7. 调查任务

Provide a sparse initial alert and the questions the investigation Agent must answer. Do not reveal every Ground Truth value in the initial alert.

### 8. 执行与清理计划

Provide reviewed `Invoke-AtomicTest` invocations in causal order, but do not execute them. Include prerequisites, mock-service requirements, snapshot timing, and explicit cleanup commands. Commands must use the selected GUIDs and recorded input overrides.

### 9. 未覆盖与人工复核项

Record omitted report behaviors, fidelity gaps, volatile evidence, unsupported platforms, and decisions requiring a security expert.

## Quality gate

A document is ready for the index only when:

- the local report and source URL are present;
- causal steps are source-labelled;
- all Atomic GUIDs validate against the checked-out catalog;
- adaptations are disclosed;
- external network and unsafe payloads are absent;
- mutating steps have cleanup;
- required Ground Truth is independently verifiable;
- the document passes `validate_chain_docs.py`.
