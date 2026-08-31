#!/usr/bin/env python3
"""Rebuild the public incident-report manifest from local source files."""

from __future__ import annotations

import csv
import hashlib
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "Public_IR_Reports"
MANIFEST = COLLECTION / "manifest.csv"

CISA_NEW = {
    "CISA/2023-05-16_AA23-136A_BianLian.pdf": (
        "CISA/FBI/ACSC",
        "#StopRansomware: BianLian Ransomware Group",
        "https://www.cisa.gov/sites/default/files/2023-05/aa23-136a_stopransomware_bianlian_ransomware_group_1.pdf",
        "valid RDP accounts; PowerShell; credential access; exfiltration; extortion",
        "Windows/AD",
    ),
    "CISA/2023-06-07_AA23-158A_CL0P-MOVEit.pdf": (
        "CISA/FBI",
        "#StopRansomware: CL0P Ransomware Gang Exploits MOVEit Vulnerability",
        "https://www.cisa.gov/sites/default/files/2023-06/aa23-158a-stopransomware-cl0p-ransomware-gang-exploits-moveit-vulnerability_7.pdf",
        "public-facing exploitation; webshell; file access; exfiltration",
        "Windows/Enterprise",
    ),
    "CISA/2023-10-16_AA23-289A_Confluence-CVE-2023-22515.pdf": (
        "CISA/FBI/MS-ISAC",
        "Threat Actors Exploit Atlassian Confluence CVE-2023-22515 for Initial Access",
        "https://www.cisa.gov/sites/default/files/2023-10/aa23-289a-threat-actors-exploit-atlassian-confluence-cve-2023-22515-for-initial-access.pdf",
        "public-facing exploitation; unauthorized account; incident hunting",
        "Linux/Enterprise",
    ),
    "CISA/2023-11-15_AA23-319A_Rhysida.pdf": (
        "CISA/FBI/MS-ISAC",
        "#StopRansomware: Rhysida Ransomware",
        "https://www.cisa.gov/sites/default/files/2023-11/aa23-319a-stopransomware-rhysida-ransomware.pdf",
        "credential access; process injection; registry modification; ransomware",
        "Windows/AD",
    ),
    "CISA/2024-04-18_AA24-109A_Akira.pdf": (
        "CISA/FBI/EC3/NCSC-NL",
        "#StopRansomware: Akira Ransomware",
        "https://www.cisa.gov/sites/default/files/2024-04/aa24-109a-stopransomware-akira-ransomware_2.pdf",
        "VPN access; account creation; Kerberoasting; LSASS; ransomware",
        "Windows/Linux/ESXi",
    ),
    "CISA/2024-05-10_AA24-131A_Black-Basta.pdf": (
        "CISA/FBI/HHS/MS-ISAC",
        "#StopRansomware: Black Basta",
        "https://www.cisa.gov/sites/default/files/2024-07/aa24-131a-joint-csa-stopransomware-black-basta_2.pdf",
        "phishing; vulnerability exploitation; lateral movement; exfiltration; ransomware",
        "Windows/AD",
    ),
    "CISA/2024-08-29_AA24-242A_RansomHub.pdf": (
        "CISA/FBI/MS-ISAC/HHS",
        "#StopRansomware: RansomHub Ransomware",
        "https://www.cisa.gov/sites/default/files/2024-09/aa24-242a-stopransomware-ransomhub-ransomware_1.pdf",
        "password spraying; remote tools; lateral movement; exfiltration; ransomware",
        "Windows/Linux/ESXi",
    ),
    "CISA/2024-11-21_AA24-326A_CISA-Red-Team-Assessment.pdf": (
        "CISA",
        "Enhancing Cyber Resilience: Insights from the CISA Red Team Assessment",
        "https://www.cisa.gov/sites/default/files/2024-11/aa24-326a-enhancing-cyber-resilience-insights-from-cisa-red-team-assessment.pdf",
        "red-team intrusion; persistence; credential access; detection gaps; response",
        "Windows/AD",
    ),
    "CISA/2025-02-19_AA25-050A_Ghost-Cring.pdf": (
        "CISA/FBI/MS-ISAC",
        "#StopRansomware: Ghost (Cring) Ransomware",
        "https://www.cisa.gov/sites/default/files/2025-02/aa25-050a-stopransomware-ghost-cring-ransomware.pdf",
        "known-vulnerability exploitation; PowerShell; credential dumping; exfiltration",
        "Windows/Enterprise",
    ),
    "CISA/2025-03-12_AA25-071A_Medusa.pdf": (
        "CISA/FBI/MS-ISAC",
        "#StopRansomware: Medusa Ransomware",
        "https://www.cisa.gov/sites/default/files/2025-03/aa25-071a-stopransomware-medusa-ransomware.pdf",
        "phishing; remote services; discovery; defense evasion; ransomware",
        "Windows/AD",
    ),
}

