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

- [ ] **この自動実行環境（Claude Code Remote）から `itunes.apple.com` と `tokyo357.com`（`tokyo357.netlify.app` を含む）への外部通信が遮断されることがある**（2026-08-14 に確認して以降、ほぼ毎回遮断されているが、**間欠的**であることが判明した。プロキシが 403 で CONNECT を拒否。`$HTTPS_PROXY/__agentproxy/status` の `recentRelayFailures` で `connect_rejected` を確認できる）。`tools/ranks.json` の記録を見ると、8/13〜8/18は取得失敗が続いたが、**8/19の回は取得に成功していた**（`checked` が実際に更新され、sukemaru の順位が59位に変わるなど実測値が入っている）。ところが **8/20の回は再び全滅**（8ジャンル中8ジャンルとも `<urlopen error Tunnel connection failed: 403 Forbidden>`、複数回リトライしても回復せず）。つまり「常時遮断」ではなく「その回のセッションによって開通したり遮断されたりする」状態で、いつ開通するか予測できない。`check_ranks.py` は取得失敗時に前回値を保持し `current` を虚偽の「ランク外」で上書きしない実装のままなので、記録が壊れる心配はない。記事執筆は WebSearch（別経路、遮断されていない）が使えるため継続できているが、iTunes lookup APIによる評価数・価格の実測とランキング取得はこのツールでは代替できない。**この状態が続くと、有料アプリの最高順位更新を取り逃している可能性がある。** ネットワークポリシー側で両ホストを常時の許可リストに入れる対応が引き続き最優先。
      **8/21の回も引き続き全滅**（`itunes.apple.com` 8ジャンル中8ジャンルとも失敗、`tokyo357.com` も `/` `/apps/` `/guides/` すべて到達不可）。これで8/20・8/21と2日連続の全滅。`$HTTPS_PROXY/__agentproxy/status` の `recentRelayFailures` を見ると、失敗しているのは `itunes.apple.com:443` と `tokyo357.com:443` の2ホストのみで、`api.github.com` は通常どおり200で応答した。ポリシーがこの2ホストだけを狙って落としている状態が続いている。
      `checked` が全ジャンル失敗で更新されない日は `tools/ranks.json` の `git diff` が空になり、「必ず差分が出る」という前提（下記ステップ1の手順書）は成り立たない。ステップ1の指示文を「差分が出なければ失敗」から「差分が出ないのは全滅日の正常な結果でもあり得る。ただし `checked` の日付が今日になっているか、あるいは全ジャンル失敗のログが出ているかを確認する」に修正する必要がある。
      また `build_guides.py` 等に、今日の日付が `ranks.json` の `checked` に無いと中断するガード（`SKIP_RANK_GUARD=1` で回避可）が入っているのを8/21に確認した。ステップ1を先に実行したうえで全滅だった日は、このガードを意図的に迂回してよい（ステップ1を怠ったわけではないため）。
      **8/22の回も引き続き全滅**（`itunes.apple.com` 8ジャンル中8ジャンルとも失敗、`https://tokyo357.netlify.app` の `/` `/apps/` `/guides/` もすべて `CONNECT tunnel failed, response 403` で到達不可。2回リトライしても回復せず）。これで8/20・8/21・8/22と3日連続の全滅。`checked` は全アプリとも8/19のまま更新できず、`tools/ranks.json` に差分は出ていない（想定どおりの全滅日の挙動）。`SKIP_RANK_GUARD=1` で `build_guides.py` を迂回して記事2本を追加・生成した。この回もローカルサーバーでのみ200を確認でき、本番URLへの到達性は確認できていない。
      **8/23の回も引き続き全滅**（`itunes.apple.com` 8ジャンル中8ジャンルとも `403 Forbidden`、`https://tokyo357.netlify.app` の `/` `/apps/` `/guides/` も `CONNECT tunnel failed, response 403`）。これで8/20〜8/23と4日連続の全滅。`checked` は8/19のまま。`SKIP_RANK_GUARD=1` で迂回して記事2本を追加・生成した。
      **この回、`WebFetch` ツールで任意の外部ドメイン（`ja.wikipedia.org` や記事執筆用に調べた業界サイト数件）を取得しようとしたところ、いずれも `EGRESS_BLOCKED`（`network egress proxy` によるブロック）で失敗した。** `itunes.apple.com` / `tokyo357.com` のような特定2ホストの間欠遮断とは別に、`WebFetch` はそもそも許可リスト外のドメインを既定でブロックする仕組みらしく、動いたのは `WebSearch`（検索結果の要約テキストのみ、リンク先の本文は読めない）だけだった。記事の事実確認は今後も検索結果のスニペット止まりで行い、正確性に自信が持てない数値は「代表的な例」に絞って掲載し、無理に大きな表を作らないこと。
      **8/24の回も引き続き全滅**（`itunes.apple.com` 8ジャンル中8ジャンルとも `403 Forbidden`、`https://tokyo357.netlify.app` の `/` `/apps/` `/guides/` も `CONNECT tunnel failed, response 403`。`$HTTPS_PROXY/__agentproxy/status` の `recentRelayFailures` でも `itunes.apple.com:443` への `connect_rejected` を確認）。これで8/20〜8/24と5日連続の全滅。`checked` は8/19のまま。`SKIP_RANK_GUARD=1` で迂回して記事2本を追加・生成した。
      **8/25の回も引き続き全滅**（`curl`・`WebFetch` のいずれで試しても `itunes.apple.com`・`tokyo357.com` とも `403`／`EGRESS_BLOCKED`。`$HTTPS_PROXY/__agentproxy/status` の `recentRelayFailures` でも `itunes.apple.com:443` への `connect_rejected` を確認）。これで**8/20〜8/25と6日連続**の全滅。`checked` は8/19のまま更新できず。`SKIP_RANK_GUARD=1` で迂回して記事2本を追加・生成した。1週間近く自社アプリの評価数・価格・順位の実測がまったくできておらず、この方針で日々の記事執筆と生成は続けられるものの、**このタスクの本来の測定手段（順位・評価数の変化）がまるまる失われている状態が長期化している。** ネットワークポリシー側での許可リスト対応を、これ以上先送りしない優先課題として運用担当者に申し送る。
      **この回、指示書にある非日本語文字混入チェックのコマンド（`grep -o '[가-힣]\+\|[а-яА-Я]\+' *.html apps/*.html guides/*.html`）が、この環境では正しく機能しないことが判明した。** この環境のロケールが `POSIX`（`LANG`/`LC_ALL` 未設定）になっており、`grep` がハングル・キリル文字のUnicode範囲指定をバイト単位で解釈してしまうため、日本語の平仮名・漢字を含むほぼ全てのHTMLファイルが誤検出される（既存の全ページで大量にヒットする）。実害としての混入は無いことをPythonの`re`モジュール（Unicodeを正しく扱う）で確認した。今後この非日本語文字チェックを行う場合は、シェルの`grep`ではなくPythonの正規表現（`re.compile(r'[가-힣]+|[Ѐ-ӿ]+')`等）で行うこと。
      **8/26の回も引き続き全滅**（`itunes.apple.com` 8ジャンル中8ジャンルとも `403 Forbidden`、`https://tokyo357.netlify.app` の `/` `/apps/` `/guides/` も `CONNECT tunnel failed, response 403`。`api.indexnow.org` への送信も同様に失敗し、遮断対象がこの2ホストに限らないことを確認）。これで**8/20〜8/26と7日連続**の全滅。`checked` は8/19のまま更新できず。`SKIP_RANK_GUARD=1` で迂回して記事2本を追加・生成した。今回は記事の対象アプリ選定を「記事数が最少のアプリ」ではなく「最終更新日が最も古いアプリ」で見直したところ、shizukatl / sukemaru / hitoriinvoice / tsuzukutodo / shimekiri / kinshuwatch の6本が8/10からまったく更新されておらず、その一方で musuberu / kagikake / magedori / negotouranai / repodasu の5本に直近2週間の追加が集中していたことが判明した（件数だけを見ると全アプリ4〜8本の範囲に収まっており、この偏りは件数の集計だけでは見えない）。今回は hitoriinvoice と tsuzukutodo から1本ずつ執筆した。**次回以降も「配信中のアプリを優先」の判断基準として、記事の本数だけでなく最終更新日の分布を確認することを推奨する。**
      **8/27の回も `itunes.apple.com` 8ジャンル中8ジャンルとも失敗、`https://tokyo357.netlify.app` の `/` `/apps/` `/guides/` も到達不可で、8/20〜8/27と8日連続の全滅が続いている。** 一方で `github.com`（`git push`）は今回は正常に通った（下記のdetached HEAD項目を参照。12コミット分のpushに成功）。つまり遮断は依然としてホスト単位・間欠的で、githubは今回開通していた。`checked` は8/19のまま更新できず、`SKIP_RANK_GUARD=1` で迂回。キューが尽きたため、直近17日間（8/10以降）新規記事のなかった live アプリ（shizukatl / shimekiri / kinshuwatch / sukemaru、いずれも記事5〜6本）を last-updated 日付で洗い出し、記事数が並んで少ない shizukatl と shimekiri から1本ずつ執筆した。
      **8/28の回も引き続き全滅**（`itunes.apple.com` 8ジャンル中8ジャンルとも `403 Forbidden`、`https://tokyo357.netlify.app` の `/` `/apps/` `/guides/` も `CONNECT tunnel failed, response 403`）。これで**8/20〜8/28と9日連続**の全滅。`checked` は8/19のまま更新できず、`tools/ranks.json` に差分なし（全滅日の想定どおりの挙動）。`SKIP_RANK_GUARD=1` で迂回。last-updated が最も古い（8/10のまま17日以上更新なし）live アプリ sukemaru / kinshuwatch から新規テーマを2本執筆・生成・検証まで完了し、push した。**測定手段（順位・評価数）が9日間まったく取得できていない状態が続いている。これはこのタスクの目的（App Store製品ページへの流入増加）の効果測定そのものが1週間以上機能していないことを意味し、ネットワークポリシー側の許可リスト対応がこれ以上先送りされるべきではない。**
      **8/29の回も引き続き全滅**（`itunes.apple.com` 8ジャンル中8ジャンルとも `403 Forbidden`、`https://tokyo357.netlify.app` の `/` `/apps/` `/guides/` も `CONNECT tunnel failed, response 403`。`api.github.com` は200で正常）。これで**8/20〜8/29と10日連続**の全滅。`checked` は8/19のまま更新できず、`tools/ranks.json` に差分なし（想定どおり）。今回はセッション開始時点で `HEAD` が `main` を指しており `origin/main` とも一致していたため、detached HEAD の再発なし（13回連続の記録は途切れた）。`SKIP_RANK_GUARD=1` で迂回し、live アプリの中で記事の last-updated が最も古かった kaeseru（8/14のまま）と、記事数が少なく last-updated も古かった musuberu（8/22のまま）から新規テーマを2本執筆。カエセルの記事は標準的な元利均等返済の式で試算した実数値を使用。CSPハッシュは今回、既存の部分追記ではなく全ページから再計算して丸ごと置き換える方式に変え、178件→180件になったことをJSON-LDとの突き合わせで検証した（旧方式は使われなくなったハッシュが残り続ける可能性があったため）。**測定手段（順位・評価数）が10日間まったく取得できていない状態が続いている。**
      **この回、CSPの sha256 ハッシュ検証スクリプトを自作した際に、最初の実装が172本すべてのJSON-LD（既存168ハッシュ分すべてを含む）を「未登録」と誤検出するバグを踏んだ。** 原因は正規表現 `<script type="application/ld\+json">\n(.*?)\n</script>` が `<script>` タグ直後の改行を「区切り文字」として消費してしまい、ハッシュ対象の先頭改行1文字が欠落していたため（`content = "\n" + m.group(1) + "\n"` が正しい）。修正後に再計算すると、実際に未登録だったのは新規記事2本ぶんの4件と、記事一覧ページ（`guides/index.html`、一覧内容が更新されるたびに中身が変わる）の1件だけで、既存記事のCSPは正常だった。**今後この種のチェックを書くときは、対象の1件を手計算（生バイトを直接スライスしてハッシュ）した結果と突き合わせてから全件に適用すること。**
      **8/30の回も引き続き全滅**（`itunes.apple.com` 8ジャンル中8ジャンルとも `403 Forbidden`、`https://tokyo357.netlify.app` の `/` `/apps/` `/guides/` も `CONNECT tunnel failed, response 403`。`$HTTPS_PROXY/__agentproxy/status` の `recentRelayFailures` でも `itunes.apple.com:443` への `connect_rejected` を確認）。これで**8/20〜8/30と11日連続**の全滅。`checked` は8/19のまま更新できず、`tools/ranks.json` に差分なし（想定どおり）。`SKIP_RANK_GUARD=1` で迂回し、live アプリの中で記事の last-updated が最も古かった kigyouojisan・othello（ともに8/19のまま11日更新なし）から新規テーマを2本執筆。kigyouojisan は退職後の社会保険切り替え（国民健康保険・国民年金、それぞれ14日・任意継続20日の期限）を WebSearch で確認し、税務・保険にかかる話のため断定を避け日本年金機構・全国健康保険協会での確認を明記。othello はパスの正しい条件（置ける場所がある限りパス不可）を WebSearch で確認し、既存記事「石の数が多い方が勝っているとは限らない」への内部リンクを追加。CSPハッシュは前回同様、全ページから再計算して丸ごと置き換え、184件になったことをJSON-LD総数（184件）との突き合わせで検証した。**測定手段（順位・評価数）が11日間まったく取得できていない状態が続いている。**
      **8/31の回も引き続き全滅**（`itunes.apple.com` 8ジャンル中8ジャンルとも `403 Forbidden`、`https://tokyo357.netlify.app` の `/` `/apps/` `/guides/` も `CONNECT tunnel failed, response 403`。`$HTTPS_PROXY/__agentproxy/status` の `recentRelayFailures` でも `itunes.apple.com:443` への `connect_rejected` を確認）。これで**8/20〜8/31と12日連続**の全滅。`checked` は8/19のまま更新できず、`tools/ranks.json` に差分なし（想定どおり）。セッション開始時に detached HEAD を発見（`origin/main` と一致、ローカル `main` だけ2コミット遅れ。8/30に続き2日連続の再発、8/29のみ例外）し、fast-forwardのみで復旧（push不要、`origin/main` は無傷）。`SKIP_RANK_GUARD=1` で迂回し、live アプリの中で記事の last-updated が最も古かった（8/23のまま8日更新なし）magedoriと、次に古い3本（kagikake/negotouranai、いずれも8/24で並び）からkagikakeを選定して2本執筆。WebSearchでCD管・PF管の自己消火性の違い・CD管の露出配管禁止・色による見分け方（複数の電材業者サイト）、iCloudバックアップの暗号化の仕組み（Apple公式サポート文書）を確認。CSPハッシュは前回同様、全ページから再計算して丸ごと置き換え、184件→188件になったことをJSON-LD総数（188件）との突き合わせで検証した。**測定手段（順位・評価数）が12日間まったく取得できていない状態が続いている。**
      2026-08-14 の実行で `HEAD` が `main` から外れた detached HEAD の状態でコミットしてしまい、
      その回の成果が2日間 `main` に反映されず、2026-08-16 の実行で発覚・fast-forwardで復旧した。
      2026-08-17 の実行でも、セッション開始直後の時点で再び `HEAD` が `main` から3コミット分
      detached していた（8/16 セッション自身が作った成果を含む）。
      **2026-08-18 の実行でも同じパターンが再発**（`HEAD` が `main` から5コミット分 detached。
      8/17 セッション自身が作った成果を含む）。
      **2026-08-19 の実行でも再発**（ローカルの `main` ブランチが `origin/main` より7コミット遅れた
      状態で detached HEAD になっていた）。ただしこの回は `origin/main` 自体は8/18セッションが
      正しくpushできていたため、fast-forwardで復旧しただけで実害はなかった。
      **2026-08-20 の実行でも再発**（5回連続）。今回は detached HEAD の位置が `origin/main` の
      最新コミットと一致していたため（ローカル `main` ブランチ自体は9コミット遅れていた）、
      fast-forwardで復旧するだけで済み実害はなかったが、毎回チェックアウトが揺れる根本原因は
      変わっていない。5回連続の再発により、
      **このリモート実行環境がセッション開始時にブランチではなく特定コミットへdetached HEADで
      チェックアウトする傾向がある**ことはほぼ確実と見てよい。いずれの回も fast-forward で復旧・
      pushできたため実害はなかったが、**もしいつか fast-forward できない形（コミットが分岐する等）
      で発生した場合、過去の成果を失うリスクがある。**
      **作業開始直後に必ず `git checkout main` してから始める運用は今後も継続すること。**
      5回連続の再発を踏まえ、環境のセッション起動処理（リポジトリのcheckout方法）側の
      調査を強く推奨する。
      **2026-08-23の実行でも再発**（6回連続）。今回は `origin/main`（7コミット分。8/22セッションの
      成果を含む）自体は正しくpushされており、ローカルの `main` ブランチだけが古いコミットを
      指していた状態だった。`git checkout -B main <detached HEADのコミット>` → `git push` で
      復旧を試みたところ `Everything up-to-date` と返り、`origin/main` は既に detached HEAD と
      同じコミットを指していたことが分かった。つまりこの回は実害なし。それでも6回連続の再発は、
      「毎回セッション開始時に `git status`/`git branch` を確認し、detached HEAD なら
      `git checkout -B main <正しいコミット>` してから作業を始める」という運用でしか防げていない。
      **2026-08-24の実行でも再発**（7回連続）。今回は detached HEAD の位置が `origin/main` の
      最新コミット（8/23セッションの成果を含む）と一致しており、ローカルの `main` ブランチ自体は
      6コミット遅れていた。`git checkout -B main origin/main` で復旧し、実害なし。7回連続の
      再発により、運用でカバーし続ける必要がある状態が続いている。
      **同じ2026-08-24、別セッション（週次点検）でも再発**（8回連続）。この回は逆パターンで、
      `origin/main` と ローカル `main` は両方とも `f64e665`（同日の記事セッションが直前に
      修正・pushしたコミット）を指していたが、セッション開始時の detached HEAD は `40587c5` で、
      そこから `origin/main` までの間に9コミット分（記事4本・IndexNow導入・404修正・FAQ追加・
      公開状態突き合わせ4本復旧など、直近数日分の実質的な成果すべて）が乗っていた。つまり
      直前の記事セッションが正しくpushを終えていたにもかかわらず、この点検セッションは
      それより9コミットも新しい断面でdetached HEADとしてチェックアウトされていた。
      `git merge-base --is-ancestor` で分岐していないこと（`origin/main` が detached HEAD の
      祖先であること）を確認したうえで `git checkout -B main 40587c5` → `git push` で
      fast-forward復旧し、実害なし。ただし今回のように9コミット分もの差が生じたのは過去最大で、
      「detached HEAD の位置が毎回ランダムな古い断面になる」のではなく、**セッションごとに
      チェックアウトされる断面がまちまちで、時系列の前後関係すら保証されない**ことを示している。
      復旧前に必ず `git merge-base --is-ancestor <古い方> <新しい方>` で祖先関係を確認し、
      分岐していないことを確かめてから `checkout -B` することを今後の手順として明記する。
      **2026-08-25の実行でも再発**（9回連続）。今回はローカルの `main` が `f64e665`（8/24より前の
      断面）を指す一方、セッション開始時の detached HEAD は `b0cb17f`（8/24週次点検セッションが
      pushした最新の10コミット先）を指しており、かつ `origin/main` 自体はすでに `b0cb17f` を
      指していた（＝pushは成功していたが、ローカル `main` ブランチの参照だけが古いまま復元されていた）。
      `git merge-base main b0cb17f` が `f64e665`（＝main側）であることを確認したうえで
      `git checkout main && git merge --ff-only b0cb17f` で復旧し、`git push` は
      `Everything up-to-date`（＝origin側は無傷）。実害なし。9回連続の再発により、この環境の
      セッション起動処理がリポジトリを毎回どこかの断面へ detached HEAD でチェックアウトする
      挙動は環境側の仕様と見てよく、**セッション開始直後に必ず `git status`/`git branch -v` を
      確認し、`git merge-base` で祖先関係を確かめてから `main` へ復旧する運用を今後も続ける。**
      **2026-08-26の実行でも再発**（10回連続）。今回は detached HEAD が `origin/main` の最新コミット
      （8/25セッションが記事2本を追加してpushした断面）と一致しており、ローカルの `main` だけが
      11コミット遅れていた。`git fetch origin main` で確認したところ祖先関係に問題はなく、
      `git checkout main && git merge --ff-only origin/main` で復旧、実害なし。10回連続の再発により、
      「セッション開始直後に必ず確認・復旧する」運用は今後も継続が前提となる。
      **2026-08-27の実行では、これまでと違い実害が出ていたことが判明した（11回連続）。**
      セッション開始時、detached HEAD は `origin/main`（`f64e665`）より**12コミットも先**にいた。
      `git merge-base --is-ancestor` で `origin/main` が detached HEAD の祖先であることを確認した
      うえで `git checkout main && git merge --ff-only <detached HEADのコミット>` で復旧し、
      `git push` したところ**今回は正常にpushできた**（`Everything up-to-date` ではなく実際に
      `origin/main` が12コミット分更新された）。つまり、8/20〜8/26の間のどこかの回から、
      毎回のセッションが detached HEAD の続き（前回セッション自身が作った未push分）の上に
      さらにコミットを積み重ねる形になっており、**その間ずっと `origin/main`（＝本番Netlifyに
      反映される内容）が更新されていなかった**。記事12本相当・IndexNow導入・404修正・
      BreadcrumbList不具合修正など、直近1週間分の実質的な成果すべてが本番未反映のまま
      ローカルにのみ溜まっていたことになる。過去の再発はすべて「fast-forwardで復旧・push成功・
      実害なし」だったが、今回は逆に**pushそのものが機能していなかった期間が続いていた**ことを
      示している。原因は特定できていないが、「セッション開始直後に検出・復旧する」運用だけでは
      不十分で、**復旧後に `git push` の出力を鵜呑みにせず、`git fetch` して `origin/main` の
      コミットハッシュが実際に前進したかを確認する**手順を今後は必須とする。
      **2026-08-28の実行でも再発**（12回連続）。今回は detached HEAD が `origin/main`
      （8/27セッションが正しくpushした断面）より1コミット遅れていただけで、`origin/main` 自体は
      無傷だった。`git merge-base --is-ancestor` でローカル `main` が detached HEAD の祖先である
      ことを確認したうえで `git checkout main && git merge --ff-only <detached HEADのコミット>`
      で復旧し、`git fetch` で `origin/main` のハッシュ前進を確認する必要すらなかった（pushが
      要らない、fast-forwardのみで完結する軽微なケース）。実害なし。12回連続の再発により、
      このセッション起動時のdetached HEAD挙動は環境側の恒常的な仕様と見てよい。
      **2026-08-29の実行は例外的に detached HEAD が発生せず**（`HEAD` が最初から `main` を指し、
      `origin/main` とも一致）、12回連続の記録は途切れた。ところが**2026-08-30の実行で再発**。
      今回は detached HEAD が `origin/main`（8/29セッションが正しくpushした断面）と完全に一致し、
      ローカルの `main` だけが1コミット遅れていた。`git checkout main && git merge --ff-only <detached
      HEADのコミット>` で復旧し、pushは不要（fast-forwardのみで完結）。実害なし。1日だけ途切れたものの
      すぐ再発したことから、detached HEAD 自体は依然として毎回のセッション起動時に起こりうる前提で
      運用を続ける必要がある。
