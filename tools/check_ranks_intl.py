#!/usr/bin/env python3
"""国別のカテゴリ順位を取得して記録する。海外KPIの計測基盤。

    python3 tools/check_ranks_intl.py YYYY-MM-DD

日本向けの check_ranks.py と同じ仕組みを、US / GB / DE / FR / AU / CA に広げたもの。
Apple の公開RSSを読むだけで認証は要らない。結果は tools/ranks_intl.json に積み上げる。

**掲載言語が日本語のままの国では、順位を追っても意味がない。**
その国の言語で掲載文を用意してから計測を始めること（docs/intl.md 参照）。
"""
import json
import pathlib
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "ranks_intl.json"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

# 計測する国。日本以外で実際に配信している主要ストア。
STORES = {
    "us": "アメリカ", "gb": "イギリス", "de": "ドイツ",
    "fr": "フランス", "au": "オーストラリア", "ca": "カナダ",
}

# slug: (App ID, ジャンルID, ジャンル表示名, 有料/無料)
TARGETS = {
    "sukemaru":     ("6796656589", "6008", "写真／ビデオ", "paid"),
    "kaeseru":      ("6796657244", "6015", "ファイナンス", "paid"),
    "shimekiri":    ("6796252958", "6007", "仕事効率化", "paid"),
    "shizukatl":    ("6796696394", "6002", "ユーティリティ", "paid"),
    "tsuzukutodo":  ("6796174701", "6007", "仕事効率化", "paid"),
    "kinshuwatch":  ("6795822272", "6013", "ヘルスケア／フィットネス", "paid"),
    "othello":      ("6793739141", "6014", "ゲーム", "free"),
    "kigyouojisan": ("6795361615", "6000", "ビジネス", "free"),
}
KIND = {"paid": "toppaidapplications", "free": "topfreeapplications"}


def chart(store, genre, kind):
    url = (f"https://itunes.apple.com/{store}/rss/{KIND[kind]}"
           f"/limit=200/genre={genre}/json")
    for _ in range(3):
        try:
            d = json.load(urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=30))
            e = d.get("feed", {}).get("entry", [])
            if isinstance(e, dict):
                e = [e]
            return [x.get("id", {}).get("attributes", {}).get("im:id") for x in e]
        except Exception:
            time.sleep(2)
    return []


def main():
    if len(sys.argv) < 2:
        print("日付を引数で渡してください（例: python3 tools/check_ranks_intl.py 2026-08-08）")
        sys.exit(1)
    today = sys.argv[1]

    data = json.loads(OUT.read_text()) if OUT.exists() else {}
    cache = {}
    hits = 0

    for store, store_ja in STORES.items():
        print(f"\n── {store.upper()} {store_ja}")
        for slug, (aid, genre, gname, kind) in TARGETS.items():
            key = (store, genre, kind)
            if key not in cache:
                cache[key] = chart(store, genre, kind)
                time.sleep(0.4)
            ids = cache[key]
            if not ids:
                print(f"  {slug:14} チャート取得失敗")
                continue
            rank = ids.index(aid) + 1 if aid in ids else None

            rec = data.setdefault(slug, {}).setdefault(store, {})
            rec["genre"] = gname
            rec["current"] = rank
            rec["checked"] = today
            if rank is not None and (rec.get("best") is None or rank < rec["best"]):
                rec["best"] = rank
                rec["best_date"] = today
            if rank:
                hits += 1
                print(f"  {slug:14} {gname:14} {rank}位"
                      f'（最高 {rec["best"]}位 / {rec["best_date"]}）')

        if not any(data.get(s, {}).get(store, {}).get("current") for s in TARGETS):
            print("  （ランクインなし）")

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"\nランクイン合計 {hits} 件 / 保存: {OUT.relative_to(ROOT)}")
    if hits == 0:
        print("まだどの国でも200位以内に入っていません。掲載言語の整備が先です（docs/intl.md）。")


if __name__ == "__main__":
    main()
