#!/usr/bin/env python3
"""比較記事を生成する。

    python3 tools/build_compare.py

競合の価格・評価・評価数は **実行時に Apple の lookup API から取り直す**。
古い数字を載せないため、記事には取得日を明記する。
API から取れない事柄（広告の量、課金の中身）は書かない。
"""
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apps import BY_SLUG, store_url  # noqa: E402
from compare_data import COMPARE  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
VER = "20260805"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
TODAY = "2026-08-05"


def lookup(ids):
    q = urllib.parse.urlencode({"id": ",".join(ids), "country": "jp", "lang": "ja_jp"})
    req = urllib.request.Request("https://itunes.apple.com/lookup?" + q, headers=UA)
    d = json.load(urllib.request.urlopen(req, timeout=25))
    return {str(r["trackId"]): r for r in d.get("results", []) if r.get("trackId")}


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def shared():
    src = (ROOT / "guides" / "transparent-png-white.html").read_text()
    head = src.split('<header class="site-head">')[1].split("</header>")[0]
    foot = src.split('<footer class="site-foot">')[1].split("</footer>")[0]
    return head, foot


def table(mine, rows, cfg):
    """比較表。自社は最後に置き、色を変える。"""
    tr = []
    for r, _blurb in rows:
        rating = f'★{r["averageUserRating"]:.2f}' if r.get("averageUserRating") else "—"
        cnt = f'{r.get("userRatingCount", 0):,}' if r.get("userRatingCount") else "—"
        tr.append(
            f'          <tr>\n'
            f'            <th>{esc(r["trackName"])}</th>\n'
            f'            <td class="num">{esc(r.get("formattedPrice") or "—")}</td>\n'
            f'            <td class="num">{rating}</td>\n'
            f'            <td class="num">{cnt}</td>\n'
            f'            <td>{esc(r.get("sellerName") or r.get("artistName"))}</td>\n'
            f'          </tr>')
    tr.append(
        f'          <tr class="me">\n'
        f'            <th>{mine["name"]}（この記事の書き手）</th>\n'
        f'            <td class="num">{mine["price"]}</td>\n'
        f'            <td class="num">—</td>\n'
        f'            <td class="num">—</td>\n'
        f'            <td>株式会社サウナ</td>\n'
        f'          </tr>')
    return (
        '      <div class="cmp-wrap">\n'
        '        <table class="cmp">\n'
        '          <thead><tr><th>アプリ</th><th>価格</th><th>評価</th><th>評価数</th><th>開発元</th></tr></thead>\n'
        '          <tbody>\n' + "\n".join(tr) + "\n          </tbody>\n"
        "        </table>\n      </div>\n"
        f'      <p class="cmp-note">価格・評価・評価数は日本のApp Storeで {TODAY} に取得した数値です。'
        f'変動するため、購入前に必ずApp Storeでご確認ください。'
        f'当社のアプリは評価が集まる前のため、評価欄は「—」としています。'
        f'なお広告の量やアプリ内課金の内容は公開APIから取得できないため、'
        f'他社アプリについてはこの記事では触れていません。</p>\n')