- [ ] **`yamaguchi@tokyo357.com` を受信できるようにする**（最優先）。ドメインにメールが未設定なら、転送設定かGoogle Workspace等を用意する。受信できないサポートURLは審査で問題になる。
- [ ] **DNSレコードの追加**（下記「独自ドメイン」参照）。Netlify側の接続とビルドは完了済み。
- [ ] 代表者名を会社概要に載せるか決める（現状は未掲載）。
- [ ] 各アプリの App Store 公開後、`/apps/<app>` に App Store へのリンクとスクリーンショットを追加する。
      2026-08-24 時点の公開済み（15本）: ぱすてるオセロ／起業おじさん／つづくToDo／シメキリ逆算／禁酒ウォッチ／
      しずかTL for X／透けマル／カエセル／サガセル録音／ひとり請求書／マゲドリ／ねごと占い／レポダス／ムスベル／カギカケ。
      申請準備中: だんどりレシピ／ハナログ／オボエル家計簿／ナラセル。審査中のアプリは現在なし。
- [ ] **`netlify.toml` の `/guides/<slug>.html → /guides/<slug>` リダイレクトが、記事85本中52本で未設定**（2026-08-24に確認）。
      直近の記事追加セッションの多くがこの手順を省略している。Netlifyの「Pretty URLs」機能により
      拡張子なしURLは自動で配信されているとみられ、現状で実害（404等）は確認されていないが、
      ネットワーク遮断のため本番での実地確認はできていない。まとめて追記するか、この手順自体が
      不要（Netlify側で自動対応済み）と判断してREADMEの手順から削るか、どちらかに倒すことを検討。
