#!/usr/bin/env python3
"""A8.net に広告主として出稿するための素材を、アプリごとに生成する。

    python3 tools/build_affiliate.py

出力先は affiliate/<slug>/ で、中身は
  banner-*.png … 日本のアフィリエイトで標準的なサイズのバナー
  text.md       … テキスト広告（文字数つき）
  info.md       … 案件情報（提携先に見せる訴求点・注意点）

バナーは Chrome のヘッドレスでHTMLを撮る。OG画像（build_assets.py）と同じやり方で、
外部サービスにも追加ライブラリにも依存しない。

素材に価格を必ず入れているのは、景品表示法の観点。アフィリエイターが貼った広告の
表示責任は広告主（＝当社）にあるので、有料アプリを無料と誤解させる余地を残さない。
"""
import base64
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apps import APPS, store_url  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = ROOT / "affiliate"

# (幅, 高さ, レイアウト, アイコン寸法, アプリ名の級数, 説明の級数, 説明を出すか)
SIZES = [
    (300, 250, "stack",  84, 24, 13, True),
    (728,  90, "row",    62, 24, 14, True),
    (468,  60, "row",    40, 17, 11, True),
    (160, 600, "stack", 110, 26, 15, True),
    (320, 100, "row",    56, 19, 12, True),
    (200, 200, "stack",  70, 19, 12, True),
    (120,  60, "row",    36, 12, 10, False),
]

HEAD = """<!doctype html><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{w}px;height:{h}px;overflow:hidden}}
body{{background:#14100E;color:#EADDC7;position:relative;
  font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif;
  border:1px solid rgba(234,221,199,.14)}}
body::after{{content:"";position:absolute;left:50%;bottom:-62%;
  width:{glow}px;height:{glow}px;transform:translateX(-50%);border-radius:50%;
  background:radial-gradient(circle,rgba(228,87,46,.26) 0%,rgba(242,181,68,.08) 36%,transparent 66%)}}
img{{border-radius:22.37%;flex:none;
  box-shadow:0 0 0 1px rgba(234,221,199,.14),0 6px 18px rgba(0,0,0,.5)}}
.name{{font-weight:700;letter-spacing:.02em;line-height:1.2;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.desc{{color:#A2957F;line-height:1.45}}
.cta{{background:#E4572E;color:#14100E;font-weight:700;letter-spacing:.04em;
  border-radius:999px;white-space:nowrap;text-align:center}}
.price{{font-family:ui-monospace,Menlo,monospace;letter-spacing:.06em;
  color:#6E6355;white-space:nowrap}}
"""

# 横型： [アイコン][名前・説明・価格][ボタン]
# 縦に積むと帯の高さを超えて文字が切れるので、ボタンは横に並べる。
ROW = HEAD + """
.in{{position:relative;z-index:2;height:100%;display:flex;align-items:center;
  gap:{gap}px;padding:{pad}px}}
img{{width:{ic}px;height:{ic}px}}
.t{{flex:1;min-width:0}}
.name{{font-size:{ns}px;white-space:{wrap}}}
.desc{{font-size:{ds}px;margin-top:3px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.price{{font-size:{ps}px;margin-top:3px}}
.cta{{flex:none;font-size:{cs}px;padding:{cpv}px {cph}px}}
</style>
<div class="in">
  <img src="data:image/png;base64,{icon}">
  <div class="t"><div class="name">{name}</div>{desc}{price}</div>
  {cta}
</div>
"""

# 縦型・正方形： 中央に積む
STACK = HEAD + """
.in{{position:relative;z-index:2;height:100%;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:{gap}px;padding:{pad}px;
  text-align:center}}
.in>img.icon{{width:{ic}px;height:{ic}px}}
.name{{font-size:{ns}px;max-width:100%}}
/* 説明は行数で頭打ちにする。溢れると上下が切れて名前まで消える */
.desc{{font-size:{ds}px;max-width:100%;overflow:hidden;
  display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:{lines}}}
.price{{font-size:{ps}px}}
.cta{{font-size:{cs}px;padding:{cpv}px {cph}px}}
/* 縦長は余白が空くので、実際の画面を下に覗かせる */
.shot{{margin-top:auto;width:100%;border-radius:10px 10px 0 0;
  box-shadow:0 0 0 1px rgba(234,221,199,.14);margin-bottom:{shotgap}px}}
</style>
<div class="in">
  <img class="icon" src="data:image/png;base64,{icon}">
  <div class="name">{name}</div>
  {desc}{cta}{price}{shot}
</div>
"""


