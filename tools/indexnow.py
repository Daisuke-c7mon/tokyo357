#!/usr/bin/env python3
"""sitemap.xml のURLを IndexNow に送る。Bing・Yandex・Naver・Seznam が即時に取りに来る。

Google は IndexNow に対応していないので、Google 向けは Search Console 側の仕事。
こちらは無料・認証不要・完全自動で回せる分だけを回す。

鍵はサイト直下の <key>.txt で証明する（中身は鍵そのもの）。鍵を変えるとファイル名も
変わるので、KEY は固定のままにすること。

    python3 tools/indexnow.py            # 送るURLの確認だけ
    python3 tools/indexnow.py send       # 実際に送信
"""
import json
import pathlib
import re
import sys
import urllib.request
import urllib.error

ROOT = pathlib.Path(__file__).parent.parent
HOST = "tokyo357.com"
KEY = "c1a912f8cdc751f1539ac52399902cc40916d508713e8b2ae3e7fc34fc43e70a"
ENDPOINT = "https://api.indexnow.org/indexnow"


def urls():
    s = (ROOT / "sitemap.xml").read_text()
    return re.findall(r"<loc>([^<]+)</loc>", s)


def main():
    us = urls()
    keyfile = ROOT / f"{KEY}.txt"
    if not keyfile.exists() or keyfile.read_text().strip() != KEY:
        sys.exit(f"鍵ファイル {keyfile.name} が無い、または中身が鍵と一致しない")
    if len(sys.argv) < 2 or sys.argv[1] != "send":
        print(f"{len(us)} 件を送る予定（先頭3件）")
        for u in us[:3]:
            print("  ", u)
        print(f"鍵ファイル: https://{HOST}/{KEY}.txt")
        print("実行するには `python3 tools/indexnow.py send`")
        return 0

    body = {"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": us}
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        res = urllib.request.urlopen(req, timeout=40)
        print(f"IndexNow: {res.status} — {len(us)} 件を送信した")
        # 200=受理 202=受理（鍵の検証待ち）
        return 0
    except urllib.error.HTTPError as e:
        print(f"IndexNow: {e.code} {e.read().decode()[:300]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