def article(slug, cfg, data):
    mine = BY_SLUG[slug]
    head, foot = shared()

    rows = []
    for rid, blurb in cfg["rivals"]:
        r = data.get(rid)
        if not r:
            print(f"  取得できず除外: {rid}")
            continue
        rows.append((r, blurb))

    crit = "\n".join(
        f'        <li><strong>{c[0]}</strong> — {c[1]}</li>' for c in cfg["criteria"])

    rivals_html = []
    for r, blurb in rows:
        rating = f'★{r["averageUserRating"]:.2f}（{r.get("userRatingCount", 0):,}件）' \
            if r.get("averageUserRating") else "評価未集計"
        rivals_html.append(
            f'      <div class="rival">\n'
            f'        <h3>{esc(r["trackName"])}</h3>\n'
            f'        <p class="fact">{esc(r.get("sellerName") or r.get("artistName"))}'
            f' ／ {esc(r.get("formattedPrice") or "—")} ／ {rating}'
            f' ／ iOS {esc(r.get("minimumOsVersion"))} 以降</p>\n'
            f'        <p>{blurb}</p>\n'
            f'        <p><a href="{esc(r["trackViewUrl"].split("?")[0])}">App Store で見る</a></p>\n'
            f'      </div>')

    live = mine["state"] == "live"
    if live:
        url = store_url(mine["appid"], "web_compare").replace("&", "&amp;")
        cta_btns = (f'          <a class="btn" href="{url}">App Store でダウンロード</a>\n'
                    f'          <a class="btn btn--ghost" href="/apps/{slug}">アプリの詳細を見る</a>')
        qr = (f'      <div class="install-qr">\n'
              f'        <img src="/assets/qr/{slug}.png" width="290" height="290"'
              f' alt="{mine["name"]} の App Store ページのQRコード" loading="lazy">\n'
              f'        <span>スマートフォンの<br>カメラで読み取る</span>\n'
              f'      </div>\n')
        state_note = ""
    else:
        cta_btns = (f'          <a class="btn btn--ghost" href="/apps/{slug}">アプリの詳細を見る</a>\n'
                    f'          <a class="btn btn--ghost" href="/support#{slug}">よくある質問</a>')
        qr = ""
        state_note = "（現在 App Store 審査中です）"

    return f"""<!DOCTYPE html>
<html lang="ja" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{cfg["title"]} ｜ 株式会社サウナ</title>
<meta name="description" content="{cfg["desc"]}">
<link rel="canonical" href="https://tokyo357.com/guides/{cfg["slug"]}">
<meta name="theme-color" content="#14100E">
<meta property="og:type" content="article">
<meta property="og:site_name" content="株式会社サウナ / Sauna Inc.">
<meta property="og:title" content="{cfg["title"]}">
<meta property="og:description" content="{cfg["desc"][:110]}">
<meta property="og:url" content="https://tokyo357.com/guides/{cfg["slug"]}">
<meta property="og:image" content="https://tokyo357.com/assets/og/{slug}.png">
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
  "headline": "{cfg["title"]}",
  "description": "{cfg["desc"][:180]}",
  "inLanguage": "ja",
  "datePublished": "{TODAY}",
  "dateModified": "{TODAY}",
  "image": "https://tokyo357.com/assets/og/{slug}.png",
  "mainEntityOfPage": "https://tokyo357.com/guides/{cfg["slug"]}",
  "author": {{ "@type": "Organization", "name": "株式会社サウナ", "url": "https://tokyo357.com/" }},
  "publisher": {{ "@type": "Organization", "name": "株式会社サウナ", "url": "https://tokyo357.com/" }}
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{ "@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://tokyo357.com/" }},
    {{ "@type": "ListItem", "position": 2, "name": "解決のヒント", "item": "https://tokyo357.com/guides/" }},
    {{ "@type": "ListItem", "position": 3, "name": "{cfg["title"]}" }}
  ]
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
      <p class="updated">{TODAY} ／ {cfg["topic"]} ／ 比較</p>
      <h1>{cfg["title"]}</h1>
      <p class="lede">{cfg["lead"]}</p>
    </div>

    <div class="prose">

      <div class="answer">
        <p class="k">この記事について</p>
        <p>この記事は<strong>{mine["name"]}{state_note}を作っている株式会社サウナが書いています</strong>。自社アプリを含む比較なので、そのつもりで読んでください。
        他社アプリについては、Apple が公開している事実（価格・評価・評価数・開発元）のみを記載し、推測は書いていません。
        どのアプリにも向き不向きがあり、下に挙げたアプリはいずれもこの分野で実際に多く使われているものです。</p>
      </div>

      <h2>先に比較表</h2>
{table(mine, rows, cfg)}
      <h2>選ぶときに見るところ</h2>
      <ul>
{crit}
      </ul>

      <h2>それぞれのアプリについて</h2>
{chr(10).join(rivals_html)}

      <h2>{mine["name"]}（当社）</h2>
{cfg["mine"]}

      <h2>まとめ</h2>
      <p>ここに挙げたアプリは、どれもこの分野で実際に使われているものです。評価数の多さは、それだけ多くの人が使い続けている証拠でもあります。
      無料で始められるものが多いので、まず試してみるのが確実です。</p>
      <p>そのうえで、<strong>広告に触れずに使いたい</strong>、<strong>月額を払い続けたくない</strong>、<strong>データを端末の外に出したくない</strong>——
      このどれかが当てはまるなら、買い切りのアプリを検討する価値があります。当社のアプリはその考え方で作っています。</p>

    </div>

    <section class="install">
      <div>
        <h2>{mine["name"]}について</h2>
        <p>{mine["os"]} ／ {mine["price"]}。{mine["short"]}</p>
        <div class="actions">
{cta_btns}
        </div>
      </div>
{qr}    </section>

  </div>
</main>

<footer class="site-foot">{foot}</footer>

<script src="/assets/site.js?v={VER}" defer></script>
</body>
</html>
"""


def main():
    ids = sorted({rid for cfg in COMPARE.values() for rid, _ in cfg["rivals"]})
    data = {}
    for i in range(0, len(ids), 10):
        data.update(lookup(ids[i:i + 10]))
        time.sleep(0.5)
    print(f"競合データ取得: {len(data)}/{len(ids)}件\n")

    for slug, cfg in COMPARE.items():
        (ROOT / "guides" / f'{cfg["slug"]}.html').write_text(article(slug, cfg, data))
        print(f'生成: guides/{cfg["slug"]}.html  ({BY_SLUG[slug]["name"]})')


if __name__ == "__main__":
    main()
