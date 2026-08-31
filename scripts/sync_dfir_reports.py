#!/usr/bin/env python3
"""Synchronize all public reports listed by The DFIR Report.

The official Reports page is backed by the site's WordPress post catalog. This
script archives each canonical report page, generates normalized Markdown, and
downloads an embedded PDF when the public page is only a short landing page.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from extract_public_report import extract


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Public_IR_Reports" / "The_DFIR_Report"
CATALOG = REPORT_DIR / "catalog.json"
API_URL = "https://thedfirreport.com/wp-json/wp/v2/posts?per_page=100&page=1&_fields=date,link,slug,title"
MINIMUM_REPORTS = 97


def curl(url: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "curl",
            "-L",
            "--fail",
            "--silent",
            "--show-error",
            "--retry",
            "3",
            "--max-time",
            "90",
            url,
            "--output",
            str(output),
        ],
        check=True,
    )


def source_url(markdown: Path) -> str:
    for line in markdown.read_text(encoding="utf-8", errors="replace").splitlines()[:20]:
        match = re.match(r'source_url:\s+"(.*)"$', line)
        if match:
            return match.group(1)
    return ""


def embedded_pdf(page: Path) -> str:
    content = page.read_text(encoding="utf-8", errors="replace")
    urls = re.findall(r'https://thedfirreport\.com/wp-content/uploads/[^"<>\s]+?\.pdf(?:\.pdf)?', content)
    return html.unescape(urls[0]) if urls else ""


def declared_word_count(page: Path) -> int:
    """Return the article word count advertised by the page's JSON-LD."""
    content = page.read_text(encoding="utf-8", errors="replace")
    match = re.search(r'"wordCount":\s*(\d+)', content)
    return int(match.group(1)) if match else 0


def restore_markdown_from_rest(post: dict[str, object], page: Path, markdown: Path) -> bool:
    """Recover article text when a canonical page renders without its post body.

    The raw canonical page remains untouched. The REST response is archived next
    to it so the normalized Markdown remains reproducible and auditable.
    """
    declared = declared_word_count(page)
    extracted_words = len(markdown.read_text(encoding="utf-8").split())
    if declared < 800 or extracted_words >= declared * 0.3:
        return False

    rest_archive = page.with_suffix(".rest.json")
    slug = str(post["slug"])
    rest_url = (
        "https://thedfirreport.com/wp-json/wp/v2/posts"
        f"?slug={slug}&_fields=content"
    )
    curl(rest_url, rest_archive)
    records = json.loads(rest_archive.read_text(encoding="utf-8"))
    if len(records) != 1:
        raise ValueError(f"REST recovery returned {len(records)} records for {slug}")
    rendered = records[0].get("content", {}).get("rendered", "")
    if not rendered:
        raise ValueError(f"REST recovery returned no content for {slug}")

    raw_page = page.read_text(encoding="utf-8", errors="replace")
    head = raw_page.split("</head>", 1)[0] + "</head>"
    # The temporary path is outside ``The_DFIR_Report``; use the extractor's
    # generic ``article`` scope so it does not depend on the path name.
    wrapper = f"{head}<body><article>{rendered}</article></body></html>"
    with tempfile.TemporaryDirectory(prefix="dfir-rest-") as temporary:
        temporary_html = Path(temporary) / page.name
        temporary_html.write_text(wrapper, encoding="utf-8")
        recovered = extract(temporary_html)
        recovered_text = recovered.read_text(encoding="utf-8")
    marker = f'source_html: "{page.name}"'
    recovered_text = recovered_text.replace(
        marker,
        marker + f'\nnormalization_source: "{rest_archive.name}"',
        1,
    )
    markdown.write_text(recovered_text, encoding="utf-8")
    recovered_words = len(recovered_text.split())
    if recovered_words < declared * 0.3:
        raise ValueError(
            f"REST recovery for {slug} produced only {recovered_words} words; expected about {declared}"
        )
    print(f"recovered REST article body {markdown.name} ({recovered_words} words)")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    catalog_tmp = CATALOG.with_suffix(".tmp.json")
    curl(API_URL, catalog_tmp)
    posts = json.loads(catalog_tmp.read_text(encoding="utf-8"))
    if len(posts) < MINIMUM_REPORTS:
        raise ValueError(
            f"Expected at least {MINIMUM_REPORTS} public reports, API returned {len(posts)}"
        )
    CATALOG.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    catalog_tmp.unlink()

    archived = {source_url(path) for path in REPORT_DIR.glob("*.md")}
    missing = [post for post in posts if post["link"] not in archived]
    print(f"Official catalog: {len(posts)}; archived: {len(archived)}; missing: {len(missing)}")
    if args.dry_run:
        for post in missing:
            print(post["date"][:10], post["link"])
        return

    downloads: list[tuple[dict[str, object], Path]] = []
    for post in missing:
        filename = f'{post["date"][:10]}_{post["slug"]}.html'
        downloads.append((post, REPORT_DIR / filename))

    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(curl, str(post["link"]), path): (post, path) for post, path in downloads}
        for future in as_completed(futures):
            post, path = futures[future]
            try:
                future.result()
                print(f"downloaded {path.name}")
            except Exception as error:  # noqa: BLE001 - aggregate download failures
                failures.append(f'{post["link"]}: {error}')
    if failures:
        raise RuntimeError("Download failures:\n" + "\n".join(failures))

    embedded_downloads: list[tuple[str, Path]] = []
    for _, page in downloads:
        markdown = extract(page)
        words = len(markdown.read_text(encoding="utf-8").split())
        pdf_url = embedded_pdf(page)
        if words < 800 and pdf_url:
            embedded_downloads.append((pdf_url, page.with_suffix(".pdf")))

    with ThreadPoolExecutor(max_workers=min(args.workers, 4)) as executor:
        futures = {executor.submit(curl, url, path): (url, path) for url, path in embedded_downloads}
        for future in as_completed(futures):
            url, path = futures[future]
            future.result()
            if not path.read_bytes().startswith(b"%PDF"):
                raise ValueError(f"Embedded report is not a PDF: {url}")
            print(f"downloaded embedded PDF {path.name}")

    posts_by_url = {str(post["link"]): post for post in posts}
    for markdown in sorted(REPORT_DIR.glob("*.md")):
        page = markdown.with_suffix(".html")
        post = posts_by_url.get(source_url(markdown))
        if page.exists() and post:
            restore_markdown_from_rest(post, page, markdown)

    final_urls = {source_url(path) for path in REPORT_DIR.glob("*.md")}
    catalog_urls = {str(post["link"]) for post in posts}
    if final_urls != catalog_urls:
        missing_urls = sorted(catalog_urls - final_urls)
        extra_urls = sorted(final_urls - catalog_urls)
        raise ValueError(f"Catalog mismatch; missing={missing_urls}; extra={extra_urls}")
    print(f"Synchronized {len(final_urls)} public DFIR reports")


if __name__ == "__main__":
    main()