def banner_html(a, icon_b64, w, h, layout, ic, ns, ds, show_desc, shot_b64=None):
    tall = h >= 400
    common = dict(w=w, h=h, glow=max(w, h) * 2, icon=icon_b64,
                  ic=ic, ns=ns, ds=ds, ps=max(9, ds - 1),
                  cs=max(10, ds), name=a["name"])

    if layout == "row":
        # 高さ60pxの帯に3行は入らない。説明を落として名前と価格だけにする。
        room = h >= 80
        # ボタンを置くと文字の幅が足りなくなる。468px以上のときだけ出す。
        big = w >= 468
        return ROW.format(
            gap=10 if h < 70 else 14, pad=8 if h < 70 else 12,
            cpv=6, cph=14, wrap="normal" if w < 200 else "nowrap",
            desc=f'<div class="desc">{a["short"]}</div>' if (show_desc and room) else "",
            price=f'<div class="price">{a["price"]}</div>' if show_desc else "",
            cta=('<div class="cta">App Store で見る</div>' if big else ""),
            **common)

    # 正方形の小さいもの（200x200）は説明まで入れると名前が押し出される
    room = h >= 250
    shot = (f'<img class="shot" src="data:image/jpeg;base64,{shot_b64}">'
            if (tall and shot_b64) else "")
    return STACK.format(
        gap=10 if tall else 8, pad=16,
        cpv=7 if tall else 5, cph=18 if tall else 14,
        lines=5 if tall else 3,
        shotgap=-int(h * 0.18) if shot else 0,
        desc=f'<div class="desc">{a["short"]}</div>' if (show_desc and room) else "",
        cta=('<div class="cta">App Store で見る</div>' if show_desc else ""),
        price=f'<div class="price">{a["price"]}</div>' if show_desc else "",
        shot=shot,
        **common)


def shoot(html, png, w, h):
    tmp = OUT / "_tmp.html"
    tmp.write_text(html)
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
         f"--screenshot={png}", f"--window-size={w},{h}",
         "--default-background-color=00000000", f"file://{tmp}"],
        capture_output=True)
    tmp.unlink(missing_ok=True)


def text_ads(a):
    """テキスト広告。A8の入稿欄は全角で数えるので、文字数を併記しておく。"""
    url = store_url(a["appid"], "a8_text")
    rows = [
        ("見出し（短）", a["name"]),
        ("見出し（中）", f'{a["name"]}｜{a["tagline"]}'),
        ("説明（1行）", a["short"]),
        ("説明（2行）", f'{a["short"]}{a["price"]}。広告なし。'),
    ]
    body = "\n".join(f"| {k} | {v} | {len(v)} |" for k, v in rows)
    return (f'# {a["name"]}｜テキスト広告\n\n'
            f"そのまま A8 の管理画面に貼れる形にしています。\n"
            f"文字数は全角・半角を区別せずに数えた文字数です。\n\n"
            f"| 用途 | 文面 | 文字数 |\n|---|---|---|\n{body}\n\n"
            f"## リンク先\n\n`{url}`\n\n"
            f"`ct=` はキャンペーン識別子です。A8 経由の流入を App Analytics で\n"
            f"切り分けるために付けています。**外さないでください。**\n")


def info(a):
    url = store_url(a["appid"], "a8_text")
    state = {"live": "配信中", "review": "審査中",
             "prepare": "申請準備中"}[a["state"]]
    return (f'# {a["name"]}｜案件情報\n\n'
            f"| 項目 | 内容 |\n|---|---|\n"
            f'| アプリ名 | {a["name"]} |\n'
            f'| 状態 | App Store {state} |\n'
            f'| 価格 | {a["price"]} |\n'
            f'| 対応 | {a["os"]} |\n'
            f'| 紹介ページ | https://tokyo357.com/apps/{a["slug"]} |\n'
            f"| App Store | {url} |\n"
            f'| 提供 | 株式会社サウナ（Sauna Inc.） |\n\n'
            f"## 何をするアプリか\n\n{a['tagline']}\n\n{a['short']}\n\n"
            f"## 紹介するときに書いてよいこと\n\n"
            f'- 価格は「{a["price"]}」。ここを省いて無料と読めるようにしないでください\n'
            f"- 広告は入っていません\n"
            f"- 実際の画面は https://tokyo357.com/apps/{a['slug']} に載せています。\n"
            f"  そこから引用してかまいません\n\n"
            f"## 書かないでほしいこと\n\n"
            f"- 「1位」「No.1」などの順位表記。順位は日々変わるうえ、\n"
            f"  根拠を示せない表示は景品表示法上のリスクになります\n"
            f"- 効果や結果の断定（「必ず〜できる」「絶対に〜」）\n"
            f"- 他社アプリを名指しでけなす表現。比較はしてかまいませんが、\n"
            f"  事実にもとづいた書き方にしてください\n")


def main():
    OUT.mkdir(exist_ok=True)
    made = 0
    for a in APPS:
        icon = ROOT / "assets" / "icons" / f'{a["slug"]}.png'
        if not icon.exists():
            print(f'{a["name"]:14} アイコンなし。とばします')
            continue
        b64 = base64.b64encode(icon.read_bytes()).decode()
        shot = ROOT / "assets" / "shots" / a["slug"] / "01.jpg"
        sb64 = base64.b64encode(shot.read_bytes()).decode() if shot.exists() else None
        d = OUT / a["slug"]
        d.mkdir(exist_ok=True)
        for w, h, layout, ic, ns, ds, show in SIZES:
            png = d / f"banner-{w}x{h}.png"
            shoot(banner_html(a, b64, w, h, layout, ic, ns, ds, show, sb64), png, w, h)
            made += 1
        (d / "text.md").write_text(text_ads(a))
        (d / "info.md").write_text(info(a))
        print(f'{a["name"]:14} バナー{len(SIZES)}点 + text.md + info.md')
    print(f"\nバナー合計 {made}点 → {OUT}")


if __name__ == "__main__":
    main()
