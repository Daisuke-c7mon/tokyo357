#!/usr/bin/env python3
"""App Store のカテゴリ別ランキングを取得し、最高順位を記録する。

    python3 tools/check_ranks.py [YYYY-MM-DD]

Apple が公開している RSS を読むだけで、認証は要らない。毎日走らせると
tools/ranks.json に「今日の順位」と「これまでの最高順位」が積み上がる。

サイトに順位を出すのは事実の掲示なので、**必ずこのスクリプトが取得した値だけ**を使う。
手で数字を書かないこと。ランク外になった日は current を null にし、最高順位は
「いつ時点のものか」を添えて残す。
"""
import json
import pathlib
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "ranks.json"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

# slug: (App ID, ジャンルID, ジャンル表示名, 有料/無料)
TARGETS = {
    "kaeseru":      ("6796657244", "6015", "ファイナンス", "paid"),
    "kinshuwatch":  ("6795822272", "6013", "ヘルスケア／フィットネス", "paid"),
    "sukemaru":     ("6796656589", "6008", "写真／ビデオ", "paid"),
    "shizukatl":    ("6796696394", "6002", "ユーティリティ", "paid"),
    "tsuzukutodo":  ("6796174701", "6007", "仕事効率化", "paid"),
    "shimekiri":    ("6796252958", "6007", "仕事効率化", "paid"),
    "hitoriinvoice": ("6796195340", "6000", "ビジネス", "paid"),
    "sagaseru":     ("6796545639", "6007", "仕事効率化", "paid"),
    "kigyouojisan": ("6795361615", "6000", "ビジネス", "free"),
    "othello":      ("6793739141", "6014", "ゲーム", "free"),
}
KIND = {"paid": "toppaidapplications", "free": "topfreeapplications"}
LABEL = {"paid": "有料App", "free": "無料App"}


class FetchFailed(Exception):
    pass


def chart(genre, kind):
    url = (f"https://itunes.apple.com/jp/rss/{KIND[kind]}"
           f"/limit=200/genre={genre}/json")
    last_err = None
    for _ in range(3):
        try:
            d = json.load(urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=30))
            e = d.get("feed", {}).get("entry", [])
            if isinstance(e, dict):
                e = [e]
            return [x.get("id", {}).get("attributes", {}).get("im:id") for x in e]
        except Exception as exc:
            last_err = exc
            time.sleep(2)
    # 取得失敗と「本当にランク外」を区別する。ここで [] を返すと
    # 呼び出し側が current=null（ランク外）として記録してしまい、
    # ネットワーク遮断のたびに過去の順位が虚偽の「圏外」で上書きされる。
    raise FetchFailed(f"{genre}/{kind}: {last_err}")


def main():
    today = sys.argv[1] if len(sys.argv) > 1 else None
    if not today:
        print("日付を引数で渡してください（例: python3 tools/check_ranks.py 2026-08-07）")
        sys.exit(1)

    data = json.loads(OUT.read_text()) if OUT.exists() else {}
    cache = {}
    failed_keys = set()
    for slug, (aid, genre, gname, kind) in TARGETS.items():
        key = (genre, kind)
        if key not in cache and key not in failed_keys:
            try:
                cache[key] = chart(genre, kind)
            except FetchFailed as exc:
                failed_keys.add(key)
                print(f"取得失敗（この分は更新せず前回値を保持）: {exc}", file=sys.stderr)
            time.sleep(0.5)

        if key in failed_keys:
            rec = data.get(slug, {})
            prev = f'{rec.get("current")}位' if rec.get("current") else "（前回値なし）"
            print(f'{slug:14} {gname:14} {LABEL[kind]}  今日 取得失敗  前回 {prev} のまま保持')
            continue

        ids = cache[key]
        rank = ids.index(aid) + 1 if aid in ids else None

        rec = data.get(slug, {})
        rec["genre"] = gname
        rec["kind"] = LABEL[kind]
        rec["current"] = rank
        rec["checked"] = today
        if rank is not None and (rec.get("best") is None or rank < rec["best"]):
            rec["best"] = rank
            rec["best_date"] = today
        data[slug] = rec

        now = f"{rank}位" if rank else "ランク外"
        best = f'（最高 {rec.get("best")}位 / {rec.get("best_date")}）' if rec.get("best") else ""
        print(f'{slug:14} {gname:14} {LABEL[kind]}  今日 {now:>6}  {best}')

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print("\n保存:", OUT.relative_to(ROOT))

    if failed_keys:
        print(f"\n{len(failed_keys)}件のジャンル取得に失敗。取得できた分だけ更新しました。", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
