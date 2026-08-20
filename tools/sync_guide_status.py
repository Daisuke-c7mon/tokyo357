#!/usr/bin/env python3
"""guides/*.html 内の「アプリの公開状態」表記を tools/apps.py に合わせ直す。

アプリが live になったあとも、記事本文の install セクションが
「審査中です」のままダウンロードボタンを出さない、related-card の
バッジが「準備中」のまま、という取り残しが起きる（apps/*.html は
build_pages.py が毎回上書きするため起きないが、guides/*.html の
install セクションは記事ごとの手書きのため取り残る）。

    python3 tools/sync_guide_status.py

何度実行しても同じ結果になる。
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apps import APPS, BY_SLUG, store_url  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
GUIDES = ROOT / "guides"

STATUS_LABEL = {"live": "配信中", "review": "審査中", "prepare": "準備中"}


def fix_related_cards(s):
    """related-card の <em>価格・状態</em> を現在の状態に合わせる。"""
    def repl(m):
        slug = m.group("slug")
        a = BY_SLUG.get(slug)
        if not a:
            return m.group(0)
        return (m.group("pre") + a["price"] + "・" + STATUS_LABEL[a["state"]]
                + m.group("post"))

    pattern = re.compile(
        r'(?P<pre><a class="related-card" href="/apps/(?P<slug>[\w-]+)">.*?<em>)'
        r'[^<]*'
        r'(?P<post></em>)',
        re.S)
    return pattern.sub(repl, s)


def fix_install_section(s, path):
    """記事が紹介している自社アプリが live なのに、install セクションが
    まだ「審査中・準備中」の文言とダウンロードできないボタンのままなら、
    実際にダウンロードできる形に差し替える。"""
    changed = False
    for a in APPS:
        if a["state"] != "live":
            continue
        cmp_note = re.search(
            r'<p class="cmp-note">' + re.escape(a["name"])
            + r'は現在 App Store [^<]*</p>\s*',
            s)
        if not cmp_note:
            continue
        # cmp-note の直後にある actions ブロック（アプリ詳細＋よくある質問の2つの
        # btn--ghost）を、ダウンロードボタン＋QRに差し替える。
        actions_pat = re.compile(
            r'<div class="actions">\s*'
            r'<a class="btn btn--ghost" href="/apps/' + re.escape(a["slug"]) + r'">[^<]*</a>\s*'
            r'<a class="btn btn--ghost" href="[^"]*">[^<]*</a>\s*'
            r'</div>\s*</div>',
            re.S)
        m = actions_pat.search(s)
        if not m:
            print(f"  警告: {path.name} の {a['slug']} 用 actions ブロックが見つからず、cmp-noteのみ除去できませんでした", file=sys.stderr)
            continue
        url = store_url(a["appid"], "web_guide").replace("&", "&amp;")
        new_actions = (
            f'<div class="actions">\n'
            f'          <a class="btn" href="{url}">App Store でダウンロード</a>\n'
            f'          <a class="btn btn--ghost" href="/apps/{a["slug"]}">アプリの詳細を見る</a>\n'
            f'        </div>\n'
            f'      </div>\n'
            f'      <div class="install-qr">\n'
            f'        <img src="/assets/qr/{a["slug"]}.png" width="290" height="290"'
            f' alt="{a["name"]} の App Store ページのQRコード" loading="lazy">\n'
            f'        <span>スマートフォンの<br>カメラで読み取る</span>\n'
            f'      </div>')
        s = s[:cmp_note.start()] + s[cmp_note.end():]
        # cmp_note を除去した後、actions_pat を再検索して置換
        m2 = actions_pat.search(s)
        if m2:
            s = s[:m2.start()] + new_actions + s[m2.end():]
            changed = True
    return s, changed


def main():
    total_related = 0
    total_install = 0
    for p in sorted(GUIDES.glob("*.html")):
        if p.name == "index.html":
            continue
        s = p.read_text()
        orig = s
        s = fix_related_cards(s)
        if s != orig:
            total_related += 1
        s, changed = fix_install_section(s, p)
        if changed:
            total_install += 1
        if s != orig:
            p.write_text(s)
            print("更新:", p.name)
    print(f"\nrelated-card 修正: {total_related} 件 / install セクション修正: {total_install} 件")


if __name__ == "__main__":
    main()
