#!/usr/bin/env python3
"""Extract readable Markdown from archived public incident-report HTML pages.

The extractor intentionally uses only Python's standard library so the report
collection can be reproduced without installing additional packages.
"""

from __future__ import annotations

import argparse
import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path


BLOCK_TAGS = {
    "article",
    "blockquote",
    "div",
    "figure",
    "figcaption",
    "p",
    "section",
    "table",
    "tr",
}
SKIP_TAGS = {"aside", "button", "form", "nav", "noscript", "script", "style", "svg"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class ReportHTMLParser(HTMLParser):
    def __init__(self, source_name: str) -> None:
        super().__init__(convert_charrefs=True)
        self.source_name = source_name
        self.meta: dict[str, str] = {}
        self.canonical_url = ""
        self.scope_depth = 0
        self.skip_depth = 0
        self.parts: list[str] = []

    @staticmethod
    def _attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {key: value or "" for key, value in attrs}

    def _starts_scope(self, tag: str, attrs: dict[str, str]) -> bool:
        classes = set(attrs.get("class", "").split())
        if "The_DFIR_Report" in self.source_name:
            return tag == "div" and "content-column" in classes
        if "Unit42" in self.source_name:
            return tag == "div" and "be__contents-wrapper" in classes
        return tag == "article"

    def _newline(self, count: int = 1) -> None:
        self.parts.append("\n" * count)

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = self._attrs(attrs_list)

        if tag == "meta":
            key = attrs.get("property") or attrs.get("name")
            value = attrs.get("content", "").strip()
            if key and value:
                self.meta[key] = value
        elif tag == "link" and attrs.get("rel") == "canonical":
            self.canonical_url = attrs.get("href", "")

        if not self.scope_depth and self._starts_scope(tag, attrs):
            self.scope_depth = 1
        elif self.scope_depth and tag not in VOID_TAGS:
            self.scope_depth += 1

        if not self.scope_depth:
            return

        if tag in SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return

        if re.fullmatch(r"h[1-6]", tag):
            self._newline(2)
            self.parts.append("#" * int(tag[1]) + " ")
        elif tag == "li":
            self._newline()
            self.parts.append("- ")
        elif tag == "br":
            self._newline()
        elif tag in {"td", "th"}:
            self.parts.append(" | ")
        elif tag in BLOCK_TAGS:
            self._newline(2 if tag in {"article", "section"} else 1)

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_TAGS:
            return
        if not self.scope_depth:
            return

        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        elif not self.skip_depth and (tag in BLOCK_TAGS or tag in {"li", "br"} or re.fullmatch(r"h[1-6]", tag)):
            self._newline()

        self.scope_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.scope_depth or self.skip_depth:
            return
        text = re.sub(r"\s+", " ", data).strip()
        if not text:
            return
        if self.parts and not self.parts[-1].endswith(("\n", " ")):
            self.parts.append(" ")
        self.parts.append(text)

    def markdown(self, source_html: Path) -> str:
        title = self.meta.get("og:title") or self.meta.get("twitter:title") or source_html.stem
        published = self.meta.get("article:published_time") or self.meta.get("date") or ""
        author = self.meta.get("author", "")
        source_url = self.canonical_url or self.meta.get("og:url", "")

        body = "".join(self.parts)
        body = re.sub(r"[ \t]+\n", "\n", body)
        body = re.sub(r"\n[ \t]+", "\n", body)
        body = re.sub(r"\n{3,}", "\n\n", body).strip()

        front_matter = [
            "---",
            f'title: "{title.replace(chr(34), chr(39))}"',
            f'source_url: "{source_url}"',
            f'published: "{published}"',
            f'author: "{author.replace(chr(34), chr(39))}"',
            f'archived_at: "{date.today().isoformat()}"',
            f'source_html: "{source_html.name}"',
            "---",
            "",
            f"# {title}",
            "",
        ]
        return "\n".join(front_matter) + body + "\n"


def extract(path: Path) -> Path:
    parser = ReportHTMLParser(str(path))
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    output = path.with_suffix(".md")
    output.write_text(parser.markdown(path), encoding="utf-8")
    return output


def main() -> None:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("paths", nargs="+", type=Path)
    args = argument_parser.parse_args()
    for path in args.paths:
        print(extract(path))


if __name__ == "__main__":
    main()
