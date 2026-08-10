#!/usr/bin/env python3
"""各アプリのApp Store用スクリーンショットを、サイト掲載用に取り込む。

    python3 tools/build_shots.py

App Store に出しているものと同じ画像を使う。サイト用に別途作らないのは、
掲載内容が食い違うと「サイトで見たものと違う」が起きるため。

元画像は 1290x2796 などの実寸なので、幅640pxに縮めて assets/shots/<slug>/ に置く。
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "shots"

# slug: (リポジトリ, 日本語iPhone用スクショの置き場を探す手がかり)
SOURCES = {
    "sukemaru":     ("sukemaru", ["iphone-ja", "ja/iphone", "store/iphone"]),
    "kaeseru":      ("kaeseru", ["iphone-ja", "ja/iphone", "store/iphone"]),
    "kinshuwatch":  ("kinshu-watch", ["iphone", "store"]),
    # シメキリ逆算は store/ が日本語版。raw/ を先に拾わないよう明示する
    "shimekiri":    ("shimekiri-gyakusan", ["screenshots/store/", "iphone-ja"]),
    "shizukatl":    ("shizuka-tl", ["iphone-ja", "ja/iphone", "store/iphone"]),
    "tsuzukutodo":  ("tsuzuku-todo", ["iphone-ja", "ja/iphone", "store/iphone"]),
    "othello":      ("othello", ["iphone", "store"]),
    "kigyouojisan": ("kigyou-ojisan", ["iphone", "store", "screenshots"]),
}

HOME = pathlib.Path.home()


def find_shots(repo, hints):
    base = HOME / repo
    if not base.exists():
        return []
    cands = [p for p in base.rglob("*.png") if "screenshot" in str(p).lower()]
    # iPad は除く。日本語があれば優先する。
    cands = [p for p in cands if "ipad" not in p.name.lower() and "ipad" not in str(p.parent).lower()]
    for h in hints:
        hit = [p for p in cands if h in str(p).replace("\\", "/")]
        if hit:
            cands = hit
            break
    # 数字の接頭辞で並ぶようにする（1_, 01_ など）
    def key(p):
        m = re.match(r"(\d+)", p.name)
        return (int(m.group(1)) if m else 999, p.name)
    return sorted(set(cands), key=key)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for slug, (repo, hints) in SOURCES.items():
        shots = find_shots(repo, hints)[:6]
        if not shots:
            print(f"{slug:14} スクショが見つかりません")
            continue
        d = OUT / slug
        d.mkdir(parents=True, exist_ok=True)
        for old in list(d.glob("*.png")) + list(d.glob("*.jpg")):
            old.unlink()
        n = 0
        for i, src in enumerate(shots, 1):
            dst = d / f"{i:02d}.jpg"
            # 表示幅は約300px。倍密度ディスプレイ向けに640pxで持つ。
            r = subprocess.run(["sips", "-s", "format", "jpeg",
                                "-s", "formatOptions", "78", "-Z", "640",
                                str(src), "--out", str(dst)],
                               capture_output=True)
            if r.returncode == 0 and dst.exists():
                n += 1
        kb = sum(p.stat().st_size for p in d.glob("*.jpg")) // 1024
        print(f"{slug:14} {n}枚 {kb:4}KB  ← {shots[0].parent.relative_to(HOME)}")
        total += n
    print(f"\n合計 {total}枚")


if __name__ == "__main__":
    main()
