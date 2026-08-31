# CISA AA23-289A safe Ubuntu scenario

This single-host Ubuntu lab scenario is derived from CISA AA23-289A. It writes a harmless application-audit canary for an unexpected Confluence administrator event, then runs one exact Linux Atomic test that stages fake text and uploads it with `curl` to a temporary loopback-only HTTP receiver. It does not exploit Confluence, create a real user, use credentials, install malware, or contact the internet.

## Prerequisites

- A disposable, recoverable Ubuntu VM.
- PowerShell 7 (`pwsh`) with `Invoke-AtomicRedTeam` installed and imported.
- `git` and `curl` already installed.
- A local `atomic-red-team` checkout at commit `6132b92779873cb0d05bef07ba0a480d47eb1cc8`.
- The path passed below must be that checkout's `atomics` directory.

## Commands

Preview only; this performs no host checks and makes no changes:

```bash
pwsh ./run.ps1 -Mode Plan
```

After taking a clean VM snapshot and confirming the target is authorized:

```bash
pwsh ./run.ps1 -Mode Execute -ConfirmExecution \
  -PathToAtomicsFolder /opt/atomic-red-team/atomics
```

If this package was copied into the VM, remove the package files before handing the VM to the investigator. Preserve `/tmp/endpointir-bench/cisa-aa23-289a-ubuntu`, which contains the endpoint evidence, and then take the investigation snapshot.

Verification reads the artifacts independently and prints JSON. An optional output must remain outside the evidence directory:

```bash
pwsh ./verify.ps1
pwsh ./verify.ps1 -OutputPath /tmp/controller-results/cisa-aa23-289a-ubuntu.json
```

After the investigation, remove only this scenario's files:

```bash
pwsh ./run.ps1 -Mode Cleanup \
  -PathToAtomicsFolder /opt/atomic-red-team/atomics
```

The temporary receiver binds only to `127.0.0.1:18089`, accepts one request, writes one compact evidence record, and is always stopped by the runner.
