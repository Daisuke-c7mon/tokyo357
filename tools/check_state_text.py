#!/usr/bin/env python3
"""公開中アプリのページに「審査中／準備中」の書き残しが無いかを機械的に確かめる。

`apps/*.html` の BUILD ブロックは build_pages.py が毎回上書きするので安全だが、
その外側の手書き本文は誰も同期しない。2026-08-20 に4本、2026-08-21 に3本で
live 後も「現在 App Store の審査中です」が残っていた。同じ取りこぼしを繰り返さない。

    python3 tools/check_state_text.py      # 問題があれば終了コード 1
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apps import BY_SLUG

ROOT = pathlib.Path(__file__).parent.parent
# live のページに出てはいけない言い回し（関連カードの「・準備中」は別アプリの話なので除く）
BAD = ["審査中です", "審査に出しています", "申請の準備中です", "申請中です", "公開されたらこのページからリンクします"]


def main():
    bad = []
    for f in sorted((ROOT / "apps").glob("*.html")):
        app = BY_SLUG.get(f.stem)
        if not app or app["state"] != "live":
            continue
        s = f.read_text()
        for phrase in BAD:
            for m in re.finditer(re.escape(phrase), s):
                line = s[:m.start()].count("\n") + 1
                bad.append(f'{f.relative_to(ROOT)}:{line} 公開中なのに「{phrase}」が残っている')
    if bad:
        print("\n".join(bad))
        print(f"\n{len(bad)} 件。apps.py を live にしたあと、本文の手書き部分を直すこと。")
        return 1
    print("状態の書き残し: なし")
    return 0


if __name__ == "__main__":
    sys.exit(main())
