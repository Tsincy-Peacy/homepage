#!/usr/bin/env python3
"""Validate a built MkDocs site without network access or third-party packages."""

from __future__ import annotations

import argparse
from collections import Counter
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urljoin, urlsplit


class Page(HTMLParser):
    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.links: list[tuple[str, int]] = []
        self.tags: Counter[str] = Counter()
        self.lang = ""
        self.feed(source)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.tags[tag] += 1
        if tag == "html":
            self.lang = attributes.get("lang") or ""
        identifier = attributes.get("id")
        if identifier:
            if identifier in self.ids:
                self.duplicate_ids.add(identifier)
            self.ids.add(identifier)
        if tag == "a" and attributes.get("name"):
            self.ids.add(attributes["name"])
        for key in ("href", "src"):
            if attributes.get(key):
                self.links.append((attributes[key], self.getpos()[0]))


def configured_url(project: Path) -> str:
    config = (project / "mkdocs.yml").read_text(encoding="utf-8")
    match = re.search(r"^site_url:\s*['\"]?([^\s'\"]+)", config, re.MULTILINE)
    if not match:
        raise ValueError("mkdocs.yml must contain a site_url, or pass --site-url")
    return match.group(1).rstrip("/") + "/"


def check_site(site: Path, base_url: str) -> list[str]:
    errors: list[str] = []
    site = site.resolve()
    base = urlsplit(base_url)
    prefix = base.path.rstrip("/") + "/"
    pages: dict[Path, Page] = {}

    for file in sorted(site.rglob("*.html")):
        source = file.read_text(encoding="utf-8")
        page = Page(source)
        pages[file] = page
        content = unescape(source)
        if not page.lang.lower().startswith("zh") and "张逸安" in content:
            errors.append(f"{file.relative_to(site)}: pen name is only allowed on Chinese pages")
        if "·" in content:
            errors.append(f"{file.relative_to(site)}: remove middle-dot separators")
        if page.duplicate_ids:
            errors.append(f"{file.relative_to(site)}: duplicate IDs {sorted(page.duplicate_ids)}")

    for file, page in pages.items():
        page_url = urljoin(base_url, file.relative_to(site).as_posix())
        for reference, line in page.links:
            resolved = urlsplit(urljoin(page_url, reference))
            if resolved.scheme not in ("http", "https") or resolved.netloc != base.netloc:
                continue
            path = unquote(resolved.path)
            if path == prefix.rstrip("/"):
                path = ""
            elif path.startswith(prefix):
                path = path[len(prefix):]
            else:
                # Root-relative 404 links also work when the site has no prefix.
                path = path.lstrip("/")
            target = (site / path).resolve()
            if not target.is_relative_to(site):
                errors.append(f"{file.relative_to(site)}:{line}: path escapes site: {reference}")
                continue
            if target.is_dir():
                target /= "index.html"
            if not target.is_file():
                errors.append(f"{file.relative_to(site)}:{line}: missing target: {reference}")
                continue
            fragment = unquote(resolved.fragment)
            if fragment and target.suffix.lower() == ".html":
                target_page = pages.get(target)
                if target_page is None or fragment not in target_page.ids:
                    errors.append(f"{file.relative_to(site)}:{line}: missing anchor: {reference}")

    for relative, language in (("index.html", "en"), ("zh/index.html", "zh-CN")):
        page = pages.get(site / relative)
        if page is None:
            errors.append(f"Missing homepage: {relative}")
            continue
        if page.lang != language:
            errors.append(f"{relative}: expected lang={language!r}, got {page.lang!r}")
        for tag, count in (("main", 1), ("h1", 1)):
            if page.tags[tag] != count:
                errors.append(f"{relative}: expected exactly one <{tag}>")
        if not page.tags["nav"] or not page.tags["header"]:
            errors.append(f"{relative}: missing semantic navigation or header")
        for anchor in ("main-content", "research", "honors", "contact"):
            if anchor not in page.ids:
                errors.append(f"{relative}: missing main section #{anchor}")

    removed_pages = {"vote", "schedule", "glossary", "teaching", "support"}
    removed_images = {
        "香薰.jpg", "护手霜.jpg", "小王子永生花礼盒.jpg", "丝巾.jpg",
        "Digital-Process-Board.png", "STM32F103C8T6.png", "XCOM-config.png",
    }
    for file in site.rglob("*"):
        if not file.is_file():
            continue
        relative = file.relative_to(site)
        if (
            file.suffix.lower() == ".exe"
            or relative.parts[0] in {"games", "sources", "lectures", "vendor", "javascripts", *removed_pages}
            or (len(relative.parts) == 1 and file.stem in removed_pages)
            or file.name in removed_images
        ):
            errors.append(f"Removed content was still published: {relative}")
    return errors


def main() -> int:
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, default=project / "site")
    parser.add_argument("--site-url", help="Override the site_url from mkdocs.yml")
    args = parser.parse_args()
    if not args.site_dir.is_dir():
        parser.error(f"Site directory does not exist: {args.site_dir}; run mkdocs build first")
    try:
        errors = check_site(args.site_dir, args.site_url or configured_url(project))
    except (OSError, ValueError) as error:
        print(f"Site check failed: {error}", file=sys.stderr)
        return 1
    if errors:
        print("Site check failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    count = len(list(args.site_dir.rglob("*.html")))
    print(f"Site check passed: {count} HTML pages; local links, anchors, languages, and content cleanup verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
