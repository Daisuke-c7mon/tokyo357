#!/usr/bin/env python3
"""OG画像（1200x630）とQRコードを生成する。

    python3 tools/build_assets.py

OG画像は Chrome のヘッドレスでHTMLを撮る（外部サービス・追加ライブラリ不要）。
QRは qrcode パッケージを使い、生成物はリポジトリにコミットする＝実行時の依存はゼロ。
"""
import base64
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apps import APPS, store_url  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OG_DIR = ROOT / "assets" / "og"
QR_DIR = ROOT / "assets" / "qr"

CARD = """<!doctype html><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1200px;height:630px;background:#14100E;color:#EADDC7;overflow:hidden;
  font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN",sans-serif;position:relative}}
body::after{{content:"";position:absolute;left:50%;bottom:-58%;width:1100px;height:1100px;
  transform:translateX(-50%);border-radius:50%;
  background:radial-gradient(circle,rgba(228,87,46,.22) 0%,rgba(242,181,68,.08) 34%,transparent 66%)}}
.in{{position:relative;z-index:2;height:100%;display:flex;align-items:center;gap:64px;padding:0 88px}}
img{{width:260px;height:260px;border-radius:22.37%;flex:none;
  box-shadow:0 0 0 1px rgba(234,221,199,.14),0 24px 60px rgba(0,0,0,.5)}}
.t{{flex:1;min-width:0}}
.mark{{font-family:ui-monospace,Menlo,monospace;font-size:20px;letter-spacing:.22em;color:#E4572E;margin-bottom:22px}}
h1{{font-family:"Yu Mincho",YuMincho,"Hiragino Mincho ProN",serif;font-size:76px;
  line-height:1.15;letter-spacing:.04em;margin-bottom:22px}}
p{{font-size:30px;line-height:1.6;color:#A2957F}}
.meta{{position:absolute;left:88px;bottom:52px;z-index:2;
  font-family:ui-monospace,Menlo,monospace;font-size:19px;letter-spacing:.14em;color:#6E6355}}
</style>
<div class="in">
  <img src="data:image/png;base64,{icon}">
  <div class="t"><p class="mark">SAUNA INC.</p><h1>{name}</h1><p>{tagline}</p></div>
</div>
<div class="meta">{meta}</div>
"""

HOME = """<!doctype html><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1200px;height:630px;background:#14100E;color:#EADDC7;overflow:hidden;
  font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN",sans-serif;position:relative}
body::after{content:"";position:absolute;left:50%;bottom:-58%;width:1100px;height:1100px;
  transform:translateX(-50%);border-radius:50%;
  background:radial-gradient(circle,rgba(228,87,46,.24) 0%,rgba(242,181,68,.08) 34%,transparent 66%)}
.in{position:relative;z-index:2;height:100%;display:flex;flex-direction:column;
  justify-content:center;padding:0 96px}
.mark{font-family:ui-monospace,Menlo,monospace;font-size:21px;letter-spacing:.24em;color:#E4572E;margin-bottom:30px}
h1{font-family:"Yu Mincho",YuMincho,"Hiragino Mincho ProN",serif;font-size:104px;
  line-height:1.14;letter-spacing:.05em;margin-bottom:28px}
h1 span{color:#7FB0C0}
p{font-size:31px;line-height:1.6;color:#A2957F}
.meta{position:absolute;left:96px;bottom:56px;z-index:2;
  font-family:ui-monospace,Menlo,monospace;font-size:19px;letter-spacing:.14em;color:#6E6355}
</style>
<div class="in">
  <p class="mark">TOKYO 357 ／ 港区浜松町 ／ SINCE 2020</p>
  <h1>熱をつくる。<br><span>ととのえる。</span></h1>
  <p>株式会社サウナ ｜ iOSアプリ開発とITコンサルティング</p>
</div>
<div class="meta">TOKYO357.COM</div>
"""


def shoot(html: str, out: pathlib.Path):
    tmp = ROOT / "_ogtmp.html"
    tmp.write_text(html, encoding="utf-8")
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         "--window-size=1200,630", "--virtual-time-budget=3000",
         f"--screenshot={out}", f"file://{tmp}"],
        capture_output=True, check=True)
    tmp.unlink()


def main():
    OG_DIR.mkdir(parents=True, exist_ok=True)
    QR_DIR.mkdir(parents=True, exist_ok=True)

    shoot(HOME, OG_DIR / "home.png")
    print("OG: home.png")

    label = {"live": "App Store で配信中", "review": "App Store 審査中", "prepare": "まもなく公開"}
    for a in APPS:
        icon = base64.b64encode((ROOT / "assets" / "icons" / f"{a['slug']}.png").read_bytes()).decode()
        meta = f"{a['os']} ・ {a['price']} ・ {label[a['state']]}"
        shoot(CARD.format(icon=icon, name=a["name"], tagline=a["tagline"], meta=meta),
              OG_DIR / f"{a['slug']}.png")
        print("OG:", a["slug"])

    import qrcode
    from qrcode.image.styledpil import StyledPilImage  # noqa: F401  (存在確認)
    for a in APPS:
        if a["state"] != "live":
            continue
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                           box_size=10, border=2)
        qr.add_data(store_url(a["appid"], "web_qr"))
        qr.make(fit=True)
        img = qr.make_image(fill_color="#14100E", back_color="#EADDC7")
        img.save(QR_DIR / f"{a['slug']}.png")
        print("QR:", a["slug"])


if __name__ == "__main__":
    main()
