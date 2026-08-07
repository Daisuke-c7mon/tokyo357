#!/usr/bin/env python3
"""アプリ一覧 /apps と、記事一覧 /guides を tools/apps.py から生成する。

    python3 tools/build_index_pages.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apps import APPS  # noqa: E402
from build_pages import rank_badge  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
HEAD_NAV = (ROOT / "index.html").read_text().split("<header", 1)[1].split("</header>", 1)[0]
FOOT = "<footer" + (ROOT / "index.html").read_text().split("<footer", 1)[1].split("</footer>", 1)[0] + "</footer>"

SHELL = """<!DOCTYPE html>
<html lang="ja" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://tokyo357.com{path}">
<meta name="theme-color" content="#14100E">
<meta property="og:type" content="website">
<meta property="og:site_name" content="株式会社サウナ / Sauna Inc.">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://tokyo357.com{path}">
<meta property="og:image" content="https://tokyo357.com/assets/og/home.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/style.css?v={ver}">
{ld}</head>
<body>
<a class="skip" href="#main">本文へスキップ</a>

<header{header}</header>

<main id="main" class="doc">
  <div class="wrap">
{body}
  </div>
</main>

{footer}

<script src="/assets/site.js?v={ver}" defer></script>
</body>
</html>
"""

VER = "20260805"

STATE_LABEL = {"live": "配信中", "review": "審査中", "prepare": "準備中"}


def _rank_text(slug):
    import json
    f = ROOT / "tools" / "ranks.json"
    if not f.exists():
        return ""
    d = json.loads(f.read_text()).get(slug)
    if not d or not d.get("best"):
        return ""
    return f'{d["genre"]}{d["kind"]}最高{d["best"]}位' 


def apps_page():
    groups = {}
    for a in APPS:
        groups.setdefault(a["topic"], []).append(a)
    order = ["毎日の記録", "仕事の道具", "画面まわり・気晴らし"]

    out = []
    for topic in order:
        items = groups.get(topic)
        if not items:
            continue
        items = sorted(items, key=lambda a: a["state"] != "live")
        cards = "\n".join(
            f'        <a class="related-card" href="/apps/{a["slug"]}">\n'
            f'          <img src="/assets/icons/{a["slug"]}.png" width="512" height="512" alt="" loading="lazy">\n'
            f'          <div>\n'
            f'            <b>{a["name"]}</b>\n'
            f'            <span>{a["short"]}</span>\n'
            f'            <em>{a["os"]}・{a["price"]}・{STATE_LABEL[a["state"]]}'
            + (f'・{_rank_text(a["slug"])}' if _rank_text(a["slug"]) else '') + '</em>\n'
            f'          </div>\n'
            f'        </a>' for a in items)
        out.append(f'      <h2>{topic}</h2>\n      <div class="related-grid">\n{cards}\n      </div>\n')

    live = sum(1 for a in APPS if a["state"] == "live")
    ld = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "アプリ一覧 ｜ 株式会社サウナ",
  "url": "https://tokyo357.com/apps/",
  "isPartOf": { "@type": "WebSite", "name": "株式会社サウナ", "url": "https://tokyo357.com/" }
}
</script>
"""
    body = f"""    <div class="doc-head">
      <p class="updated">SAUNA INC. ／ APPS</p>
      <h1>アプリ一覧</h1>
      <p class="lede">株式会社サウナが企画・開発した iOS アプリです。現在 {len(APPS)}本（うち {live}本を配信中）。
      どれも、既存アプリの低評価レビューを読み込んで<strong>実際に困っている一点</strong>を見つけ、そこをひとつずつ潰す形で作っています。
      広告は入れず、価格は買い切りに揃えています。</p>
    </div>

    <div class="prose">
{"".join(out)}
      <h2>共通していること</h2>
      <ul>
        <li><strong>買い切り。</strong>月額でも年額でもありません。追加課金もありません。</li>
        <li><strong>広告なし。</strong>広告SDKを入れていないので、ボタンがバナーに隠れることはありません。</li>
        <li><strong>端末の中で完結。</strong>起業おじさん（AIの応答に通信が必要）を除き、通信を行いません。</li>
        <li><strong>アカウント登録なし。</strong>メールアドレスも電話番号も聞きません。</li>
      </ul>

      <h2>サポート</h2>
      <p>使い方や不具合のご相談は<a href="/support">サポートページ</a>から。アプリごとのよくある質問もそこにまとめています。
      個別のご連絡は <a href="mailto:yamaguchi@tokyo357.com">yamaguchi@tokyo357.com</a> へどうぞ。</p>
    </div>
"""
    return SHELL.format(
        title="アプリ一覧 ｜ 株式会社サウナ / Sauna Inc.",
        desc=f"株式会社サウナ（Sauna Inc.）が開発した iOS アプリ {len(APPS)}本の一覧。買い切り・広告なし・端末内で完結。既存アプリの低評価レビューを読み込んで、実際に困っている一点を潰す形で作っています。",
        path="/apps/", ld=ld, header=HEAD_NAV, footer=FOOT, body=body, ver=VER)


def main():
    (ROOT / "apps" / "index.html").write_text(apps_page())
    print("生成: apps/index.html (/apps/)")


if __name__ == "__main__":
    main()
