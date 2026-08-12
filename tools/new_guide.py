#!/usr/bin/env python3
"""記事（/guides）のガワを作る。本文だけ書けば1本できる状態にするためのもの。

    from new_guide import write_guide
    write_guide(slug=..., title=..., desc=..., lead=..., date=..., topic=...,
                app="sukemaru", pitch="…", body='<h2>…</h2><p>…</p>')

head / footer / アプリ導線 / 関連カードは既存記事と同じものを機械的に付ける。
記事を足したら build_guides.py の GUIDES にも1行足して、build_guides.py を回すこと。
（一覧ページとサイトマップはそちらが面倒をみる）
"""
import html
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apps import BY_SLUG, store_url  # noqa: E402
from build_pages import related_block  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
VER = "20260805"
REF = ROOT / "guides" / "jun-alcohol-keisan.html"


def _shared():
    src = REF.read_text()
    head = src.split('<header class="site-head">')[1].split("</header>")[0]
    foot = src.split('<footer class="site-foot">')[1].split("</footer>")[0]
    return head, foot


def _install(a, pitch):
    """記事の末尾に置くアプリ導線。記事ごとに刺さる一文を pitch で受ける。"""
    url = store_url(a["appid"], "web_guide").replace("&", "&amp;")
    if a["state"] == "live":
        btn = (f'<a class="btn" href="{url}">App Store でダウンロード</a>\n'
               f'          <a class="btn btn--ghost" href="/apps/{a["slug"]}">'
               f'{a["name"]}について読む</a>')
        qr = (f'\n      <div class="install-qr">\n'
              f'        <img src="/assets/qr/{a["slug"]}.png" width="290" height="290"'
              f' alt="{a["name"]} の App Store ページのQRコード" loading="lazy">\n'
              f'        <span>スマートフォンの<br>カメラで読み取る</span>\n'
              f'      </div>')
    else:
        btn = (f'<a class="btn btn--ghost" href="/apps/{a["slug"]}">'
               f'{a["name"]}について読む</a>')
        qr = ""
    return (f'    <section class="install">\n'
            f'      <div>\n'
            f'        <h2>{a["name"]}</h2>\n'
            f'        <p>{pitch}</p>\n'
            f'        <p class="cmp-note">{a["os"]} ／ {a["price"]}</p>\n'
            f'        <div class="actions">\n'
            f'          {btn}\n'
            f'        </div>\n'
            f'      </div>{qr}\n'
            f'    </section>\n')


def write_guide(slug, title, desc, lead, date, topic, app, pitch, body):
    a = BY_SLUG[app]
    head, foot = _shared()
    og = f"https://tokyo357.com/assets/og/{app}.png"
    url = f"https://tokyo357.com/guides/{slug}"
    t = html.escape(title)
    d = html.escape(desc)

    doc = f"""<!DOCTYPE html>
<html lang="ja" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t} ｜ 株式会社サウナ</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#14100E">
<meta property="og:type" content="article">
<meta property="og:site_name" content="株式会社サウナ / Sauna Inc.">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/style.css?v={VER}">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{t}",
  "description": "{d}",
  "inLanguage": "ja",
  "datePublished": "{date}",
  "dateModified": "{date}",
  "image": "{og}",
  "mainEntityOfPage": "{url}",
  "author": {{ "@type": "Organization", "name": "株式会社サウナ", "url": "https://tokyo357.com/" }},
  "publisher": {{ "@type": "Organization", "name": "株式会社サウナ", "url": "https://tokyo357.com/" }}
}}
</script>
</head>
<body>
<a class="skip" href="#main">本文へスキップ</a>

<header class="site-head">{head}</header>

<main id="main" class="doc">
  <div class="wrap">

    <p class="crumb"><a href="/">ホーム</a><span>／</span><a href="/guides/">解決のヒント</a></p>

    <div class="doc-head">
      <p class="updated">{date} ／ {topic}</p>
      <h1>{title}</h1>
      <p class="lede">{lead}</p>
    </div>

    <div class="prose">

{body}

    </div>

{_install(a, pitch)}
{related_block(app)}
  </div>
</main>

<footer class="site-foot">{foot}</footer>
</body>
</html>
"""
    p = ROOT / "guides" / f"{slug}.html"
    p.write_text(doc)
    return p
