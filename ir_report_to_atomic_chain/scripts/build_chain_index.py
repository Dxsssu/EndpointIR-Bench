#!/usr/bin/env python3
"""Build docs/Atomic攻击链索引.md from generated chain frontmatter."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError as error:  # pragma: no cover - environment diagnostic
    raise SystemExit("PyYAML is required: install the 'yaml' Python package") from error


def load_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"Missing YAML frontmatter: {path}")
    raw, _ = text[4:].split("\n---\n", 1)
    metadata = yaml.safe_load(raw)
    if not isinstance(metadata, dict):
        raise ValueError(f"Invalid YAML frontmatter: {path}")
    return metadata


def cell(value: object) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo_root.resolve()
    chain_dir = repo / "docs" / "atomic-chains"
    output = repo / "docs" / "Atomic攻击链索引.md"
    records: list[tuple[Path, dict[str, object]]] = []
    for path in sorted(chain_dir.glob("*.md")):
        records.append((path, load_frontmatter(path)))
    if not records:
        raise SystemExit(f"No chain documents found in {chain_dir}")

    records.sort(key=lambda item: (str(item[1].get("source", "")), str(item[1].get("published", ""))), reverse=True)
    levels = Counter(str(metadata.get("scenario_level")) for _, metadata in records)
    sources = Counter(str(metadata.get("source")) for _, metadata in records)
    techniques = {
        str(test.get("technique"))
        for _, metadata in records
        for test in metadata.get("atomic_tests", [])
        if isinstance(test, dict) and test.get("implementation") == "atomic" and test.get("technique")
    }

    lines = [
        "# Atomic Red Team 攻击链索引",
        "",
        f"更新时间：{date.today().isoformat()}。当前包含 **{len(records)} 条**从公开溯源报告提取并映射的攻击链，覆盖 **{len(techniques)} 种**唯一 ATT&CK 技术。",
        "",
        "本索引应仅在所有新增文档通过 `validate_chain_docs.py` 后重建。攻击链文档是模拟规格，不代表已经执行。",
        "",
        f"场景等级：L1 {levels['L1']} 条、L2 {levels['L2']} 条、L3 {levels['L3']} 条。来源："
        + "、".join(f"{source} {count} 条" for source, count in sorted(sources.items()))
        + "。",
        "",
        "| # | 攻击链 | 来源报告 | 来源 | 日期 | 等级 | 平台 | Atomic 步骤 | ATT&CK 技术 | Atomic 提交 |",
        "|---:|---|---|---|---|:---:|---|---:|---|---|",
    ]

    for index, (path, metadata) in enumerate(records, start=1):
        tests = [
            test
            for test in metadata.get("atomic_tests", [])
            if isinstance(test, dict) and test.get("implementation") == "atomic"
        ]
        technique_text = ", ".join(dict.fromkeys(str(test.get("technique")) for test in tests))
        chain_link = f"[查看](<atomic-chains/{path.name}>)"
        source_report = str(metadata.get("source_report", ""))
        source_link = f"[{cell(metadata.get('title', metadata.get('report_id', '报告')))}](<../{source_report}>)"
        commit = str(metadata.get("atomic_repo_commit", ""))
        lines.append(
            "| "
            + " | ".join(
                (
                    str(index),
                    chain_link,
                    source_link,
                    cell(metadata.get("source", "")),
                    cell(metadata.get("published", "")),
                    cell(metadata.get("scenario_level", "")),
                    cell(metadata.get("platform", "")),
                    str(len(tests)),
                    cell(technique_text),
                    cell(commit[:12]),
                )
            )
            + " |"
        )

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} chains to {output}")


if __name__ == "__main__":
    main()
