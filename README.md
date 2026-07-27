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
| `/apps/othello` | `apps/othello.html` | オセロのアプリ紹介・サポート導線 |
| — | `404.html` | 存在しないURL |

`/contact` → `/support`、`/othello` → `/apps/othello` のリダイレクトも張ってある（`netlify.toml`）。

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
| マーケティングURL（任意） | `https://tokyo357.com/apps/othello` |
| EULA | 標準EULAのままで可。独自にする場合は `https://tokyo357.com/terms` |

## 未確定・要対応

- [ ] **`yamaguchi@tokyo357.com` を受信できるようにする**（最優先）。ドメインにメールが未設定なら、転送設定かGoogle Workspace等を用意する。受信できないサポートURLは審査で問題になる。
- [ ] **DNSレコードの追加**（下記「独自ドメイン」参照）。Netlify側の接続とビルドは完了済み。
- [ ] 代表者名を会社概要に載せるか決める（現状は未掲載）。
- [ ] App Store 公開後、`/apps/othello` に App Store へのリンクとスクリーンショットを追加する。

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

## CSPのハッシュ更新

`netlify.toml` の `Content-Security-Policy` は、ページ内の JSON-LD をハッシュで許可している。
JSON-LD を編集したら次を実行し、出た値で `netlify.toml` を書き換える。

```bash
python3 - <<'PY'
import re, hashlib, base64, pathlib
for f in ['index.html', 'apps/othello.html']:
    s = pathlib.Path(f).read_text()
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        print(f, "'sha256-" + base64.b64encode(hashlib.sha256(m.group(1).encode()).digest()).decode() + "'")
PY
```
