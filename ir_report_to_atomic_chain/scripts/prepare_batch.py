#!/usr/bin/env python3
"""Prepare a deterministic, resumable queue of IR reports for chain extraction."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-.")
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
    manifest = repo / "Public_IR_Reports" / "manifest.csv"
    atomics = repo / "atomic-red-team" / "atomics"
    if not manifest.is_file():
        raise SystemExit(f"Manifest not found: {manifest}")
    if not atomics.is_dir():
        raise SystemExit(f"Atomic catalog not found: {atomics}")

    output_dir = repo / "docs" / "atomic-chains"
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
        report_path = repo / "Public_IR_Reports" / report_relative
        if not report_path.is_file():
            raise SystemExit(f"Manifest references a missing report: {report_path}")
        output_path = output_dir / f"{safe_name(row['id'])}.md"
        exists = output_path.is_file()
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
                "report_path": str(report_path),
                "report_relative": str(report_path.relative_to(repo)),
                "output_path": str(output_path),
                "output_relative": str(output_path.relative_to(repo)),
                "already_exists": exists,
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
            and (output_dir / f"{safe_name(row['id'])}.md").is_file()
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
