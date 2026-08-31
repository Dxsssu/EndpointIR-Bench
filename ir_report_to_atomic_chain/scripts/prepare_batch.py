#!/usr/bin/env python3
"""Prepare a deterministic, resumable queue of IR reports for runnable scenarios."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-.").lower()
    if not cleaned:
        raise ValueError(f"Cannot derive output name from report id: {value!r}")
    return cleaned


def source_matches(source: str, requested: list[str]) -> bool:
    if not requested:
        return True
    lower = source.lower()
    return any(term.lower() in lower for term in requested)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--level", choices=("A", "B", "all"), default="A")
    parser.add_argument("--source", action="append", default=[], help="Substring filter; repeatable")
    parser.add_argument("--platform", default="", help="Case-insensitive platform substring")
    parser.add_argument("--date-from", default="", help="Inclusive YYYY-MM-DD")
    parser.add_argument("--date-to", default="", help="Inclusive YYYY-MM-DD")
    parser.add_argument("--report-id", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0, help="0 means every matching report")
    parser.add_argument("--include-existing", action="store_true")
    parser.add_argument("--format", choices=("jsonl", "json"), default="jsonl")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    repo = args.repo_root.resolve()
    manifest = repo / "public_ir_reports" / "manifest.csv"
    atomics = repo / "atomic_red_team" / "atomics"
    if not manifest.is_file():
        raise SystemExit(f"Manifest not found: {manifest}")
    if not atomics.is_dir():
        raise SystemExit(f"Atomic catalog not found: {atomics}")

    output_dir = repo / "scenarios"
    required_files = (
        "scenario.json",
        "run.ps1",
        "verify.ps1",
        "validate_scenario.py",
        "README.md",
    )
    selected: list[dict[str, object]] = []
    rows = list(csv.DictReader(manifest.open(encoding="utf-8")))
    rows.sort(key=lambda row: (row["published"], row["source"], row["id"]), reverse=True)

    requested_ids = set(args.report_id)
    for row in rows:
        if args.level != "all" and row["use_level"] != args.level:
            continue
        if requested_ids and row["id"] not in requested_ids:
            continue
        if not source_matches(row["source"], args.source):
            continue
        if args.platform and args.platform.lower() not in row["platform"].lower():
            continue
        if args.date_from and row["published"] < args.date_from:
            continue
        if args.date_to and row["published"] > args.date_to:
            continue

        report_relative = row["normalized_file"] or row["source_file"]
        report_path = repo / "public_ir_reports" / report_relative
        if not report_path.is_file():
            raise SystemExit(f"Manifest references a missing report: {report_path}")
        scenario_id = safe_name(row["id"])
        output_path = output_dir / scenario_id
        existing_files = sorted(
            name for name in required_files if (output_path / name).is_file()
        )
        exists = len(existing_files) == len(required_files)
        if exists and not args.include_existing:
            continue

        selected.append(
            {
                "report_id": row["id"],
                "source": row["source"],
                "published": row["published"],
                "title": row["title"],
                "use_level": row["use_level"],
                "platform": row["platform"],
                "scenario_focus": row["scenario_focus"],
                "source_url": row["source_url"],
                "scenario_id": scenario_id,
                "report_path": str(report_path),
                "report_relative": str(report_path.relative_to(repo)),
                "scenario_dir": str(output_path),
                "scenario_relative": str(output_path.relative_to(repo)),
                "scenario_file": str(output_path / "scenario.json"),
                "run_file": str(output_path / "run.ps1"),
                "verify_file": str(output_path / "verify.ps1"),
                "validator_file": str(output_path / "validate_scenario.py"),
                "readme_file": str(output_path / "README.md"),
                "already_exists": exists,
                "existing_files": existing_files,
            }
        )
        if args.limit and len(selected) >= args.limit:
            break

    if requested_ids:
        found = {item["report_id"] for item in selected}
        existing_requested = {
            row["id"]
            for row in rows
            if row["id"] in requested_ids
            and all(
                (output_dir / safe_name(row["id"]) / name).is_file()
                for name in required_files
            )
            and not args.include_existing
        }
        missing = requested_ids - found - existing_requested
        if missing:
            raise SystemExit(f"Requested report IDs were not selected: {sorted(missing)}")

    if args.format == "json":
        rendered = json.dumps(selected, ensure_ascii=False, indent=2) + "\n"
    else:
        rendered = "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in selected)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Queued {len(selected)} reports in {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(rendered)


if __name__ == "__main__":
    main()
