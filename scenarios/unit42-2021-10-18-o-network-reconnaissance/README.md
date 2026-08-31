# Runnable Unit 42 reconnaissance scenario

This is a safe, single-host Windows lab slice derived from Unit 42's BazarLoader-to-reconnaissance report. It creates a harmless DLL-named text canary, one scenario-owned `HKCU` Run value, runs three built-in discovery Atomics, and sends four requests to a temporary loopback-only HTTP service. It does not contain malware, contact report IOCs, enumerate Active Directory, move laterally, or weaken security controls.

## Prerequisites

- A disposable, recoverable Windows VM.
- PowerShell with `Invoke-AtomicTest` imported.
- A local `atomic-red-team` checkout whose HEAD is exactly `6132b92779873cb0d05bef07ba0a480d47eb1cc8`.
- The path passed below must be that checkout's `atomics` directory.

## Commands

Preview only; this performs no host checks and makes no changes:

```powershell
.\run.ps1 -Mode Plan
```

Execute only after taking a clean VM snapshot and confirming the target is authorized:

```powershell
.\run.ps1 -Mode Execute -ConfirmExecution -PathToAtomicsFolder C:\AtomicRedTeam\atomics
```

Before giving the VM to an investigator, remove this control package from the target if it was copied into the VM. Do not remove `C:\ProgramData\EndpointIRBench\unit42-2021-10-18-o-network-reconnaissance`, because that is the endpoint evidence to investigate. Then take the investigation snapshot.

Verification reads independent endpoint evidence and prints JSON. Run it from the controller or save outside the scenario root:

```powershell
.\verify.ps1
.\verify.ps1 -OutputPath C:\ControllerResults\unit42-bazar-recon.json
```

After the investigation, remove only this scenario's registry value and files:

```powershell
.\run.ps1 -Mode Cleanup -PathToAtomicsFolder C:\AtomicRedTeam\atomics
```

The optional process-telemetry finding is scored only when the VM already has Sysmon Event ID 1 collection. Required findings use the canary file, exact registry value, and loopback Mock-service log.
