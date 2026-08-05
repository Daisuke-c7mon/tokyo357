#!/usr/bin/env python3
"""記事（/guides）のヘッダー・フッター・一覧ページを一括で揃える。

    python3 tools/build_guides.py

記事の本文は guides/*.html に直接書く。このスクリプトは共通パーツと一覧だけを面倒みる。
記事を足したら GUIDES に1行足すこと。
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apps import BY_SLUG  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
VER = "20260805"

# 記事の台帳。順番がそのまま一覧の並び。
GUIDES = [
    dict(slug="transparent-png-white", topic="画像・写真", date="2026-08-05",
         title="背景を透過したのに、保存すると白くなる",
         lead="透過したはずのPNGが白く見える現象には、種類の違う3つの原因があります。最も多いのは「写真アプリの表示上の仕様」で、ファイルは壊れていません。",
         app="sukemaru"),
    dict(slug="x-chronological-safari", topic="X・SNSの表示", date="2026-08-05",
         title="X（旧Twitter）のタイムラインを時系列に戻す",
         lead="「フォロー中」を選んでも、しばらくすると「おすすめ」に戻ってしまう。iPhoneのSafariで、表示を自分の側で固定する方法を説明します。",
         app="shizukatl"),
    dict(slug="deadline-daily-quota", topic="習慣・記録", date="2026-08-05",
         title="締切から逆算して、今日やる量を決める",
         lead="「1日◯ページ」を最初に決めても、1日休んだ時点で計画は壊れます。壊れない配分の作り方と、間に合わないと分かったときの3つの選択肢。",
         app="shimekiri"),
]


def shared():
    src = (ROOT / "guides" / "transparent-png-white.html").read_text()
    head = src.split('<header class="site-head">')[1].split("</header>")[0]
    foot = src.split('<footer class="site-foot">')[1].split("</footer>")[0]
    return head, foot


def sync_shared():
    head, foot = shared()
    for p in sorted((ROOT / "guides").glob("*.html")):
        s = p.read_text()
        s = re.sub(r'(<header class="site-head">).*?(</header>)',
                   lambda m: m.group(1) + head + m.group(2), s, flags=re.S)
        s = re.sub(r'(<footer class="site-foot">).*?(</footer>)',
                   lambda m: m.group(1) + foot + m.group(2), s, flags=re.S)
        p.write_text(s)
        print("共通パーツを同期:", p.name)


def index_page():
    head, foot = shared()
    rows = []
    for g in GUIDES:
        a = BY_SLUG[g["app"]]
        rows.append(
            f'      <a class="work rise mt-l" href="/guides/{g["slug"]}">\n'
            f'        <img class="work-icon" src="/assets/icons/{a["slug"]}.png" width="512" height="512"'
            f' alt="" loading="lazy" decoding="async">\n'
            f'        <div>\n'
            f'          <p class="meta">{g["date"]} · {g["topic"]}</p>\n'
            f'          <h3>{g["title"]}</h3>\n'
            f'          <p>{g["lead"]}</p>\n'
            f'          <span class="go">続きを読む →</span>\n'
            f'        </div>\n'
            f'      </a>')
    body = "\n\n".join(rows)

    items = "".join(
        f'    {{ "@type": "ListItem", "position": {i+1}, "url": "https://tokyo357.com/guides/{g["slug"]}" }}'
        + (",\n" if i < len(GUIDES) - 1 else "\n") for i, g in enumerate(GUIDES))

    return f"""<!DOCTYPE html>
<html lang="ja" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>解決のヒント ｜ 株式会社サウナ / Sauna Inc.</title>
<meta name="description" content="iPhoneでよくある「うまくいかない」を、原因から切り分けて説明します。背景透過が白くなる、タイムラインが時系列に戻らない、締切に間に合わないなど。株式会社サウナ（Sauna Inc.）がアプリ開発の過程で調べたことをそのまま公開しています。">
<link rel="canonical" href="https://tokyo357.com/guides/">
<meta name="theme-color" content="#14100E">
<meta property="og:type" content="website">
<meta property="og:site_name" content="株式会社サウナ / Sauna Inc.">
<meta property="og:title" content="解決のヒント ｜ 株式会社サウナ">
<meta property="og:description" content="iPhoneでよくある「うまくいかない」を、原因から切り分けて説明します。">
<meta property="og:url" content="https://tokyo357.com/guides/">
<meta property="og:image" content="https://tokyo357.com/assets/og/home.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/style.css?v={VER}">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "解決のヒント",
  "url": "https://tokyo357.com/guides/",
  "itemListElement": [
{items}  ]
}}
</script>
</head>
<body>
<a class="skip" href="#main">本文へスキップ</a>

<header class="site-head">{head}</header>

<main id="main" class="doc">
  <div class="wrap">

    <div class="doc-head">
      <p class="updated">SAUNA INC. ／ GUIDES</p>
      <h1>解決のヒント</h1>
      <p class="lede">アプリを作るとき、私たちはまず既存アプリの低評価レビューを読み込んで、
      利用者が実際にどこで詰まっているかを数えます。そこで分かったことは、アプリを使う人だけでなく、
      同じ問題で困っている人すべてに役立つはずです。調べたことをそのまま公開しています。</p>
    </div>

{body}

  </div>
</main>

<footer class="site-foot">{foot}</footer>

<script src="/assets/site.js?v={VER}" defer></script>
</body>
</html>
"""


def main():
    sync_shared()
    (ROOT / "guides" / "index.html").write_text(index_page())
    print("生成: guides/index.html (/guides/)")


if __name__ == "__main__":
    main()
