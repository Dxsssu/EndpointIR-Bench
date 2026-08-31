#!/usr/bin/env python3
"""Statically validate this runnable scenario against the pinned local Atomic catalog."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


REQUIRED_FILES = {
    "scenario.json",
    "run.ps1",
    "verify.ps1",
    "validate_scenario.py",
    "README.md",
}
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "scenario_id",
    "title",
    "level",
    "platform",
    "host_count",
    "source",
    "atomic_repo_commit",
    "initial_alert",
    "safety",
    "steps",
    "expected_findings",
    "omitted_behaviors",
}
URL_PATTERN = re.compile(r"https?://[^\s\"']+", re.IGNORECASE)
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def fail(errors: list[str]) -> None:
    if errors:
        raise SystemExit("Scenario validation failed:\n- " + "\n- ".join(errors))


def run_checked(command: list[str], label: str, errors: list[str]) -> str:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        errors.append(f"{label} failed: {detail}")
        return ""
    return completed.stdout.strip()


def assert_local_url(value: str, context: str, errors: list[str]) -> None:
    for match in URL_PATTERN.findall(value):
        host = (urlparse(match).hostname or "").lower()
        if host not in LOOPBACK_HOSTS:
            errors.append(f"non-loopback URL in {context}: {match}")


def parse_powershell(script: Path, powershell: str, errors: list[str]) -> None:
    escaped_script = str(script).replace("'", "''")
    parser_command = (
        "$tokens=$null; $parseErrors=$null; "
        f"[System.Management.Automation.Language.Parser]::ParseFile('{escaped_script}', "
        "[ref]$tokens, [ref]$parseErrors) | Out-Null; "
        "if ($parseErrors.Count -gt 0) { "
        "$parseErrors | ForEach-Object { Write-Error $_.Message }; exit 1 }"
    )
    run_checked(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", parser_command],
        f"PowerShell AST parse for {script.name}",
        errors,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    package = Path(__file__).resolve().parent
    repo = args.repo_root.resolve()
    errors: list[str] = []

    missing = sorted(name for name in REQUIRED_FILES if not (package / name).is_file())
    if missing:
        errors.append("missing required package files: " + ", ".join(missing))

    scenario_path = package / "scenario.json"
    try:
        scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Unable to read scenario.json: {exc}") from exc

    missing_fields = sorted(REQUIRED_TOP_LEVEL - scenario.keys())
    if missing_fields:
        errors.append("missing scenario.json fields: " + ", ".join(missing_fields))
    if scenario.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if scenario.get("platform") != "windows":
        errors.append("platform must be windows")
    if scenario.get("host_count") != 1:
        errors.append("this safe package must target exactly one host")
    if scenario.get("safety", {}).get("external_network") is not False:
        errors.append("safety.external_network must be false")
    if scenario.get("safety", {}).get("requires_elevation") is not False:
        errors.append("safety.requires_elevation must be false")
    if scenario.get("safety", {}).get("allows_dependencies") is not False:
        errors.append("safety.allows_dependencies must be false")

    source_file = repo / scenario.get("source", {}).get("local_file", "")
    reports_root = (repo / "public_ir_reports").resolve()
    try:
        resolved_source = source_file.resolve()
        resolved_source.relative_to(reports_root)
        if not resolved_source.is_file():
            errors.append(f"source report does not exist: {resolved_source}")
    except ValueError:
        errors.append(f"source report escapes public_ir_reports: {source_file}")

    steps = scenario.get("steps", [])
    orders = [step.get("order") for step in steps]
    if orders != list(range(1, len(steps) + 1)):
        errors.append(f"step order must be contiguous from 1: {orders}")
    finding_ids = [item.get("id") for item in scenario.get("expected_findings", [])]
    if len(finding_ids) != len(set(finding_ids)):
        errors.append("expected finding IDs must be unique")
    if not all(finding_ids):
        errors.append("every expected finding must have a non-empty id")

    atomics_repo = repo / "atomic_red_team"
    atomics_root = atomics_repo / "atomics"
    if not atomics_root.is_dir():
        errors.append(f"Atomic catalog not found: {atomics_root}")
    git = shutil.which("git")
    if not git:
        errors.append("git is required to validate the pinned Atomic commit")
    else:
        actual_commit = run_checked(
            [git, "-C", str(atomics_repo), "rev-parse", "HEAD"],
            "Atomic commit lookup",
            errors,
        )
        if actual_commit and actual_commit != scenario.get("atomic_repo_commit"):
            errors.append(
                "Atomic commit mismatch: "
                f"scenario={scenario.get('atomic_repo_commit')} local={actual_commit}"
            )

    try:
        import yaml
    except ImportError as exc:
        raise SystemExit(
            "PyYAML is required for Atomic YAML validation. Install it with "
            f"'{sys.executable} -m pip install PyYAML' and rerun."
        ) from exc

    atomic_count = 0
    for step in steps:
        implementation = step.get("implementation")
        if step.get("mutates_state") and implementation == "custom_canary" and not step.get("cleanup_action"):
            errors.append(f"step {step.get('order')} custom mutation has no cleanup_action")
        if implementation == "custom_canary":
            continue
        if implementation != "atomic":
            errors.append(f"step {step.get('order')} has unsupported implementation: {implementation}")
            continue

        atomic_count += 1
        technique = step.get("technique", "")
        guid = step.get("atomic_guid", "")
        atomic_file = atomics_root / technique / f"{technique}.yaml"
        if not atomic_file.is_file():
            errors.append(f"missing Atomic definition: {atomic_file}")
            continue
        definition = yaml.safe_load(atomic_file.read_text(encoding="utf-8"))
        matches = [
            test
            for test in definition.get("atomic_tests", [])
            if test.get("auto_generated_guid") == guid
        ]
        if len(matches) != 1:
            errors.append(f"{technique} expected one test for {guid}, found {len(matches)}")
            continue
        test = matches[0]
        if test.get("name") != step.get("atomic_name"):
            errors.append(
                f"{technique}/{guid} name mismatch: "
                f"scenario={step.get('atomic_name')!r} catalog={test.get('name')!r}"
            )
        if "windows" not in test.get("supported_platforms", []):
            errors.append(f"{technique}/{guid} is not a Windows test")
        executor = test.get("executor") or {}
        if executor.get("elevation_required", False):
            errors.append(f"{technique}/{guid} unexpectedly requires elevation")
        if test.get("dependencies"):
            errors.append(f"{technique}/{guid} unexpectedly has dependencies")

        declared_inputs = test.get("input_arguments") or {}
        supplied_inputs = step.get("input_args") or {}
        unknown_inputs = sorted(set(supplied_inputs) - set(declared_inputs))
        if unknown_inputs:
            errors.append(
                f"{technique}/{guid} has unknown input overrides: {', '.join(unknown_inputs)}"
            )
        resolved_command = str(executor.get("command", ""))
        for key, details in declared_inputs.items():
            value = supplied_inputs.get(key, details.get("default", ""))
            resolved_command = resolved_command.replace(f"#{{{key}}}", str(value))
            if isinstance(value, str):
                assert_local_url(value, f"{technique}/{guid} input {key}", errors)
        assert_local_url(resolved_command, f"{technique}/{guid} resolved command", errors)

        if step.get("mutates_state") and not executor.get("cleanup_command") and not step.get("cleanup_action"):
            errors.append(f"mutating step {step.get('order')} has no Atomic or custom cleanup")

    run_text = (package / "run.ps1").read_text(encoding="utf-8")
    verify_text = (package / "verify.ps1").read_text(encoding="utf-8")
    for forbidden in ("Start-Transcript", "execution-transcript", "verification.json"):
        if forbidden.lower() in run_text.lower():
            errors.append(f"run.ps1 contains forbidden controller-truth artifact: {forbidden}")
    for script_name, script_text in (("run.ps1", run_text), ("verify.ps1", verify_text)):
        if "scenario.json" in script_text:
            errors.append(f"{script_name} must be standalone and not read scenario.json")
        assert_local_url(script_text, script_name, errors)
    for required_text in (
        scenario.get("atomic_repo_commit", ""),
        "NoExecutionLog",
        "ConfirmExecution",
        "127b4afe-2346-4192-815c-69042bec570e",
        "66703791-c902-4560-8770-42b8a91f7667",
        "970ab6a1-0157-4f3f-9a73-ec4166754b23",
        "2d5a61f5-0447-4be4-944a-1f8530ed6574",
        "81c13829-f6c9-45b8-85a6-053366d55297",
    ):
        if required_text not in run_text:
            errors.append(f"run.ps1 is missing required pinned value: {required_text}")

    powershell = shutil.which("pwsh") or shutil.which("powershell")
    if not powershell:
        errors.append("pwsh or powershell is required for AST and Plan validation")
    else:
        parse_powershell(package / "run.ps1", powershell, errors)
        parse_powershell(package / "verify.ps1", powershell, errors)
        plan_output = run_checked(
            [
                powershell,
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(package / "run.ps1"),
                "-Mode",
                "Plan",
            ],
            "run.ps1 Plan smoke test",
            errors,
        )
        if plan_output and "made no changes" not in plan_output:
            errors.append("Plan output does not affirm its no-change boundary")

    fail(errors)
    print(
        f"PASS: {scenario['scenario_id']}; {atomic_count} exact Atomic tests; "
        "PowerShell parsed; Plan succeeded; network targets are loopback only"
    )


if __name__ == "__main__":
    main()
