#!/usr/bin/env python3
"""Validate scenario references against the checked-out Atomic Red Team catalog."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
SCENARIO = Path(__file__).with_name("scenario.yml")
DEFAULT_ATOMICS = ROOT / "atomic-red-team" / "atomics"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--atomics", type=Path, default=DEFAULT_ATOMICS)
    args = parser.parse_args()

    scenario = yaml.safe_load(SCENARIO.read_text(encoding="utf-8"))
    errors: list[str] = []
    external_targets: list[str] = []

    for step in scenario["steps"]:
        technique = step["technique"]
        guid = step["atomic_guid"]
        atomic_file = args.atomics / technique / f"{technique}.yaml"
        if not atomic_file.is_file():
            errors.append(f"missing Atomic definition: {atomic_file}")
            continue
        definition = yaml.safe_load(atomic_file.read_text(encoding="utf-8"))
        tests = [test for test in definition.get("atomic_tests", []) if test.get("auto_generated_guid") == guid]
        if len(tests) != 1:
            errors.append(f"{technique} expected one test for {guid}, found {len(tests)}")
            continue
        test = tests[0]
        if "windows" not in test.get("supported_platforms", []):
            errors.append(f"{technique}/{guid} is not a Windows test")
        if test.get("executor", {}).get("elevation_required", False):
            errors.append(f"{technique}/{guid} unexpectedly requires elevation")
        if test.get("dependencies"):
            errors.append(f"{technique}/{guid} unexpectedly has external dependencies")
        for value in (step.get("input_args") or {}).values():
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                external_targets.append(value)

    if external_targets != ["http://127.0.0.1:18088/beacon"]:
        errors.append(f"unexpected network targets: {external_targets}")
    if scenario["safety"]["external_network"] is not False:
        errors.append("scenario must explicitly disable external networking")
    if errors:
        raise SystemExit("Scenario validation failed:\n- " + "\n- ".join(errors))

    print(
        f'PASS: {scenario["scenario_id"]}; {len(scenario["steps"])} Atomic tests; '
        "Windows only; no elevation, external dependencies, or external network targets"
    )


if __name__ == "__main__":
    main()
