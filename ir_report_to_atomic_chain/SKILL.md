---
name: ir-report-to-atomic-chain
description: Convert public incident-response and DFIR reports into source-grounded, safety-adjusted, locally validated Atomic Red Team attack-chain documents. Use for one-report extraction or batch generation into docs/atomic-chains; do not use to execute attacks or invent unsupported report facts.
---

# IR Report to Atomic Chain

Turn archived DFIR narratives into reproducible attack-chain specifications for an endpoint-investigation benchmark. The deliverable is documentation and validation metadata, not attack execution.

## Required workspace inputs

Locate the repository root before acting. It must contain:

- `Public_IR_Reports/manifest.csv` and the report files referenced by it;
- `atomic-red-team/atomics/` with local Atomic YAML definitions;
- a writable `docs/` directory, creating it when needed.

If the report collection or Atomic catalog is missing, stop and report the missing input. Do not replace local validation with remembered ATT&CK or Atomic details, and do not browse for payloads.

## Modes

- **Single report:** process the report named or linked by the user.
- **Filtered batch:** honor requested source, A/B level, date range, platform, count, or report IDs.
- **Unscoped batch:** default to unprocessed A-class reports. Process every matching report, using resumable batches when context requires it; do not silently include B-class material.

Use `scripts/prepare_batch.py` to produce a deterministic queue and skip documents already present in `docs/atomic-chains/`. Do not overwrite an existing chain document unless the user asks to regenerate it or the source manifest changed materially.

## Workflow

1. Read the selected manifest row and the complete normalized report. For a PDF without normalized Markdown, use the available PDF-reading workflow and cite page numbers.
2. Extract the report's causal sequence before assigning ATT&CK IDs. Label each source step as `observed`, `reported`, `inferred`, or `unknown`; never convert analyst uncertainty into fact.
3. Select a benchmark slice. Prefer the smallest causally meaningful chain: L1 for one semantic action, L2 for a single-host multi-step chain, and L3 only when cross-host evidence is essential. Record omitted steps.
4. Map each retained semantic action to ATT&CK and then to an exact local Atomic test. Inspect the technique YAML and verify GUID, name, platform, executor, inputs, dependencies, elevation requirement, observable effects, and cleanup. Never select an Atomic test from its title alone.
5. When no safe Atomic test preserves the report behavior, use `custom_canary` or `not_simulated`; do not force an inaccurate mapping. Document every semantic substitution.
6. Read [references/fidelity-safety.md](references/fidelity-safety.md) before choosing or adapting tests. External targets, malware, credential theft, exploit execution, process injection, and ransomware require the safe substitutions defined there.
7. Read [references/output-schema.md](references/output-schema.md) before writing. Save one document per report under `docs/atomic-chains/<report-id>.md`, with machine-readable YAML frontmatter and the required Chinese sections.
8. Run `scripts/validate_chain_docs.py` against every new or changed document. Fix errors rather than suppressing them. Then run `scripts/build_chain_index.py` to rebuild `docs/Atomic攻击链索引.md`.
9. Report the number generated, skipped, and failed, plus validation errors that still require human judgment.

## Non-negotiable invariants

- Preserve causal order from the report; do not sort steps merely by ATT&CK tactic.
- Separate report facts, ATT&CK interpretation, Atomic implementation, and Ground Truth. Ground Truth may contain only evidence the selected implementation is expected to create and that an independent verifier can check.
- Prefer no-elevation, no-dependency tests with cleanup. A mutating test without cleanup is invalid unless the document provides a narrowly scoped custom cleanup and explains it.
- Replace public C2 and download URLs with loopback or an explicitly provided isolated mock service. Never reuse report IOCs as live targets.
- Use harmless canary data and scenario-owned paths. Do not generate or fetch real malware, dump real credentials, exploit a production vulnerability, encrypt user data, weaken host security, or perform lateral movement outside an authorized disposable lab.
- Generating a chain does not authorize executing it. Only execute when the user separately requests execution and supplies an authorized, recoverable target environment.
- Every Atomic entry in frontmatter must use a GUID found in the checked-out local repository. Record the Atomic repository commit so later changes are detectable.

## Supporting scripts

Resolve script paths relative to this `SKILL.md` file.

```bash
python3 scripts/prepare_batch.py --repo-root <repo> --level A
python3 scripts/validate_chain_docs.py --repo-root <repo> <docs...>
python3 scripts/build_chain_index.py --repo-root <repo>
```

The scripts handle queueing, structural checks, local Atomic verification, and index generation. The Agent remains responsible for reading each report, making the causal and semantic judgments, and correcting unsafe or unsupported mappings.
