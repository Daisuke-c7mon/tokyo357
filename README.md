# tokyo357.com — 株式会社サウナ / Sauna Inc.

iOSアプリ開発とITコンサルティングを行う株式会社サウナのコーポレートサイト。
**App Store 申請時の「サポートURL」「プライバシーポリシーURL」を兼ねる。**

ビルド不要の静的サイト（HTML / CSS / Vanilla JS）。Netlify が GitHub の `main` を見て自動デプロイする。

## ページ

| URL | ファイル | 用途 |
|---|---|---|
| `/` | `index.html` | 会社トップ（事業内容・制作物・会社概要） |
| `/support` | `support.html` | **App Store のサポートURLに指定する**。日英併記 |
| `/privacy` | `privacy.html` | **App Store のプライバシーポリシーURLに指定する**。日英併記 |
| `/terms` | `terms.html` | 利用規約（EULA）。日英併記 |
| `/apps/<app>` | `apps/<app>.html` | アプリ紹介・サポート導線。現在 shizukatl / sukemaru / kaeseru / sagaseru / hitoriinvoice / tsuzukutodo / shimekiri / kinshuwatch / kigyouojisan / othello の10本 |
| — | `404.html` | 存在しないURL |

`/contact` → `/support`、`/<app>` → `/apps/<app>` のリダイレクトも張ってある（`netlify.toml`）。
しずかTL は App Store Connect に `/shizukatl/support` `/shizukatl/privacy` を登録済みのため、この2つのリダイレクトを消さないこと（消すと審査で 404 になる）。

## ローカルで見る

```bash
cd ~/tokyo357
python3 -m http.server 8357
# http://localhost:8357/ を開く
```

ローカルの簡易サーバーは拡張子なしURLを解決しないため、`/support.html` のように直接開く。Netlify 上では `/support` で表示される。

## デプロイ

`main` に push すると Netlify が自動で公開する。

```bash
git add -A && git commit -m "…" && git push
```

### Netlify 接続（完了済み）

| 項目 | 値 |
|---|---|
| プロジェクト名 | `tokyo357` |
| 暫定URL | https://tokyo357.netlify.app |
| 管理画面 | https://app.netlify.com/projects/tokyo357 |
| 連携リポジトリ | `Daisuke-c7mon/tokyo357` の `main` |

Build command は空、Publish directory は `.`（`netlify.toml` の通り）。`main` に push すると自動でビルドが走る。

### 独自ドメイン（tokyo357.com）

現在 `tokyo357.com` は NS が `01〜04.dnsv.jp`（お名前.com系）に向いており、**A / CNAME レコードが未設定＝未公開**。

Netlify で **Domain management → Add custom domain → `tokyo357.com`** を追加したうえで、DNS 側に次を設定する。

| ホスト | 種別 | 値 |
|---|---|---|
| `@`（tokyo357.com） | A | `75.2.60.5`（Netlify の Apex 用IP。管理画面の指示を優先） |
| `www` | CNAME | `<サイト名>.netlify.app` |

反映後、Netlify が Let's Encrypt の証明書を自動発行する（数分〜1時間）。`https://tokyo357.com/support` が開けたら App Store Connect に登録できる。

> ネームサーバーごと Netlify DNS に委任する方法もあるが、同ドメインでメールを使う場合は MX レコードの移設が必要になるため、上記のレコード追加のみを推奨。

## App Store Connect への登録値

| 項目 | 値 |
|---|---|
| サポートURL | `https://tokyo357.com/support` |
| プライバシーポリシーURL | `https://tokyo357.com/privacy` |
| マーケティングURL（任意） | `https://tokyo357.com/apps/<app>` |
| EULA | 標準EULAのままで可。独自にする場合は `https://tokyo357.com/terms` |

## 未確定・要対応

- [ ] **`yamaguchi@tokyo357.com` を受信できるようにする**（最優先）。ドメインにメールが未設定なら、転送設定かGoogle Workspace等を用意する。受信できないサポートURLは審査で問題になる。
- [ ] **DNSレコードの追加**（下記「独自ドメイン」参照）。Netlify側の接続とビルドは完了済み。
- [ ] 代表者名を会社概要に載せるか決める（現状は未掲載）。
- [ ] 各アプリの App Store 公開後、`/apps/<app>` に App Store へのリンクとスクリーンショットを追加する。
      2026-08-05 時点の公開済み: ぱすてるオセロ／起業おじさん／つづくToDo／シメキリ逆算／禁酒ウォッチ。
      審査中: しずかTL for X／透けマル／カエセル／サガセル録音／ひとり請求書。
- [ ] **ライブガチャ（`com.tokyo357.livegacha` / App ID 6797749180）はサイトに載せない。**
      ライセンサー提示用のTestFlight内部テスト限定デモで、同梱素材に未許諾の第三者IPを含む
      （`~/live-gacha/README.md` 参照）。公開素材へ差し替えて一般配信すると決まるまで掲載不可。
- [ ] App Store の販売者表示は `Daisuke Yamaguchi`（個人名義）。サイト各所の「提供元 株式会社サウナ」と食い違うため、Apple Developer の法人アカウント移行かサイト表記のどちらに寄せるか決める。

