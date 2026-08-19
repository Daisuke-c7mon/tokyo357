#!/usr/bin/env python3
"""トップページ（index.html）のアプリカードを tools/apps.py に合わせる。

やることは2つだけ。何度実行しても同じ結果になる。

1. apps.py にあってカードが無いアプリを、最後のカードの後ろに追加する
2. 既存カードの `.meta` 末尾の状態表記（App Store 公開中／審査中／準備中）を
   apps.py の state に合わせて書き換える

説明文（<p>）と順位行（<p class="rank">）は手で書いた文章なので触らない。
新規追加のときだけ apps.py の short を入れておく（あとから書き足す前提）。

    python3 tools/sync_index_cards.py
"""
import re
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apps import APPS

INDEX = pathlib.Path(__file__).parent.parent / "index.html"

# state → メタ行の末尾に付ける文字列
SUFFIX = {"live": "App Store 公開中", "review": "審査中", "prepare": "準備中"}
ALL_SUFFIX = tuple(SUFFIX.values())

CARD = """      <a class="work rise mt-l" href="/apps/{slug}">
        <img class="work-icon" src="/assets/icons/{slug}.png" width="512" height="512" alt="{name} のアプリアイコン" loading="lazy" decoding="async">
        <div>
          <p class="meta">{os} · IPHONE / IPAD · {price} · {suffix}</p>
          <h3>{name}</h3>
          <p>{short}</p>
          <span class="go">アプリの詳細とサポート →</span>
        </div>
      </a>

"""


def meta_of(app):
    return f'{app["os"]} · IPHONE / IPAD · {app["price"]} · {SUFFIX[app["state"]]}'


def main():
    s = INDEX.read_text()
    changed = []

    # ── 1. 既存カードの状態表記を合わせる ───────────────────────
    for app in APPS:
        i = s.find(f'href="/apps/{app["slug"]}"')
        if i < 0:
            continue
        m = re.compile(r'<p class="meta">([^<]*)</p>').search(s, i)
        if not m:
            continue
        want = meta_of(app)
        if m.group(1) == want:
            continue
        s = s[:m.start(1)] + want + s[m.end(1):]
        changed.append(f'状態: {app["name"]} → {SUFFIX[app["state"]]}')

    # ── 2. 足りないカードを追加する ─────────────────────────────
    missing = [a for a in APPS if f'href="/apps/{a["slug"]}"' not in s]
    if missing:
        starts = [m.start() for m in re.finditer(r'<a class="work[^"]*" href="/apps/', s)]
        if not starts:
            sys.exit("index.html にアプリカードが1つも無い。手で1枚置いてから実行すること")
        tail = s.find("</a>", starts[-1]) + len("</a>\n\n")
        block = "".join(
            CARD.format(slug=a["slug"], name=a["name"], os=a["os"],
                        price=a["price"], suffix=SUFFIX[a["state"]], short=a["short"])
            for a in missing)
        s = s[:tail] + block + s[tail:]
        changed += [f'追加: {a["name"]}' for a in missing]

    if not changed:
        print("index.html: 変更なし")
        return
    INDEX.write_text(s)
    for c in changed:
        print(" ", c)
    print(f"index.html を更新（{len(changed)}件）")
    if missing:
        print("※ 追加したカードの説明文は apps.py の short をそのまま入れてある。"
              "他のカードに合わせて書き足すこと")


if __name__ == "__main__":
    main()
