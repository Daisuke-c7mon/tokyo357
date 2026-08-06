"""サイト内で使うアプリ台帳。ページ生成スクリプトはすべてここを唯一の情報源にする。

App Store Connect の状態が変わったら、ここと各HTMLの状態行を更新する。
"""

# state: "live"（公開中） / "review"（審査中） / "prepare"（申請準備中）
APPS = [
    dict(slug="shizukatl", name="しずかTL for X", appid="6796696394", state="review",
         price="買い切り 120円", os="iOS 17+",
         tagline="タイムラインを、静かに、順番どおりに。",
         short="Safari で X を時系列・静かな画面で読む拡張機能。効いているかを診断できる。",
         topic="画面まわり・気晴らし"),
    dict(slug="sukemaru", name="透けマル", appid="6796656589", state="live",
         price="買い切り 120円", os="iOS 17+",
         tagline="透過できたか、数値で分かる。",
         short="背景を消して透過PNGに。書き出したファイルを読み戻してアルファを実測する。",
         topic="画面まわり・気晴らし"),
    dict(slug="kaeseru", name="カエセル", appid="6796657244", state="live",
         price="買い切り 120円", os="iOS 17+",
         tagline="グラフではなく、円の差額で答える。",
         short="住宅ローンの計算。金利上昇と繰上返済の損得を金額で出す。",
         topic="仕事の道具"),
    dict(slug="sagaseru", name="サガセル録音", appid="6796545639", state="review",
         price="買い切り 120円", os="iOS 17+",
         tagline="録音を、話した言葉で探す。",
         short="文字起こしの1文をタップすると音声がその瞬間まで飛ぶボイスメモ。",
         topic="仕事の道具"),
    dict(slug="hitoriinvoice", name="ひとり請求書", appid="6796195340", state="review",
         price="無料（120円の買い切りで全機能）", os="iOS 17+",
         tagline="明細の件数で、行き止まらない。",
         short="見積・納品・請求・領収を同じ明細から1タップ。インボイス対応。",
         topic="仕事の道具"),
    dict(slug="tsuzukutodo", name="つづくToDo", appid="6796174701", state="live",
         price="買い切り 120円", os="iOS 17+",
         tagline="習慣もToDoも、ひとつの画面で。",
         short="上限のないタスク、取り消せる記録、あとから付けられる日。",
         topic="毎日の記録"),
    dict(slug="shimekiri", name="シメキリ逆算", appid="6796252958", state="live",
         price="買い切り 120円", os="iOS 17+",
         tagline="今日やる分を、締切から逆算する。",
         short="間に合わないときは、延ばす日数・増やす分数・削る量を数字で出す。",
         topic="毎日の記録"),
    dict(slug="kinshuwatch", name="禁酒ウォッチ", appid="6795822272", state="live",
         price="買い切り 100円", os="iOS 17+",
         tagline="飲んでいない時間が、積み上がる。",
         short="本数・金額・カロリーに換算。飲んでも記録は消えない。",
         topic="毎日の記録"),
    dict(slug="kigyouojisan", name="起業おじさん", appid="6795361615", state="live",
         price="無料", os="iOS 17+",
         tagline="起業の悩みを、話せる相手。",
         short="まず聞いて、今週できる一歩を1つか2つだけ示す相談アプリ。",
         topic="仕事の道具"),
    dict(slug="othello", name="ぱすてるオセロ", appid="6793739141", state="live",
         price="無料", os="iOS 16+",
         tagline="Lv1は必ず勝てる。Lv10は全力。",
         short="レベル1〜10のCPUと対戦。オフラインで遊べる。",
         topic="画面まわり・気晴らし"),
]

BY_SLUG = {a["slug"]: a for a in APPS}


def store_url(appid, ct):
    """App Store のURL。ct はキャンペーントークンで、App Store Connect の
    App Analytics → 獲得 → キャンペーン に流入元として表示される（無料）。"""
    return f"https://apps.apple.com/jp/app/id{appid}?ct={ct}&mt=8"
