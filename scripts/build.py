"""Validate approved static content, then assemble a full Pages release."""
import html
import json
import os
import re
import shutil
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DIST = ROOT / "dist"

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href", "src") and value:
                self.links.append(value)

def build():
    dashboards = json.loads((ROOT / "dashboards.json").read_text(encoding="utf-8"))
    if not isinstance(dashboards, list) or not dashboards:
        raise ValueError("Registry must contain at least one dashboard")
    seen = set()
    for item in dashboards:
        ident = item["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ident) or ident in seen:
            raise ValueError("Invalid or duplicate dashboard ID")
        seen.add(ident)
        if not item.get("title"):
            raise ValueError("Dashboard title is required")
        stamp = datetime.fromisoformat(item["source_updated_at"].replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("Source timestamp must include a timezone")
        if not (SITE / "dashboards" / ident / "index.html").is_file():
            raise ValueError("Dashboard entry file is missing: " + ident)
    allowed = {".html", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico", ".woff", ".woff2"}
    for path in SITE.rglob("*"):
        if path.is_symlink():
            raise ValueError("Links are not allowed in site content")
        if path.is_file() and path.suffix.lower() not in allowed:
            raise ValueError("Unapproved output file type: " + path.name)
    # Build only after registry validation. Local dist is disposable generated output.
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SITE, DIST)
    build_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    commit = os.environ.get("GITHUB_SHA", "local-preview")
    cards = []
    for item in dashboards:
        cards.append('<article class="card"><h2><a href="dashboards/' + item["id"] + '/">' + html.escape(item["title"]) + '</a></h2><p>' + html.escape(item.get("description", "")) + '</p><p>Source updated: ' + html.escape(item["source_updated_at"]) + '</p></article>')
    index = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Live Dashboard Hub</title><link rel="stylesheet" href="assets/style.css"></head><body><main><header><p class="eyebrow">Live Dashboard Hub</p><h1>Your dashboards.<br>One place.</h1><p>Open a dashboard below. Every update is published to the same permanent link.</p><span class="badge">Public dashboards</span></header><section class="grid" aria-label="Available dashboards">' + "".join(cards) + '</section><footer>Published build: {{BUILD_TIME}} · Version <code>{{COMMIT}}</code><p>Currently showing synthetic demonstration content.</p></footer></main></body></html>'
    (DIST / "index.html").write_text(index, encoding="utf-8")
    (DIST / ".nojekyll").touch()
    for path in DIST.rglob("*.html"):
        text = path.read_text(encoding="utf-8").replace("{{BUILD_TIME}}", html.escape(build_time)).replace("{{COMMIT}}", html.escape(commit))
        path.write_text(text, encoding="utf-8")
        parser = Links()
        parser.feed(text)
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                raise ValueError("External links/assets require review: " + link)
            if not url.path:
                continue
            if url.path.startswith("/"):
                raise ValueError("Use relative paths for project Pages: " + link)
            target = (path.parent / unquote(url.path)).resolve()
            if not target.is_relative_to(DIST.resolve()):
                raise ValueError("Link escapes site: " + link)
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                raise ValueError("Missing local link target: " + link)
    print("Validated and built " + str(len(dashboards)) + " dashboard(s).")

if __name__ == "__main__":
    build()
