#!/usr/bin/env python3
"""sitemap.xml を実際のファイルから作り直す。

    python3 tools/build_sitemap.py

手で書いていると記事を足したときに入れ忘れる。実際にあるHTMLを数えて作る。
lastmod は git の最終コミット日を使う（無ければ今日）。

除外するもの
  404 / Search Console の確認用ファイル … 検索結果に出す意味がない
  affiliate/ … アフィリエイターに配る素材で、検索から来る人には用がない
"""
import datetime
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://tokyo357.com"
TODAY = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

SKIP = {"404.html"}
SKIP_DIRS = {"tools", "assets", "affiliate", "docs", "go"}


def lastmod(p):
    r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(p)],
                       cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() or TODAY


def url_for(p):
    """/apps/sukemaru.html → /apps/sukemaru、index.html → ディレクトリのURL。"""
    rel = p.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[:-len("index.html")]
    return "/" + rel[:-len(".html")]


def priority(u):
    if u == "/":
        return "1.0"
    if u in ("/apps/", "/guides/", "/support"):
        return "0.9"
    if u.startswith("/apps/"):
        return "0.8"
    if u.startswith("/guides/"):
        return "0.7"
    return "0.5"


def main():
    pages = []
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS or rel.name in SKIP:
            continue
        # Search Console の確認用ファイルなど、中身のないものは外す
        if p.stat().st_size < 800:
            continue
        pages.append(p)

    urls = sorted({url_for(p): p for p in pages}.items(),
                  key=lambda kv: (kv[0] != "/", kv[0]))

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, p in urls:
        out += ["  <url>",
                f"    <loc>{BASE}{u}</loc>",
                f"    <lastmod>{lastmod(p)}</lastmod>",
                f"    <priority>{priority(u)}</priority>",
                "  </url>"]
    out.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(out) + "\n")
    print(f"sitemap.xml に {len(urls)} 件")


if __name__ == "__main__":
    main()
