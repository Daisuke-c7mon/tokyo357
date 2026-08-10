#!/usr/bin/env python3
"""/go/<slug> — App Store へ送り出す中継ページを作る。

    python3 tools/build_go.py

なぜ直リンクではなく中継を挟むのか。

A8 の成果は「広告主のサイト上で成果地点のタグが発火する」ことで計上される。
App Store でのダウンロードは Apple から A8 に通知が飛ばないので、
**ダウンロード自体を成果地点にはできない**。中継ページを自社ドメインに置けば、
そこを成果地点にできる（＝App Store に送り出した時点で計上する形）。

検索結果に出す意味はないので noindex。sitemap にも入れない。
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apps import APPS, store_url  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "go"

PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{name} を App Store で開いています</title>
<link rel="canonical" href="https://tokyo357.com/apps/{slug}">
<meta http-equiv="refresh" content="0; url={url}">
<link rel="stylesheet" href="/assets/style.css?v=20260805">
</head>
<body>
<main id="main" class="doc">
  <div class="wrap">
    <div class="doc-head doc-head--app">
      <img class="doc-icon" src="/assets/icons/{slug}.png" width="512" height="512" alt="">
      <div>
        <p class="updated">APP STORE へ移動しています</p>
        <h1>{name}</h1>
        <p class="lede">自動で App Store に移動します。切り替わらない場合は、
        下のリンクをタップしてください。</p>
        <div class="actions mt-s">
          <a class="btn" href="{url}">App Store を開く</a>
          <a class="btn btn--ghost" href="/apps/{slug}">先に説明を読む</a>
        </div>
      </div>
    </div>
  </div>
</main>

<!-- A8 の成果地点タグはこの下に貼る（管理画面で発行されたものをそのまま） -->
<!-- A8_CONVERSION_TAG -->

<script>location.replace({url_js});</script>
</body>
</html>
"""


def main():
    OUT.mkdir(exist_ok=True)
    n = 0
    for a in APPS:
        if a["state"] != "live":
            continue          # 配信前のアプリに送っても開けない
        url = store_url(a["appid"], "a8")
        (OUT / f'{a["slug"]}.html').write_text(PAGE.format(
            name=a["name"], slug=a["slug"],
            url=url.replace("&", "&amp;"),
            url_js='"' + url + '"'))
        n += 1
        print(f'/go/{a["slug"]:14} → {url}')
    print(f"\n{n}本ぶん作成")


if __name__ == "__main__":
    main()