- [ ] **ライブガチャ（`com.tokyo357.livegacha` / App ID 6797749180）はサイトに載せない。**
      ライセンサー提示用のTestFlight内部テスト限定デモで、同梱素材に未許諾の第三者IPを含む
      （`~/live-gacha/README.md` 参照）。公開素材へ差し替えて一般配信すると決まるまで掲載不可。
- [ ] App Store の販売者表示は `Daisuke Yamaguchi`（個人名義）。サイト各所の「提供元 株式会社サウナ」と食い違うため、Apple Developer の法人アカウント移行かサイト表記のどちらに寄せるか決める。
- [ ] `tools/naraseru`（サンプラー）はまだ記事が0本（`tools/article_queue.md` に未着手のまま1行残っている）。`state="prepare"` のため優先度は live アプリより低いが、キューが尽きたら着手する。

### 完了済み

- [x] **`tools/new_guide.py` の `write_guide()` が BreadcrumbList の構造化データを生成していなかった不具合を修正**（2026-08-25）。
      既存記事はどれも `Article` と `BreadcrumbList` の2つの JSON-LD を持つが、`write_guide()` は `Article` の1つしか
      出力していなかった（既存記事にBreadcrumbListがある理由はこのツールを使わず手で足していたためとみられる）。
      本日追加した2本で気づき、`write_guide()` にBreadcrumbList生成を追加してから再生成した。検証（JSON-LD数・CSPハッシュ数の一致）で確認済み。
