#!/usr/bin/env python3
"""比較記事の materials を Apple の公開APIから集める。

    python3 tools/research_rivals.py

比較記事は実在の他社アプリを名指しするので、**憶測を書かない**ことが絶対条件。
ここで取れるのは Apple が公開している事実（名前・開発元・価格・評価・評価数・
最終更新・対応OS）だけで、記事にはこの範囲しか書かない。
広告の有無や課金の中身はAPIから取れないため、特定アプリについては断定しない。

出力: tools/rivals.json
"""
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

# 各アプリの「戦っている検索語」。ここから実際の上位アプリを引く。
QUERIES = {
    "kinshuwatch":   ["禁酒", "断酒", "禁酒 カウンター"],
    "tsuzukutodo":   ["習慣化", "習慣 記録", "ルーティン"],
    "shimekiri":     ["締切 管理", "執筆 進捗", "読書 ペース"],
    "sukemaru":      ["背景透過", "背景 消しゴム", "透過 png"],
    "kaeseru":       ["住宅ローン 計算", "ローン シミュレーション", "繰上返済"],
    "sagaseru":      ["ボイスメモ 文字起こし", "録音 文字起こし", "議事録"],
    "hitoriinvoice": ["請求書 作成", "見積書", "インボイス 請求書"],
    "shizukatl":     ["safari 拡張 広告", "タイムライン 時系列", "sns 制限"],
    "othello":       ["オセロ", "リバーシ"],
    "kigyouojisan":  ["起業 相談", "副業 独立", "事業計画"],
}

OURS = {"6796696394", "6796656589", "6796657244", "6796545639", "6796195340",
        "6796174701", "6796252958", "6795822272", "6795361615", "6793739141",
        "880950896", "6796174961"}


def get(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=25))
        except Exception as e:
            if attempt == 2:
                print("  取得失敗:", e, file=sys.stderr)
                return None
            time.sleep(2)


def search(term, limit=12):
    q = urllib.parse.urlencode({"term": term, "country": "jp", "media": "software",
                                "entity": "software", "limit": limit, "lang": "ja_jp"})
    d = get("https://itunes.apple.com/search?" + q)
    return d.get("results", []) if d else []


def slim(r):
    return dict(
        id=str(r.get("trackId")),
        name=r.get("trackName"),
        seller=r.get("sellerName") or r.get("artistName"),
        price=r.get("formattedPrice"),
        price_num=r.get("price"),
        rating=round(r.get("averageUserRating"), 2) if r.get("averageUserRating") else None,
        ratings=r.get("userRatingCount") or 0,
        rating_current=round(r.get("averageUserRatingForCurrentVersion"), 2)
        if r.get("averageUserRatingForCurrentVersion") else None,
        updated=(r.get("currentVersionReleaseDate") or "")[:10],
        version=r.get("version"),
        min_os=r.get("minimumOsVersion"),
        size_mb=round(int(r.get("fileSizeBytes", 0)) / 1024 / 1024) if r.get("fileSizeBytes") else None,
        genres=r.get("genres"),
        url=(r.get("trackViewUrl") or "").split("?")[0],
        advisory=r.get("contentAdvisoryRating"),
    )


def main():
    out = {}
    for slug, terms in QUERIES.items():
        seen, rivals = set(), []
        for t in terms:
            for r in search(t):
                tid = str(r.get("trackId"))
                if tid in OURS or tid in seen:
                    continue
                if not r.get("userRatingCount"):      # 評価ゼロは比較対象にしない
                    continue
                seen.add(tid)
                rivals.append(slim(r))
            time.sleep(0.6)
        # 評価数の多い順＝実際に使われている順
        rivals.sort(key=lambda x: x["ratings"], reverse=True)
        out[slug] = rivals[:8]
        top = ", ".join(f'{x["name"][:18]}({x["ratings"]})' for x in rivals[:4])
        print(f'{slug:14} {len(rivals)}件  上位: {top}')

    (ROOT / "tools" / "rivals.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2))
    print("\n保存: tools/rivals.json")


if __name__ == "__main__":
    main()