### 完了済み

- [x] Netlify 接続（プロジェクト `tokyo357` / https://tokyo357.netlify.app、`main` push で自動デプロイ）
- [x] App Store 販売者名義を **株式会社サウナ** に確定。`~/othello` と `~/othello-privacy` の表記も統一済み
      （Bundle ID も `com.tokyo357.othello` に変更した。Apple Developer 側で `com.c7mon.othello` を
      すでに登録済みだった場合はここを戻すこと）

## 設計メモ

サウナの温度（サウナ室 → 水風呂 → 外気浴）をそのまま情報構造に使っている。

- 熱いセクション（炭色＋熾火色）＝ **つくる**：アプリ開発・制作物
- 冷たいセクション（水風呂色に反転）＝ **整える**：ITコンサルティング
- 左端の温度計レールは `data-temp` / `data-stage` / `data-level` / `data-phase` 属性を読んで動く（`assets/site.js`）。セクションを増やすときは同じ属性を付ける。

配色・タイポは `assets/style.css` 冒頭の `:root` に集約。

## 集客の仕組み（2026-08-05）

サイト経由でインストールまで運ぶための仕掛け。すべて無料で回している。

| 仕掛け | 場所 | ねらい |
|---|---|---|
| Smart App Banner | 公開済みアプリページの `<meta name="apple-itunes-app">` | iOS Safari が純正のインストールバナーを最上部に出す。web→installで最も効く |
| キャンペーントークン | App Storeリンクの `?ct=` | App Store Connect → App Analytics → 獲得 → キャンペーン で流入元別のインストール数が見える |
| QRコード | 公開済みアプリページ（PCのみ表示） | PCで読んだ人をスマホに渡す。スマホでは非表示 |
| og:image | 全ページ | X・LINE・Slackで共有されたときにカードが出る |
| FAQPage 構造化データ | `/support` | 検索結果に質問が展開される（リッチリザルト） |
| 解決記事 | `/guides/` | 「透過 保存 白い」等の悩み検索の受け皿。無料で答え切ってからアプリを案内する |
| 回遊 | 各アプリページ下部 | 1本入れた人に他のアプリを見せる |

### ct（キャンペーントークン）の使い分け

- `web_app_hero` … アプリページ上部のボタン
- `web_app_body` … 本文中のリンク
- `web_app_page` … アプリページ下部のインストール枠
- `web_qr` … QRコード経由
- `web_guide` … 記事からのリンク

### 生成スクリプト

台帳は `tools/apps.py` の1ファイルだけ。ここを直してから下を回す。

```bash
python3 tools/build_assets.py       # OG画像とQRを生成（アイコンや状態を変えたとき）
python3 tools/build_pages.py        # アプリページの head / インストール枠 / 関連アプリ
python3 tools/build_index_pages.py  # /apps/
python3 tools/build_guides.py       # /guides/ の共通パーツと一覧
python3 tools/build_faq_ld.py       # /support の FAQPage 構造化データ
python3 tools/sync_nav.py           # 全ページのナビ
```

最後に CSP のハッシュを更新すること（下記）。すべて何度実行しても同じ結果になる。

### まだ手をつけていないこと

- [ ] Google Search Console にサイトを登録して sitemap を送信する（無料。検索での見え方はここでしか分からない）
- [ ] 記事を増やす。次の候補は「請求書の明細が足りない」「住宅ローンの5年ルールと未払利息」「録音から必要な部分だけ探す」
- [ ] 審査中のアプリが公開されたら `tools/apps.py` の state を live にして再生成（QRとバナーが自動でつく）

## CSS/JSを変更したときは

`assets/style.css` か `assets/site.js` を触ったら、**全HTMLの `?v=` を今日の日付に上げる**。
上げ忘れると、HTMLだけ新しくCSSが古い訪問者が出てレイアウトが崩れる。

```bash
cd ~/tokyo357
NEW=$(date +%Y%m%d)
grep -rlE 'style\.css\?v=|site\.js\?v=' --include='*.html' . \
  | xargs sed -i '' -E "s/(style\.css|site\.js)\?v=[0-9]+/\1?v=$NEW/g"
grep -rho 'style\.css?v=[0-9]*' --include='*.html' . | sort -u   # 1種類だけになっていること
```

`netlify.toml` 側でも `/assets/*` は `max-age=0, must-revalidate`（ETagで304）にしてあるので、
`?v=` を忘れても最悪1リクエストで正しいCSSに戻る。二重の保険。

## CSPのハッシュ更新

`netlify.toml` の `Content-Security-Policy` は、ページ内の JSON-LD をハッシュで許可している。
JSON-LD を編集したら次を実行し、出た値で `netlify.toml` を書き換える。

```bash
python3 - <<'PY'
import re, hashlib, base64, pathlib
import glob
for f in ['index.html'] + sorted(glob.glob('apps/*.html')) + ['support.html', 'privacy.html', 'terms.html', '404.html']:
    if not pathlib.Path(f).exists(): continue
    s = pathlib.Path(f).read_text()
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        print(f, "'sha256-" + base64.b64encode(hashlib.sha256(m.group(1).encode()).digest()).decode() + "'")
PY
```
