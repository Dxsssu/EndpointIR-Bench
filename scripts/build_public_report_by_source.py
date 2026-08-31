#!/usr/bin/env python3
"""Build a source-grouped Markdown catalog of archived public IR reports."""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date

from build_public_report_summary import (
    MANIFEST,
    ROOT,
    cell,
    source_family,
    translate_focus,
)


OUTPUT = ROOT / "docs" / "公开溯源报告按来源汇总.md"
GROUPS = ("The DFIR Report", "Unit 42", "CISA 等机构")


def report_row(index: int, row: dict[str, str]) -> str:
    local_file = row["normalized_file"] or row["source_file"]
    local_target = f"../Public_IR_Reports/{local_file}"
    title = cell(row["title"])
    return (
        "| "
        + " | ".join(
            (
                str(index),
                cell(row["id"]),
                cell(row["published"]),
                f"[{title}](<{local_target}>)",
                cell(row["source"]),
                cell(row["use_level"]),
                cell(row["format"]),
                cell(row["platform"]),
                cell(translate_focus(row["scenario_focus"])),
                f"[原文](<{row['source_url']}>)",
            )
        )
        + " |"
    )


def main() -> None:
    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    grouped = {group: [] for group in GROUPS}
    for row in rows:
        grouped[source_family(row["source"])].append(row)
    for group_rows in grouped.values():
        group_rows.sort(key=lambda row: (row["published"], row["title"]), reverse=True)

    lines = [
        "# 公开溯源报告按来源汇总",
        "",
        f"更新时间：{date.today().isoformat()}。当前集合共收录 **{len(rows)} 份**公开溯源与事件响应材料，以下按照发布来源分组。",
        "",
        "A 类通常具有较完整的攻击时间线和终端证据，优先用于构建攻击场景；B 类主要是短文、年度总结、指南或覆盖参考，需要在使用前进一步复核。",
        "",
        "| 来源 | 报告数 | A 类 | B 类 | 年份范围 | 主要材料特征 |",
        "|---|---:|---:|---:|---|---|",
    ]

    characteristics = {
        "The DFIR Report": "真实入侵时间线、进程与命令、跨主机行为、C2 和勒索部署",
        "Unit 42": "事件响应案例、身份与云攻击、虚拟化环境和攻击组织画像",
        "CISA 等机构": "联合安全通告、调查结论、攻击者 TTP、IOC 和缓解建议",
    }
    for group in GROUPS:
        group_rows = grouped[group]
        levels = Counter(row["use_level"] for row in group_rows)
        years = sorted({row["published"][:4] for row in group_rows})
        lines.append(
            f"| {group} | {len(group_rows)} | {levels['A']} | {levels['B']} | "
            f"{years[0]}–{years[-1]} | {characteristics[group]} |"
        )

    for group in GROUPS:
        group_rows = grouped[group]
        levels = Counter(row["use_level"] for row in group_rows)
        lines.extend(
            (
                "",
                f"## {group}（{len(group_rows)} 份）",
                "",
                f"本组包含 A 类 {levels['A']} 份、B 类 {levels['B']} 份，按发布日期由新到旧排列。",
                "",
                "| # | 报告 ID | 发布日期 | 报告（本地文件） | 发布机构 | 级别 | 格式 | 平台 | 场景重点 | 原文 |",
                "|---:|---|---|---|---|:---:|:---:|---|---|:---:|",
            )
        )
        lines.extend(report_row(index, row) for index, row in enumerate(group_rows, start=1))

    lines.extend(
        (
            "",
            "## 维护方式",
            "",
            "`manifest.csv` 更新后运行以下命令重新生成本文档：",
            "",
            "```bash",
            "python3 scripts/build_public_report_by_source.py",
            "```",
            "",
            "逐条哈希、验证状态和原始存档路径以 [`manifest.csv`](../Public_IR_Reports/manifest.csv) 为准。未分组的单表版本见 [`公开溯源报告汇总.md`](公开溯源报告汇总.md)。",
        )
    )
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} source-grouped report rows to {OUTPUT}")


if __name__ == "__main__":
    main()
