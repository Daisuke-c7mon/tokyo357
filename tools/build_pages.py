#!/usr/bin/env python3
"""アプリページに「インストール導線」「他のアプリ」「OG画像」「Smart App Banner」を差し込む。

    python3 tools/build_pages.py

何度実行しても同じ結果になる（既存ブロックを丸ごと置き換える）。
アプリの状態や文言を変えたら tools/apps.py を直してから再実行する。
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apps import APPS, BY_SLUG, store_url  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent

B0, B1 = "<!-- BUILD:install -->", "<!-- /BUILD:install -->"
R0, R1 = "<!-- BUILD:related -->", "<!-- /BUILD:related -->"
H0, H1 = "<!-- BUILD:head -->", "<!-- /BUILD:head -->"


def replace_block(s, start, end, body):
    """マーカーがあれば中身を差し替え、無ければ None を返す。"""
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if pat.search(s):
        return pat.sub(start + body + end, s)
    return None



def rank_badge(slug, compact=False):
    """tools/ranks.json に記録された実測の順位だけを出す。手書きの数字は使わない。"""
    f = ROOT / "tools" / "ranks.json"
    if not f.exists():
        return ""
    import json
    d = json.loads(f.read_text()).get(slug)
    if not d or not d.get("best"):
        return ""
    cls = "rank"
    return (f'<p class="{cls}">App Store {d["genre"]}（{d["kind"]}）'
            f'<b>最高 {d["best"]}位</b>'
            f'<span class="when">{d["best_date"]} 時点</span></p>')


def head_block(a):
    """OG画像・Twitterカード・Smart App Banner。"""
    out = [
        "",
        f'<meta property="og:image" content="https://tokyo357.com/assets/og/{a["slug"]}.png">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    if a["state"] == "live":
        # iOS Safari が純正のインストールバナーをページ上部に出す。無料で最も効く導線。
        out.append(f'<meta name="apple-itunes-app" content="app-id={a["appid"]}">')
    out.append("")
    return "\n".join(out)


def install_block(a):
    url = store_url(a["appid"], "web_app_page").replace("&", "&amp;")
    if a["state"] == "live":
        qr = (f'\n      <div class="install-qr">\n'
              f'        <img src="/assets/qr/{a["slug"]}.png" width="290" height="290"'
              f' alt="{a["name"]} の App Store ページのQRコード" loading="lazy">\n'
              f'        <span>スマートフォンの<br>カメラで読み取る</span>\n'
              f'      </div>')
        body = (f'\n    <section class="install">\n'
                f'      <div>\n'
                f'        <h2>{a["name"]}を使ってみる</h2>\n'
                f'        <p>{a["os"]} ／ {a["price"]}。'
                f'この端末がiPhone・iPadなら、下のボタンから直接 App Store が開きます。</p>\n'
                f'        <div class="actions">\n'
                f'          <a class="btn" href="{url}">App Store でダウンロード</a>\n'
                f'          <a class="btn btn--ghost" href="/support#{a["slug"]}">先に質問を読む</a>\n'
                f'        </div>\n'
                f'      </div>{qr}\n'
                f'    </section>\n  ')
    else:
        state = "審査中です" if a["state"] == "review" else "申請の準備中です"
        body = (f'\n    <section class="install">\n'
                f'      <div>\n'
                f'        <h2>{a["name"]}は現在 App Store {state}</h2>\n'
                f'        <p>{a["os"]} ／ {a["price"]} で公開予定です。'
                f'公開されしだい、このページにダウンロードのリンクを出します。'
                f'先に中身を知りたい方は、上の説明とよくある質問をご覧ください。</p>\n'
                f'        <div class="actions">\n'
                f'          <a class="btn btn--ghost" href="/support#{a["slug"]}">よくある質問</a>\n'
                f'          <a class="btn btn--ghost" href="/apps/">ほかのアプリを見る</a>\n'
                f'        </div>\n'
                f'      </div>\n'
                f'    </section>\n  ')
    return body


def related_block(slug):
    """同じテーマ→公開中を優先して3件。回遊で他アプリのインストールにつなげる。"""
    me = BY_SLUG[slug]
    others = [a for a in APPS if a["slug"] != slug]
    others.sort(key=lambda a: (a["topic"] != me["topic"], a["state"] != "live"))
    picks = others[:3]
    cards = "\n".join(
        f'        <a class="related-card" href="/apps/{a["slug"]}">\n'
        f'          <img src="/assets/icons/{a["slug"]}.png" width="512" height="512" alt="" loading="lazy">\n'
        f'          <div>\n'
        f'            <b>{a["name"]}</b>\n'
        f'            <span>{a["short"]}</span>\n'
        f'            <em>{a["price"]}'
        + ("・配信中" if a["state"] == "live" else "・準備中") +
        f'</em>\n'
        f'          </div>\n'
        f'        </a>'
        for a in picks)
    return (f'\n    <section class="related">\n'
            f'      <h2>ほかにもつくっています</h2>\n'
            f'      <p>どれも同じ考え方で、実際に困っている一点をひとつずつ潰しています。'
            f'<a href="/apps/">アプリ一覧を見る</a></p>\n'
            f'      <div class="related-grid">\n{cards}\n      </div>\n'
            f'    </section>\n  ')



def sync_index_ranks():
    """トップページのカードにも順位を出す（ランクインしているアプリだけ）。"""
    p = ROOT / "index.html"
    s = p.read_text()
    s = re.sub(r'\n *<p class="rank">.*?</p>', "", s, flags=re.S)
    for a in APPS:
        badge = rank_badge(a["slug"])
        if not badge:
            continue
        m = re.search(r'(href="/apps/' + a["slug"] + r'">.*?<h3>[^<]*</h3>\n)', s, re.S)
        if m:
            s = s[:m.end()] + "          " + badge + "\n" + s[m.end():]
    p.write_text(s)
    print("トップのカードに順位を反映")


def main():
    for a in APPS:
        p = ROOT / "apps" / f'{a["slug"]}.html'
        s = p.read_text()

        # --- head ---
        blk = head_block(a)
        new = replace_block(s, H0, H1, blk)
        if new is None:
            anchor = '<link rel="stylesheet" href="/assets/style.css?v='
            i = s.index(anchor)
            j = s.index("\n", i) + 1
            s = s[:j] + H0 + blk + H1 + "\n" + s[j:]
        else:
            s = new

        # --- rank badge（doc-head の lede の直後） ---
        badge = rank_badge(a["slug"])
        s = re.sub(r'\n *<p class="rank">.*?</p>', "", s, flags=re.S)
        if badge:
            m = re.search(r'(<p class="lede">.*?</p>\n)', s, re.S)
            if m:
                indent = "        "
                s = s[:m.end()] + indent + badge + "\n" + s[m.end():]

        # --- install ---
        blk = install_block(a)
        new = replace_block(s, B0, B1, blk)
        if new is None:
            anchor = "    </div>\n  </div>\n</main>"
            assert anchor in s, a["slug"]
            s = s.replace(anchor, "    </div>\n" + B0 + blk + B1 + "\n  </div>\n</main>", 1)
        else:
            s = new

        # --- related ---
        blk = related_block(a["slug"])
        new = replace_block(s, R0, R1, blk)
        if new is None:
            anchor = B1 + "\n  </div>\n</main>"
            s = s.replace(anchor, B1 + "\n" + R0 + blk + R1 + "\n  </div>\n</main>", 1)
        else:
            s = new

        p.write_text(s)
        print("更新:", a["slug"])

    sync_index_ranks()


if __name__ == "__main__":
    main()