- [x] Netlify 接続（プロジェクト `tokyo357` / https://tokyo357.netlify.app、`main` push で自動デプロイ）
- [x] App Store 販売者名義を **株式会社サウナ** に確定。`~/othello` と `~/othello-privacy` の表記も統一済み
      （Bundle ID も `com.tokyo357.othello` に変更した。Apple Developer 側で `com.c7mon.othello` を
      すでに登録済みだった場合はここを戻すこと）
- [x] **アプリが live になったあとも「審査中です」「申請の準備中です」の文言が取り残る不具合を修正**（2026-08-20）。
      `apps/*.html` は `build_pages.py` が毎回 `BUILD:install` ブロックを丸ごと上書きするため live 反映は
      問題なかったが、①アプリ紹介ページの本文（`.prose`内、BUILDブロック外）に手書きで残った「現在 App Store に
      申請の準備中です」の一文が4本（kagikake / magedori / musuberu / repodasu）で live 後も表示されたままだった、
      ②`guides/*.html` の install セクション（記事内の自社アプリ紹介）は個別記事ごとの手書きで、live化を検知して
      自動更新する仕組みがなく、6本の記事で「よくある質問」の灰色ボタンしか出ず**ダウンロードボタンが出ていなかった**、
      ③関連記事カード（related-card）の `<em>価格・状態</em>` も30本の記事で古い状態表示のままだった。
      ①は手動で除去、②③は `tools/sync_guide_status.py` を新規作成し `tools/apps.py` を単一情報源として
      機械的に同期する仕組みにした（何度実行しても同じ結果になる）。今後 `tools/apps.py` の state を
      live に変えたら、`build_pages.py` `build_index_pages.py` に加えて **`sync_guide_status.py` も回すこと**。

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
python3 tools/sync_guide_status.py  # /guides/ 記事内の自社アプリ紹介・related-cardの状態表記をapps.pyに同期
python3 tools/build_faq_ld.py       # /support の FAQPage 構造化データ
python3 tools/sync_nav.py           # 全ページのナビ
```

最後に CSP のハッシュを更新すること（下記）。すべて何度実行しても同じ結果になる。

### IndexNow（Bing・Yandex・Naver・Seznam に即時通知）

Google は IndexNow に対応していないので、これで動くのは Bing 系だけ（DuckDuckGo も Bing）。
それでも無料・認証不要・ユーザー操作ゼロで回せるので、内容を更新したら送る。

```bash
python3 tools/indexnow.py        # 送るURLの確認
python3 tools/indexnow.py send   # 送信（sitemap.xml の全URL）
```

鍵はサイト直下の `<key>.txt` で証明している。**このファイルを消すと送信が全部弾かれる**。
鍵を変えるとファイル名も変わるので、`tools/indexnow.py` の `KEY` は固定のままにすること。

### まだ手をつけていないこと

- [ ] Google Search Console で sitemap を送信する（所有権確認ファイルは設置済み。API はOAuthが要るので手作業）
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
for f in ['index.html'] + sorted(glob.glob('apps/*.html')) + sorted(glob.glob('guides/*.html')) + ['support.html', 'privacy.html', 'terms.html', '404.html']:
    if not pathlib.Path(f).exists(): continue
    s = pathlib.Path(f).read_text()
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        print(f, "'sha256-" + base64.b64encode(hashlib.sha256(m.group(1).encode()).digest()).decode() + "'")
PY
```
