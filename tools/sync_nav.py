#!/usr/bin/env python3
"""全ページのヘッダーナビとフッターナビを揃える。

    python3 tools/sync_nav.py

ページを足したらここを直して回す。手で全ファイルを編集しないこと。
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apps import APPS  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent

NAV = """
      <a href="/apps/">アプリ</a>
      <a href="/guides/">解決のヒント</a>
      <a href="/#build" class="opt">事業</a>
      <a href="/support">サポート</a>
    """

FOOT = ["""        <a href="/">ホーム</a>
        <a href="/apps/">アプリ一覧</a>
        <a href="/guides/">解決のヒント</a>"""]
FOOT += [f'        <a href="/apps/{a["slug"]}">{a["name"]}</a>' for a in APPS]
FOOT += ["""        <a href="/support">サポート</a>
        <a href="/privacy">プライバシーポリシー</a>
        <a href="/terms">利用規約</a>"""]
FOOT = "\n".join(FOOT)


def main():
    files = sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("apps/*.html")) + sorted(ROOT.glob("guides/*.html"))
    for p in files:
        s = p.read_text()
        o = s
        s = re.sub(r'(<nav class="nav" aria-label="サイト内">).*?(</nav>)',
                   lambda m: m.group(1) + NAV + m.group(2), s, flags=re.S)
        s = re.sub(r'(<nav class="foot-nav" aria-label="フッター">\n).*?(\n      </nav>)',
                   lambda m: m.group(1) + FOOT + m.group(2), s, flags=re.S)
        if s != o:
            p.write_text(s)
            print("ナビを同期:", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
