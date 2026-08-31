#!/usr/bin/env python3
"""Validate generated chain documents against the local Atomic Red Team catalog."""

from __future__ import annotations

import argparse
import ipaddress
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import yaml
except ImportError as error:  # pragma: no cover - environment diagnostic
    raise SystemExit("PyYAML is required: install the 'yaml' Python package") from error


REQUIRED_FIELDS = {
    "chain_id",
    "report_id",
    "title",
    "source",
    "published",
    "source_report",
    "source_url",
    "use_level",
    "scenario_level",
    "platform",
    "atomic_repo_commit",
    "generated_at",
    "atomic_tests",
}
REQUIRED_HEADINGS = (
    "## 来源与场景范围",
    "## 报告原始攻击链",
    "## 可执行攻击语义链",
    "## Atomic Red Team 映射",
    "## 安全与适配说明",
    "## Ground Truth",
    "## 调查任务",
    "## 执行与清理计划",
    "## 未覆盖与人工复核项",
)
CONFIDENCE = {"observed", "reported", "inferred", "unknown"}
IMPLEMENTATIONS = {"atomic", "custom_canary", "not_simulated"}
URL_PATTERN = re.compile(r"https?://[^\s'\"<>]+")


def load_frontmatter(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    try:
        raw, body = text[4:].split("\n---\n", 1)
    except ValueError as error:
        raise ValueError("unterminated YAML frontmatter") from error
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data, body


def git_commit(repository: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def external_url(value: str) -> bool:
    parsed = urlparse(value)
    host = parsed.hostname
    if not host:
        return False
    if host.lower() == "localhost":
        return False
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return True
    return not address.is_loopback


def urls_in(value: object) -> list[str]:
    if isinstance(value, dict):
        return [url for child in value.values() for url in urls_in(child)]
    if isinstance(value, list):
        return [url for child in value for url in urls_in(child)]
    if isinstance(value, str):
        return URL_PATTERN.findall(value)
    return []


def validate_document(path: Path, repo: Path, atomics: Path, commit: str) -> list[str]:
    errors: list[str] = []
    try:
        metadata, body = load_frontmatter(path)
    except Exception as error:  # noqa: BLE001 - aggregate all document failures
        return [str(error)]

    missing = sorted(REQUIRED_FIELDS - metadata.keys())
    if missing:
        errors.append(f"missing frontmatter fields: {missing}")
    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            errors.append(f"missing section: {heading}")

    source_report = metadata.get("source_report")
    if isinstance(source_report, str):
        source_path = (repo / source_report).resolve()
        collection = (repo / "Public_IR_Reports").resolve()
        if collection not in source_path.parents or not source_path.is_file():
            errors.append(f"source_report is missing or outside Public_IR_Reports: {source_report}")
    else:
        errors.append("source_report must be a string")

    source_url = metadata.get("source_url")
    if not isinstance(source_url, str) or not source_url.startswith(("https://", "http://")):
        errors.append("source_url must be an HTTP(S) URL")
    if str(metadata.get("atomic_repo_commit", "")) not in {commit, commit[:12], commit[:7]}:
        errors.append("atomic_repo_commit does not match the checked-out Atomic repository")
    if metadata.get("scenario_level") not in {"L1", "L2", "L3"}:
        errors.append("scenario_level must be L1, L2, or L3")

    tests = metadata.get("atomic_tests")
    if not isinstance(tests, list) or not tests:
        errors.append("atomic_tests must be a non-empty list")
        return errors

    orders: list[int] = []
    atomic_count = 0
    for position, item in enumerate(tests, start=1):
        label = f"atomic_tests[{position}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be a mapping")
            continue
        implementation = item.get("implementation")
        if implementation not in IMPLEMENTATIONS:
            errors.append(f"{label} has invalid implementation: {implementation!r}")
            continue
        confidence = item.get("source_confidence")
        if confidence not in CONFIDENCE:
            errors.append(f"{label} has invalid source_confidence: {confidence!r}")
        order = item.get("order")
        if not isinstance(order, int):
            errors.append(f"{label}.order must be an integer")
        else:
            orders.append(order)
        if not isinstance(item.get("mutates_state"), bool):
            errors.append(f"{label}.mutates_state must be boolean")

        if implementation == "not_simulated":
            continue
        if implementation == "custom_canary":
            if item.get("mutates_state") and not item.get("custom_cleanup"):
                errors.append(f"{label} custom canary mutates state but has no custom_cleanup")
            for url in urls_in(item.get("input_args", {})):
                if external_url(url):
                    errors.append(f"{label} uses a non-loopback target: {url}")
            continue

        atomic_count += 1
        technique = item.get("technique")
        guid = item.get("guid")
        expected_name = item.get("name")
        if not all(isinstance(value, str) and value for value in (technique, guid, expected_name)):
            errors.append(f"{label} atomic implementation requires technique, guid, and name")
            continue
        definition_path = atomics / technique / f"{technique}.yaml"
        if not definition_path.is_file():
            errors.append(f"{label} technique definition not found: {technique}")
            continue
        definition = yaml.safe_load(definition_path.read_text(encoding="utf-8"))
        matches = [test for test in definition.get("atomic_tests", []) if test.get("auto_generated_guid") == guid]
        if len(matches) != 1:
            errors.append(f"{label} expected one local Atomic test for {technique}/{guid}, found {len(matches)}")
            continue
        test = matches[0]
        if test.get("name") != expected_name:
            errors.append(f"{label} name mismatch: local name is {test.get('name')!r}")

        document_platform = str(metadata.get("platform", "")).lower()
        supported = {str(value).lower() for value in test.get("supported_platforms", [])}
        if document_platform != "mixed" and document_platform not in supported:
            errors.append(f"{label} platform {document_platform!r} not in {sorted(supported)}")
        dependencies = test.get("dependencies") or []
        if dependencies and not item.get("allow_dependencies", False):
            errors.append(f"{label} has {len(dependencies)} dependencies but allow_dependencies is false")
        executor = test.get("executor") or {}
        if executor.get("elevation_required", False) and not item.get("allow_elevation", False):
            errors.append(f"{label} requires elevation but allow_elevation is false")

        valid_inputs = set((test.get("input_arguments") or {}).keys())
        overrides = item.get("input_args") or {}
        if not isinstance(overrides, dict):
            errors.append(f"{label}.input_args must be a mapping")
            overrides = {}
        unknown_inputs = sorted(set(overrides) - valid_inputs)
        if unknown_inputs:
            errors.append(f"{label} has unknown input arguments: {unknown_inputs}")
        resolved_inputs = {
            key: value.get("default")
            for key, value in (test.get("input_arguments") or {}).items()
            if isinstance(value, dict)
        }
        resolved_inputs.update(overrides)
        for url in urls_in(resolved_inputs):
            if external_url(url):
                errors.append(f"{label} resolves to a non-loopback target: {url}")
        for url in urls_in(executor.get("command", "")):
            if external_url(url):
                errors.append(f"{label} command embeds a non-loopback URL: {url}")
        if item.get("mutates_state") and not executor.get("cleanup_command") and not item.get("custom_cleanup"):
            errors.append(f"{label} mutates state but has no Atomic or custom cleanup")

    if len(orders) != len(set(orders)):
        errors.append("atomic_tests contains duplicate order values")
    if orders and sorted(orders) != list(range(1, len(orders) + 1)):
        errors.append("atomic_tests order must be contiguous starting at 1")
    if atomic_count == 0:
        errors.append("chain must contain at least one locally validated Atomic test")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()

    repo = args.repo_root.resolve()
    atomics = repo / "atomic-red-team" / "atomics"
    atomic_repository = repo / "atomic-red-team"
    if not atomics.is_dir():
        raise SystemExit(f"Atomic catalog not found: {atomics}")
    paths = [path.resolve() for path in args.paths]
    if not paths:
        paths = sorted((repo / "docs" / "atomic-chains").glob("*.md"))
    if not paths:
        raise SystemExit("No chain documents found")

    commit = git_commit(atomic_repository)
    failures = 0
    seen_chain_ids: dict[str, Path] = {}
    seen_report_ids: dict[str, Path] = {}
    for path in paths:
        errors = validate_document(path, repo, atomics, commit)
        try:
            metadata, _ = load_frontmatter(path)
            for key, seen in (("chain_id", seen_chain_ids), ("report_id", seen_report_ids)):
                value = metadata.get(key)
                if isinstance(value, str) and value in seen:
                    errors.append(f"duplicate {key} also used by {seen[value]}")
                elif isinstance(value, str):
                    seen[value] = path
        except Exception:
            pass
        if errors:
            failures += 1
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path}")

    print(f"Validated {len(paths)} documents; {failures} failed")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