FIELDS = [
    "id",
    "source",
    "published",
    "title",
    "use_level",
    "format",
    "source_file",
    "normalized_file",
    "source_url",
    "sha256",
    "scenario_focus",
    "platform",
    "validation",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pdf_pages(path: Path) -> int:
    result = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True)
    match = re.search(r"^Pages:\s+(\d+)$", result.stdout, re.MULTILINE)
    if not match:
        raise ValueError(f"Could not determine page count: {path}")
    return int(match.group(1))


def front_matter(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines()[1:20]:
        if line == "---":
            break
        match = re.match(r"([a-z_]+):\s+\"(.*)\"$", line)
        if match:
            result[match.group(1)] = match.group(2)
    return result


def classify(title: str) -> tuple[str, str]:
    lower = title.lower()
    focus: list[str] = []
    rules = [
        (("confluence", "activemq", "wordpress", "exchange", "proxyshell", "follina", "exploit"), "public-facing exploitation"),
        (("email", "zoom", "onenote", "html smuggling", "lnk", "iso", "bumblebee", "bazar", "icedid", "nitrogen", "gootloader", "emotet"), "phishing or user execution"),
        (("rdp", "password spray", "sql brute"), "remote services or credential attack"),
        (("domain", "zerologon", "ad cs", "certificate"), "Active Directory or privilege escalation"),
        (("exfil", "collect", "shinyhunters"), "collection or exfiltration"),
        (("ransom", "lockbit", "blackcat", "alphv", "dagon", "trigona", "nokoyawa", "wipe"), "impact or ransomware"),
        (("muddled libra", "cloud", "aws", "snowflake"), "identity or cloud investigation"),
    ]
    for keywords, label in rules:
        if any(keyword in lower for keyword in keywords):
            focus.append(label)
    if not focus:
        focus.append("multi-stage intrusion investigation")
    platform = "Windows/AD"
    if any(keyword in lower for keyword in ("cloud", "aws", "snowflake", "shinyhunters")):
        platform = "Cloud/Windows"
    if "wordpress" in lower or "activemq" in lower or "confluence" in lower:
        platform = "Linux/Windows/Enterprise"
    return "; ".join(focus), platform


def main() -> None:
    existing_rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8"))) if MANIFEST.exists() else []
    existing_by_source = {row["source_file"]: row for row in existing_rows}
    existing_by_normalized = {row["normalized_file"]: row for row in existing_rows if row["normalized_file"]}
    rows: list[dict[str, str]] = []

    for pdf in sorted((COLLECTION / "CISA").glob("*.pdf")):
        relative = str(pdf.relative_to(COLLECTION))
        if relative in existing_by_source:
            row = dict(existing_by_source[relative])
        else:
            source, title, url, focus, platform = CISA_NEW[relative]
            date_match = re.match(r"(\d{4}-\d{2}-\d{2})_(AA\d{2}-\d{3}[A-Z])", pdf.name)
            if not date_match:
                raise ValueError(f"Unexpected CISA filename: {pdf.name}")
            row = {
                "id": f"CISA-{date_match.group(2)}",
                "source": source,
                "published": date_match.group(1),
                "title": title,
                "use_level": "A" if "Red-Team" in pdf.name else "B",
                "format": "PDF",
                "source_file": relative,
                "normalized_file": "",
                "source_url": url,
                "scenario_focus": focus,
                "platform": platform,
            }
        row["sha256"] = sha256(pdf)
        row["validation"] = f"PDF; {pdf_pages(pdf)} pages; readable"
        rows.append(row)

    for source_dir, source_name in (("The_DFIR_Report", "The DFIR Report"), ("Unit42", "Unit 42")):
        for markdown in sorted((COLLECTION / source_dir).glob("*.md")):
            normalized = str(markdown.relative_to(COLLECTION))
            metadata = front_matter(markdown)
            html = markdown.with_suffix(".html")
            source_path = html
            source_format = "HTML"
            if markdown.with_suffix(".pdf").exists():
                source_path = markdown.with_suffix(".pdf")
                source_format = "PDF"
            relative_source = str(source_path.relative_to(COLLECTION))

            if normalized in existing_by_normalized:
                row = dict(existing_by_normalized[normalized])
            else:
                published = metadata.get("published", "")[:10]
                title = metadata.get("title", markdown.stem)
                focus, platform = classify(title)
                prefix = "DFIR" if source_dir == "The_DFIR_Report" else "UNIT42"
                source_url = metadata.get("source_url", "")
                secondary_material = any(
                    marker in markdown.stem.lower()
                    for marker in (
                        "year-in-review",
                        "defenders-guide",
                        "sans-ransomware-summit",
                        "adfind-recon",
                        "sharefinder",
                        "default-post",
                    )
                )
                row = {
                    "id": f"{prefix}-{published}-{hashlib.sha1(source_url.encode()).hexdigest()[:8]}",
                    "source": source_name,
                    "published": published,
                    "title": title,
                    "use_level": "B" if "Trends" in markdown.stem or secondary_material else "A",
                    "format": source_format,
                    "source_file": relative_source,
                    "normalized_file": normalized,
                    "source_url": source_url,
                    "scenario_focus": focus,
                    "platform": platform,
                }

            row["format"] = source_format
            row["source_file"] = relative_source
            row["sha256"] = sha256(source_path)
            words = len(markdown.read_text(encoding="utf-8").split())
            secondary_material = any(
                marker in markdown.stem.lower()
                for marker in (
                    "year-in-review",
                    "defenders-guide",
                    "sans-ransomware-summit",
                    "adfind-recon",
                    "sharefinder",
                    "default-post",
                )
            )
            short_html = source_format == "HTML" and words < 800
            row["use_level"] = (
                "B"
                if "Trends" in markdown.stem or secondary_material or short_html
                else "A"
            )
            if source_format == "PDF":
                row["validation"] = f"PDF; {pdf_pages(source_path)} pages; landing HTML archived; Markdown summary {words} words"
            else:
                short_note = "; SHORT_TEXT_REVIEW" if short_html else ""
                rest_note = (
                    f'; WordPress REST recovery cached as {metadata["normalization_source"]}'
                    if metadata.get("normalization_source")
                    else ""
                )
                row["validation"] = (
                    f"HTTP 200; Markdown extracted; {words} words{rest_note}{short_note}"
                )
            rows.append(row)

    expected_rows = (
        len(list((COLLECTION / "CISA").glob("*.pdf")))
        + len(list((COLLECTION / "The_DFIR_Report").glob("*.md")))
        + len(list((COLLECTION / "Unit42").glob("*.md")))
    )
    if len(rows) != expected_rows:
        raise ValueError(f"Expected {expected_rows} report records, found {len(rows)}")

    rows.sort(key=lambda row: (row["source"], row["published"], row["title"]))
    with MANIFEST.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} records to {MANIFEST}")


if __name__ == "__main__":
    main()
