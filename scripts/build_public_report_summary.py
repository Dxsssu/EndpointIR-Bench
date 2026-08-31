#!/usr/bin/env python3
"""Build the Markdown catalog for the archived public IR reports."""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "Public_IR_Reports"
MANIFEST = COLLECTION / "manifest.csv"
OUTPUT = ROOT / "docs" / "公开溯源报告汇总.md"

FOCUS_REPLACEMENTS = (
    ("known-vulnerability exploitation", "已知漏洞利用"),
    ("ransomware affiliate TTPs", "勒索联盟 TTP"),
    ("multi-stage intrusion investigation", "多阶段入侵调查"),
    ("phishing or user execution", "钓鱼或用户执行"),
    ("public-facing exploitation", "暴露服务利用"),
    ("Active Directory or privilege escalation", "AD 或权限提升"),
    ("remote services or credential attack", "远程服务或凭据攻击"),
    ("collection or exfiltration", "收集或数据外传"),
    ("identity or cloud investigation", "身份或云环境调查"),
    ("impact or ransomware", "影响或勒索软件"),
    ("red-team intrusion", "红队入侵"),
    ("persistence", "持久化"),
    ("credential access", "凭据访问"),
    ("detection gaps", "检测缺口"),
    ("response", "响应"),
    ("vulnerability chaining", "漏洞链利用"),
    ("webshells", "WebShell"),
    ("webshell", "WebShell"),
    ("detection", "检测"),
    ("lateral movement", "横向移动"),
    ("social engineering", "社会工程"),
    ("valid accounts", "有效账号"),
    ("remote access tools", "远程访问工具"),
    ("exfiltration", "数据外传"),
    ("valid RDP accounts", "有效 RDP 账号"),
    ("PowerShell", "PowerShell"),
    ("extortion", "勒索"),
    ("VPN access", "VPN 访问"),
    ("account creation", "账号创建"),
    ("Kerberoasting", "Kerberoasting"),
    ("LSASS", "LSASS"),
    ("ransomware", "勒索软件"),
    ("phishing", "钓鱼"),
    ("vulnerability exploitation", "漏洞利用"),
    ("remote services", "远程服务"),
    ("discovery", "发现"),
    ("defense evasion", "防御规避"),
    ("password spraying", "密码喷洒"),
    ("remote tools", "远程工具"),
    ("credential dumping", "凭据转储"),
    ("process injection", "进程注入"),
    ("registry modification", "注册表修改"),
    ("unauthorized account", "未授权账号"),
    ("incident hunting", "事件狩猎"),
    ("file access", "文件访问"),
    ("destructive malware", "破坏性恶意软件"),
    ("living off the land", "LOTL"),
    ("command history", "命令历史"),
    ("tools", "工具"),
    ("impact", "影响"),
    ("rogue VM", "恶意虚拟机"),
    ("certificates", "证书"),
    ("valid cloud credentials", "有效云凭据"),
    ("deletion", "删除"),
    ("cloud logs", "云日志"),
    ("scheduled tasks", "计划任务"),
    ("proxies", "代理"),
    ("registry run key", "注册表 Run Key"),
    ("file sharing", "文件共享"),
    ("email interaction", "邮件交互"),
    ("MSSQL brute force", "MSSQL 暴力破解"),
    ("Office lure", "Office 诱饵"),
    ("failed actions", "失败动作"),
    ("disk encryption", "磁盘加密"),
    ("Exchange exploit", "Exchange 利用"),
)


def source_family(source: str) -> str:
    if source.startswith("CISA"):
        return "CISA 等机构"
    return source


def translate_focus(value: str) -> str:
    translated = value
    for english, chinese in FOCUS_REPLACEMENTS:
        translated = translated.replace(english, chinese)
    return translated


def cell(value: str) -> str:
    return " ".join(value.split()).replace("|", "\\|")


def main() -> None:
    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    rows.sort(key=lambda row: (row["published"], row["title"]), reverse=True)
    rows.sort(
        key=lambda row: {"The DFIR Report": 0, "Unit 42": 1, "CISA 等机构": 2}[
            source_family(row["source"])
        ]
    )

    families = Counter(source_family(row["source"]) for row in rows)
    levels = Counter(row["use_level"] for row in rows)
    years = Counter(row["published"][:4] for row in rows)
    year_summary = "、".join(f"{year} 年 {years[year]} 份" for year in sorted(years))

    lines = [
        "# 公开溯源报告汇总",
        "",
        f"更新时间：{date.today().isoformat()}。本表由 `Public_IR_Reports/manifest.csv` 自动生成，共收录 **{len(rows)} 份**公开溯源与事件响应材料：The DFIR Report {families['The DFIR Report']} 份、Unit 42 {families['Unit 42']} 份、CISA 等机构 {families['CISA 等机构']} 份。",
        "",
        f"质量分级包括 **A 类 {levels['A']} 份**和 **B 类 {levels['B']} 份**。A 类通常具有较完整的时间线和终端证据，优先作为攻击场景种子；B 类包括短文、年度总结、指南或覆盖参考，使用前需要进一步复核。",
        "",
        f"时间覆盖：{year_summary}。报告只提供真实事件语义和证据线索，不应未经验证直接转化为攻击脚本或 Ground Truth。",
        "",
        "| # | 报告 ID | 来源 | 发布日期 | 报告（本地文件） | 级别 | 格式 | 平台 | 场景重点 | 原文 |",
        "|---:|---|---|---|---|:---:|:---:|---|---|:---:|",
    ]

    for index, row in enumerate(rows, start=1):
        local_file = row["normalized_file"] or row["source_file"]
        local_target = f"../Public_IR_Reports/{local_file}"
        title = cell(row["title"])
        local_link = f"[{title}](<{local_target}>)"
        original_link = f"[原文](<{row['source_url']}>)"
        lines.append(
            "| "
            + " | ".join(
                (
                    str(index),
                    cell(row["id"]),
                    cell(row["source"]),
                    cell(row["published"]),
                    local_link,
                    cell(row["use_level"]),
                    cell(row["format"]),
                    cell(row["platform"]),
                    cell(translate_focus(row["scenario_focus"])),
                    original_link,
                )
            )
            + " |"
        )

    lines.extend(
        (
            "",
            "## 维护方式",
            "",
            "报告新增、重新抓取或质量分级发生变化后，先重建 `manifest.csv`，再运行：",
            "",
            "```bash",
            "python3 scripts/build_public_report_summary.py",
            "```",
            "",
            "更详细的文件哈希、验证结果和原始存档路径以 [`manifest.csv`](../Public_IR_Reports/manifest.csv) 为准。",
        )
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} report rows to {OUTPUT}")


if __name__ == "__main__":
    main()
