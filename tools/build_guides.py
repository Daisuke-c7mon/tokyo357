#!/usr/bin/env python3
"""記事（/guides）のヘッダー・フッター・一覧ページを一括で揃える。

    python3 tools/build_guides.py

記事の本文は guides/*.html に直接書く。このスクリプトは共通パーツと一覧だけを面倒みる。
記事を足したら GUIDES に1行足すこと。
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apps import BY_SLUG  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
VER = "20260805"

# 記事の台帳。順番がそのまま一覧の並び。
GUIDES = [
    dict(slug="transparent-png-white", topic="画像・写真", date="2026-08-05",
         title="背景を透過したのに、保存すると白くなる",
         lead="透過したはずのPNGが白く見える現象には、種類の違う3つの原因があります。最も多いのは「写真アプリの表示上の仕様」で、ファイルは壊れていません。",
         app="sukemaru"),
    dict(slug="x-chronological-safari", topic="X・SNSの表示", date="2026-08-05",
         title="X（旧Twitter）のタイムラインを時系列に戻す",
         lead="「フォロー中」を選んでも、しばらくすると「おすすめ」に戻ってしまう。iPhoneのSafariで、表示を自分の側で固定する方法を説明します。",
         app="shizukatl"),
    dict(slug="deadline-daily-quota", topic="習慣・記録", date="2026-08-05",
         title="締切から逆算して、今日やる量を決める",
         lead="「1日◯ページ」を最初に決めても、1日休んだ時点で計画は壊れます。壊れない配分の作り方と、間に合わないと分かったときの3つの選択肢。",
         app="shimekiri"),
    dict(slug="kinshu-app-hikaku", topic="毎日の記録／比較", date="2026-08-05",
         title="禁酒・断酒アプリ6本を比較して分かった、続く記録の条件",
         lead="禁酒アプリは無料でよくできたものが揃っています。それでも続かないのは、機能の差ではなく「飲んでしまった日にどうなるか」の設計の差です。App Storeで実際に使われている6本を、価格・評価・設計思想の面から比",
         app="kinshuwatch"),
    dict(slug="shukan-app-hikaku", topic="毎日の記録／比較", date="2026-08-05",
         title="習慣化アプリ6本を比較 — 買い切りと無料、どちらを選ぶか",
         lead="習慣化アプリは無料の名作が揃っている分野です。それでも買い切りを選ぶ理由があるとすれば、どこか。App Storeで実際に使われている6本を、価格・評価・タスク数の上限・記録の直しやすさで比べます。",
         app="tsuzukutodo"),
    dict(slug="shimekiri-app-hikaku", topic="毎日の記録／比較", date="2026-08-05",
         title="締切・進捗管理アプリを比較 — 「間に合わない」と分かった後に何が出るか",
         lead="締切管理アプリの多くは、残り日数を数えるところで止まります。本当に必要なのは、間に合わないと分かったときに何をすればいいかです。App Storeの締切・進捗管理アプリを比べ、選ぶ基準を整理します。",
         app="shimekiri"),
    dict(slug="haikei-touka-app-hikaku", topic="画像・写真／比較", date="2026-08-05",
         title="背景透過アプリを比較 — 「保存すると白くなる」が起きる理由",
         lead="背景透過アプリは無料の名作が揃っています。それでも低評価レビューで最も多いのは「保存すると透過にならない」でした。実際に使われているアプリを比べながら、この問題がどこで起きるかを説明します。",
         app="sukemaru"),
    dict(slug="seikyusho-app-hikaku", topic="仕事の道具／比較", date="2026-08-05",
         title="請求書アプリを比較 — 個人事業主が「行き止まる」ところ",
         lead="請求書アプリは無料でクラウド連携するものが主流です。しかし低評価レビュー333件を分類すると、不満が集まる場所ははっきり決まっていました。実際に使われているアプリを比べ、ひとりで帳票を出す人の選び方を整理します",
         app="hitoriinvoice"),
    dict(slug="loan-app-hikaku", topic="お金の計算／比較", date="2026-08-05",
         title="住宅ローン計算アプリを比較 — 5年ルールと未払利息が見えるか",
         lead="住宅ローン計算アプリは無料の定番が揃っています。しかし変動金利の「5年ルール・125%ルール」で繰り延べられる未払利息まで出すものは多くありません。実際に使われているアプリを比べます。",
         app="kaeseru"),
    dict(slug="rokuon-mojiokoshi-hikaku", topic="仕事の道具／比較", date="2026-08-05",
         title="録音・文字起こしアプリを比較 — 1時間の録音から30秒を探せるか",
         lead="文字起こしができるアプリは増えましたが、書き起こした後に「必要な部分へ戻れるか」で使い勝手は大きく変わります。実際に使われている録音・文字起こしアプリを比べます。",
         app="sagaseru"),
    dict(slug="safari-hyoji-seigyo-hikaku", topic="X・SNSの表示／比較", date="2026-08-05",
         title="Safariの表示を変える拡張機能を比較 — 効いているか分かるか",
         lead="Safariの拡張機能は、入れても効いているかどうかが分かりません。広告ブロッカーと表示制御の拡張機能を比べながら、選ぶときに見るべき点を整理します。",
         app="shizukatl"),
    dict(slug="othello-app-hikaku", topic="ゲーム／比較", date="2026-08-05",
         title="オセロアプリを比較 — ひとりで練習したい人が選ぶなら",
         lead="オセロアプリはオンライン対戦が主流で、無料のものが揃っています。ひとりで静かに練習したい場合に何を見て選ぶべきかを、実際に使われているアプリと比べながら整理します。",
         app="othello"),
    dict(slug="seikyusho-meisai-tarinai", topic="仕事の道具", date="2026-08-06",
         title="請求書の明細が途中で足りなくなる",
         lead="ExcelやNumbersの請求書テンプレートは行数があらかじめ決まっています。26行や30行を超えると崩れる理由と、テンプレートのまま直せる範囲・直らない場合の考え方を説明します。",
         app="hitoriinvoice"),
    dict(slug="loan-5nen-rule-miharai-risoku", topic="仕事の道具", date="2026-08-06",
         title="変動金利の5年ルール・125%ルールと未払利息の仕組み",
         lead="金利が上がったのに返済額が変わらないのはなぜか。5年ルール・125%ルールの仕組みと、その裏で積み上がる未払利息、完済時の一括請求リスクを説明します。",
         app="kaeseru"),
    dict(slug="shukan-mikka-bouzu", topic="毎日の記録", date="2026-08-06",
         title="習慣が三日坊主で終わるのは、記録の付け方に原因がある",
         lead="習慣が続かないのは意志が弱いからではなく、記録の設計が「1日休んだら終わり」になっているからです。連続日数を追わない記録の付け方を説明します。",
         app="tsuzukutodo"),
    dict(slug="kinshu-ikura-uku", topic="毎日の記録", date="2026-08-06",
         title="禁酒でお金はいくら浮くのか — 自分の数字で計算する",
         lead="「年間◯万円節約」という平均値は自分には当てはまりません。1日あたりの実額の出し方と、見落としがちな付随費用、続けたときの累計を計算します。",
         app="kinshuwatch"),
    dict(slug="kuriage-hensai-dochira", topic="お金の計算", date="2026-08-06",
         title="繰上返済は期間短縮型と返済額軽減型のどちらが得か",
         lead="利息の削減額は期間短縮型が大きくなりますが、それだけで決めると危険です。判断に必要な数字と、手数料を含めた損得の見方を説明します。",
         app="kaeseru"),
    dict(slug="line-stamp-touka-png", topic="画像・写真", date="2026-08-06",
         title="LINEスタンプやフリマ用に、背景を透明にしたPNGを作る",
         lead="提出してから「透過されていません」で弾かれるのがこの作業で最もつらいところです。作り方と、事前に確認する方法を説明します。",
         app="sukemaru"),
    dict(slug="othello-joseki-kihon", topic="ゲーム", date="2026-08-06",
         title="オセロで初心者が勝てるようになる順番",
         lead="オセロは序盤にたくさん取ると不利になるゲームです。角と辺の考え方、序盤に石を取りすぎない理由を、練習する順番で整理します。",
         app="othello"),
    dict(slug="rokuon-hitsuyou-bubun-sagasu", topic="仕事の道具", date="2026-08-07",
         title="1時間の録音から、必要な30秒だけを探す方法",
         lead="長い会議や打ち合わせの録音から、あの発言だけをもう一度聞きたい。倍速再生やスキップボタンには限界があります。文字起こしを検索してから頭出しするという探し方を説明します。",
         app="sagaseru"),
    dict(slug="seikyusho-pdf-a4-insatsu", topic="仕事の道具", date="2026-08-07",
         title="iPhoneで請求書をPDFにして、A4サイズのまま印刷する方法",
         lead="iPhoneで作った請求書をPDFにして印刷したら、A4の紙に極小サイズで印刷された。この現象が起きる理由と、正しいA4サイズで書き出す方法、プリンターがない場合の印刷方法を説明します。",
         app="hitoriinvoice"),
    dict(slug="kaigyoutodoke-junban", topic="仕事の道具", date="2026-08-08",
         title="個人事業の開業、何から手をつければいいか",
         lead="提出する書類の種類と順番が分からず止まってしまう人は多いです。実は法律で期限が決まっている届出は「開業届」と「青色申告承認申請書」の2つだけ。何を、いつまでに出すべきかを期限順に整理します。",
         app="kigyouojisan"),
    dict(slug="yagou-kimekata", topic="仕事の道具", date="2026-08-09",
         title="屋号はどう決めればいいか — 使える語と、口座を作れるタイミング",
         lead="屋号には登記も許可も不要で、開業届の提出時に決まっていなくても構いません。ただし「銀行」「保険」など使えない語があり、屋号名義の口座は開業届の控えが必要になることが多いです。決め方と使い始めるタイミングを整理します。",
         app="kigyouojisan"),
    dict(slug="receipt-app-osoi", topic="仕事の道具", date="2026-08-09",
         title="レシートを撮る家計簿アプリで、反映が遅いのはなぜか",
         lead="レシートを撮ってから反映まで1〜2日かかることがあります。処理が遅いのではなく、読み取りを人が目視でやっているためです。",
         app="oboerukakeibo"),
    dict(slug="kakeibo-tsuzukanai", topic="仕事の道具", date="2026-08-09",
         title="家計簿が続かないのは、入力が面倒だからではない",
         lead="脱落が起きるのは面倒になったときではなく、記録した数字が信用できなくなった瞬間です。ずれが生まれる3か所を潰します。",
         app="oboerukakeibo"),
    dict(slug="nikki-tsuzukanai-hanasu", topic="毎日の記録", date="2026-08-09",
         title="日記が三日で終わる人のための、書かない記録のつくり方",
         lead="続かないのは意志ではなく「書く」作業の重さです。話して記録に変える方法と、読み返せる形に整える考え方。",
         app="hanalog"),
    dict(slug="kondate-kimaranai", topic="毎日の記録", date="2026-08-09",
         title="献立が決まらない日の決め方と、買い物を1回で終わらせる手順",
         lead="献立が決まらないのは選択肢が多すぎるからです。決める順番を固定し、売り場順の買い物リストで往復をなくします。",
         app="dandorirecipe"),
    dict(slug="densenkan-mage-sunpou", topic="仕事の道具", date="2026-08-09",
         title="電線管の曲げ寸法が現物と合わない理由と、合わせ方",
         lead="計算どおりに出しても合わないのは、ベンダーごとに実際の曲げ半径が違うためです。試し曲げ1回で自分の道具に合わせます。",
         app="magedori"),
    dict(slug="jun-alcohol-keisan", topic="毎日の記録", date="2026-08-09",
         title="純アルコール量の計算方法と、お酒の種類ごとの目安",
         lead="杯数では比べられません。純アルコール量に直すと、種類が違っても同じ物差しで比べられます。計算式と目安表。",
         app="kinshuwatch"),
    dict(slug="negoto-rokuon-houhou", topic="画面まわり・気晴らし", date="2026-08-09",
         title="iPhoneで寝言を録音する方法と、朝に見つけやすくするコツ",
         lead="普通に録ると7〜8時間の無音から探すことになります。音を検知したときだけ録る方法と、置き方の注意点。",
         app="negotouranai"),
    dict(slug="loan-karikae-nannenme", topic="お金の計算", date="2026-08-09",
         title="住宅ローンの借り換えは、何年目までなら得か",
         lead="得か損かは残り期間・残高・金利差の3つで決まります。諸費用を含めた損益分岐の出し方を整理します。",
         app="kaeseru"),
    dict(slug="harizuna-yurumi-musubikata", topic="暮らしの道具", date="2026-08-10",
         title="テントの張り綱が夜中に緩むのは、結び方のせいです",
         lead="張ったはずのロープが朝には緩んでいる。原因はロープの伸縮に結び方が追従できていないことです。場面ごとの結びの選び方を整理します。",
         app="musuberu"),
    dict(slug="hihyouji-album-genkai", topic="画像・写真", date="2026-08-10",
         title="iPhoneの「非表示」アルバムは、パスコードを別に守ってはくれません",
         lead="非表示アルバムは端末のロックと同じ鍵で開きます。家族と端末を共有していると見落としやすい仕組みと、別のパスコードで守る方法を説明します。",
         app="kagikake"),
    dict(slug="png-jpeg-touka-chigai", topic="画像・写真", date="2026-08-10",
         title="PNGとJPEGの違い — 透過が消えるのはどこか",
         lead="JPEGには透明を記録する場所がありません。透過したPNGが白くなるのは、どこかの経路でJPEGに変換されているためです。見分け方と、透過を保ったまま渡す方法をまとめます。",
         app="sukemaru"),
    dict(slug="safari-kakuchou-ugokanai", topic="X・SNSの表示", date="2026-08-10",
         title="Safariの拡張機能が動かないときに確認する順番",
         lead="iPhoneのSafari拡張機能が効かないときは、原因が5か所に分かれます。権限・対象サイト・プライベートブラウズ・低電力モード・サイト側の変更を、上から順に切り分けます。",
         app="shizukatl"),
    dict(slug="jisshitsu-nenritsu-toha", topic="お金の計算", date="2026-08-10",
         title="実質年率とは — 表面金利と何が違うのか",
         lead="表面金利が同じでも、事務手数料や保証料を含めた実質年率は変わります。金利0.1%の差が数十万円になる世界で、比べるときに見るべき数字を整理します。",
         app="kaeseru"),
    dict(slug="shukan-nannichi", topic="習慣・記録", date="2026-08-10",
         title="習慣が身につくまで何日かかるのか — 21日説の出どころ",
         lead="「21日で習慣になる」の出どころは、もともと習慣の研究ではありませんでした。実際に測った研究では中央値66日、個人差は18日から254日まで開いています。",
         app="tsuzukutodo"),
    dict(slug="sotsuron-shinchoku-gyakusan", topic="締切・進捗", date="2026-08-10",
         title="卒論・修論の進捗を、締切から逆算して管理する",
         lead="卒論がつらいのは量が多いからというより、進んでいるかが分からないからです。総量の決め方、逆算のときに引いておく日、間に合わないと分かったときの3つの選択肢。",
         app="shimekiri"),
    dict(slug="kyukanbi-nanniti", topic="毎日の記録", date="2026-08-10",
         title="休肝日の数え方と、記録すると見えてくること",
         lead="休肝日を「飲まなかった日」として数えるだけでは実態が分かりません。純アルコール量で見る方法と、飲んでしまった日の記録を消さずに残す理由をまとめます。",
         app="kinshuwatch"),
    dict(slug="sougyou-yushi-junbi", topic="起業・開業", date="2026-08-10",
         title="創業融資を受けるときに、先に用意しておくもの",
         lead="創業時は決算書がないぶん、見られる点が決まっています。事業計画・自己資金・経歴・返済能力の4つについて、申し込む前に整えておくことを整理します。",
         app="kigyouojisan"),
    dict(slug="othello-kado-x-uchi", topic="ボードゲーム", date="2026-08-10",
         title="オセロで角を取られないために — X打ちとC打ちを覚える",
         lead="角を取られたところで勝負は決まっています。そして角を取られる原因は、その手前のマスに自分から石を置いたことにあります。名前のついた2か所を覚えます。",
         app="othello"),
    dict(slug="shokanhyo-mikata", topic="お金の計算", date="2026-08-10",
         title="償還表（返済予定表）の見方 — どの列を見れば何が分かるか",
         lead="毎月同じ額を払っていても、元金と利息の内訳は返済が進むにつれて入れ替わります。3つの列だけ見れば、繰上返済をいつやるべきかまで読めます。",
         app="kaeseru"),
    dict(slug="x-osusume-tab-kesu", topic="X・SNSの表示", date="2026-08-10",
         title="Xの「おすすめ」を消して、フォロー中だけ見る",
         lead="公式アプリに「フォロー中」を既定にする設定はありません。iPhoneのSafariでできることと、サイトの作りが変わると効かなくなるという限界まで書きます。",
         app="shizukatl"),
    dict(slug="touka-gazou-shoyou-riyou", topic="画像・写真", date="2026-08-10",
         title="背景を透過した画像を、商用利用してよいか",
         lead="使えるかどうかは、アプリの規約ではなく元画像の権利で決まります。著作権・写り込んだ人や物の権利・アプリの規約を、3つ別々に切り分けます。",
         app="sukemaru"),
    dict(slug="doujinshi-nyuukou-gyakusan", topic="締切・進捗", date="2026-08-10",
         title="同人誌の入稿締切から逆算する — 印刷所の締切は完成の締切ではない",
         lead="入稿の前にデータチェックの戻り・書き出し・表紙の別締切があります。そのぶん原稿の完成日は手前になります。実際に使える日数の出し方。",
         app="shimekiri"),
    dict(slug="widget-shukan-kiroku", topic="習慣・記録", date="2026-08-10",
         title="ウィジェットで習慣を記録する — アプリを開かずに1タップにする",
         lead="続かないのは意志の問題というより、アプリを開くまでの手数です。4手を1手にする置き方と、既にある行動にくっつけるやり方。",
         app="tsuzukutodo"),
    dict(slug="bonus-hensai-settei", topic="お金の計算", date="2026-08-10",
         title="ボーナス返済は設定したほうがいいか",
         lead="毎月の返済額を下げられると聞くと魅力的に見えますが、ボーナス返済は「まとまった額を半年に一度、確実に払える」ことが前提の仕組みです。仕組みと、向き・不向きを整理します。",
         app="kaeseru"),
    dict(slug="nomikai-kotowarikata", topic="毎日の記録", date="2026-08-10",
         title="飲み会で断るときの言い方と、事前に決めておくこと",
         lead="断りにくいのは「意志が弱いから」ではなく、多くの場合その場で理由を考えているからです。先に決めておけば、当日は決めたことを言うだけで済みます。",
         app="kinshuwatch"),
    dict(slug="kojin-houjin-dochira", topic="起業・開業", date="2026-08-10",
         title="個人事業主と法人、どちらで始めるか",
         lead="「法人のほうが信用される」と聞いて最初から法人を考える人もいますが、開業の手続き・費用・社会保険の負担は大きく異なります。何を基準に選べばいいかを整理します。",
         app="kigyouojisan"),
    dict(slug="fukugyou-kaishabare", topic="起業・開業", date="2026-08-10",
         title="副業から始めるときに確認すること — 就業規則と住民税",
         lead="副業を始める前に確認しておきたいことは、大きく2つに分かれます。勤務先の就業規則で副業が認められているか、そして住民税の通知でどう扱われるかです。",
         app="kigyouojisan"),
    dict(slug="othello-shuban-saigo", topic="ボードゲーム", date="2026-08-10",
         title="オセロの終盤 — 最後に打つ側が有利になる仕組み",
         lead="オセロは64マスの盤面を、開始時に埋まっている4マスを除いた残りのマスで交互に打ち合うゲームです。終盤で「置けるマスがどちらにどれだけ残っているか」が、勝敗を大きく左右します。",
         app="othello"),
    dict(slug="shuchu-timer-tsukaikata", topic="毎日の記録", date="2026-08-10",
         title="集中が続かないときのタイマーの使い方",
         lead="「集中しよう」と思うほど続かないのはなぜか。時間を区切るタイマーが効くのは、終わりを先に決めて負担を減らすからです。区切り方の目安と、崩れたときの立て直し方を整理します。",
         app="shimekiri"),
    dict(slug="shomeishashin-haikei-sashikae", topic="画像・写真", date="2026-08-10",
         title="証明写真の背景を、白や指定色に差し替える",
         lead="証明写真の背景は「透明にする」のではなく、提出先が求める色でぴったり塗りつぶす必要があります。透過PNGを作ったあとに、もう一段階必要な理由と手順を説明します。",
         app="sukemaru"),
    dict(slug="sns-jikantai-hyouji-kirikae", topic="X・SNSの表示", date="2026-08-10",
         title="SNSを見る時間を減らす — 時間帯で表示を変える",
         lead="「見る時間を減らす」というと我慢が思い浮かびますが、効果が出やすいのは表示そのものを時間帯で変えることです。iPhoneのSafariでできる範囲と、その考え方を整理します。",
         app="shizukatl"),
    dict(slug="todo-subsc-kaikiri-chigai", topic="毎日の記録", date="2026-08-10",
         title="サブスクのToDoアプリと買い切りの違い",
         lead="ToDoアプリを選ぶとき、価格の高い安いだけで比べると失敗しやすいです。サブスクと買い切りは、そもそも何にお金を払っているのかが違います。",
         app="tsuzukutodo"),
    dict(slug="kaigi-rokuon-mojiokoshi-chuui", topic="仕事の道具", date="2026-08-10",
         title="会議の録音を文字起こしするときに気をつけること",
         lead="会議を録音して文字起こしすれば議事録が楽になりますが、注意すべき点は精度だけではありません。録音そのものの許可や、音声データの扱いも含めて整理します。",
         app="sagaseru"),
    dict(slug="rokuon-choujikan-settei", topic="仕事の道具", date="2026-08-10",
         title="iPhoneで長時間録音するときの設定と容量の目安",
         lead="長時間の録音で困るのは、音質そのものより途中で止まることと容量が足りなくなることです。事前に決めておけば防げる設定と、時間から容量を見積もる目安を説明します。",
         app="sagaseru"),
    dict(slug="invoice-kisai-jikou", topic="仕事の道具", date="2026-08-10",
         title="インボイス制度で、請求書に必要な記載事項",
         lead="適格請求書（インボイス）には、決まった項目がすべて揃っている必要があります。一般的に必要とされる記載項目を整理します。個別の判断は国税庁の公表資料または税理士にご確認ください。",
         app="hitoriinvoice"),
    dict(slug="gensenchoushu-seikyusho-kakikata", topic="仕事の道具", date="2026-08-10",
         title="源泉徴収がある場合の請求書の書き方",
         lead="源泉徴収は支払う側が差し引いて納める仕組みで、請求書に金額を書く義務は必須ではありません。それでも内訳を分けて書いておくと、入金額の食い違いを防げます。",
         app="hitoriinvoice"),
    dict(slug="tsukurioki-dandori-junban", topic="毎日の記録", date="2026-08-10",
         title="作り置きの段取り — 火を使う順番で時間が変わる",
         lead="同じ品数を作っても、通しの時間が大きく変わるのは火を使う順番のせいです。待ち時間に他の作業を重ねる段取りの組み方を説明します。",
         app="dandorirecipe"),
    dict(slug="recipe-hozon-atode-sagasu", topic="毎日の記録", date="2026-08-10",
         title="紙のレシピやスクショを、あとで探せる形にする",
         lead="レシピが増えて困るのは量そのものより、あとで探せないことです。撮った・保存しただけでは検索できません。探せる形で残す考え方を説明します。",
         app="dandorirecipe"),
    dict(slug="onsei-nikki-tsuzukekata", topic="毎日の記録", date="2026-08-10",
         title="話して残す日記 — 書けない日でも続く記録の作り方",
         lead="日記を書く時間を確保しようとして、結局続かない人は多いです。実は必要なのは時間の長さではなく、手や目がふさがっていても記録できる「場面」です。",
         app="hanalog"),
    dict(slug="mojiokoshi-seido-naosu", topic="毎日の記録", date="2026-08-10",
         title="文字起こしの精度が出ないときに直すところ",
         lead="文字起こしがうまくいかないと「アプリの精度が低い」と思いがちですが、実際にずれの多くは録り方に原因があり、直せる範囲も広いです。",
         app="hanalog"),
    dict(slug="receipt-hozon-kikan", topic="仕事の道具", date="2026-08-10",
         title="レシートの保存期間と、電子で残すときの決まり",
         lead="レシートを家計簿アプリで撮ったあと、紙をどれくらい残しておけばいいのか迷う人は多いです。家庭で使う場合と、確定申告に使う場合とでは、考え方が違います。",
         app="oboerukakeibo"),
    dict(slug="shishutsu-dake-kakeibo", topic="仕事の道具", date="2026-08-10",
         title="支出だけの家計簿という考え方",
         lead="家計簿アプリの多くは、収入・支出・予算・貯蓄目標をまとめて管理しようとします。しかし多くの人にとって、本当に必要なのは支出だけの記録です。",
         app="oboerukakeibo"),
    dict(slug="densenkan-offset-mage-keisan", topic="仕事の道具", date="2026-08-10",
         title="電線管のオフセット曲げ（S字曲げ）の計算 — 曲げ量とマーキングの出し方",
         lead="配管が障害物にぶつかるときに使うのがオフセット曲げ（S字曲げ）です。オフセット量と曲げ角度から、2か所の曲げ位置をどう出すかを整理します。",
         app="magedori"),
    dict(slug="negogoto-kiroku", topic="毎日の記録", date="2026-08-12",
         title="寝言はなぜ出るのか — 記録してみて分かること",
         lead="寝言は珍しい体質ではなく、眠りの浅い時間帯に多くの人へ起きる現象です。仕組みと、自分で確かめる方法、注意したほうがよいケースを分けて説明します。",
         app="negotouranai"),
    dict(slug="kyouikuloan-shougakukin-hikaku", topic="お金の計算", date="2026-08-14",
         title="教育ローンと奨学金の返済を、同じ物差しで比べる",
         lead="教育ローンと奨学金は、どちらも進学のお金を借りる仕組みですが、借りる人・返す人・返済が始まる時期がそもそも違います。混同したまま比べると判断を誤ります。違いを整理し、比べるときに見るべき物差しをまとめます。",
         app="kaeseru"),
    dict(slug="hikkoshi-nizumi-rope-kotei", topic="暮らしの道具", date="2026-08-16",
         title="引っ越しで荷物をロープで固定する — 締まる結びとほどける結び",
         lead="走行中に緩まないことと、着いたときにほどけることは別の条件です。締め込む段階と仕上げの段階を分けて考える、荷締めの結び方を整理します。",
         app="musuberu"),
    dict(slug="shashin-1mai-dake-miseru", topic="画像・写真", date="2026-08-16",
         title="写真を人に見せるとき、他の写真を見られないようにする",
         lead="1枚だけ見せるつもりが、スワイプで前後の写真まで見られてしまう。標準の写真アプリの仕組みと、その場で見せる前にできる対策を整理します。",
         app="kagikake"),
    dict(slug="othello-ishikazu-yuuri-tokakiranai", topic="ボードゲーム", date="2026-08-17",
         title="オセロで石の数が多い方が勝っているとは限らない",
         lead="対局の途中で自分の石が少ないと不安になりますが、オセロは終局までの手で盤面が入れ替わるゲームです。中盤の石数と、最終的な勝敗の関係を整理します。",
         app="othello"),
    dict(slug="aoiro-shinkoku-65man-kojo-youken", topic="起業・開業", date="2026-08-17",
         title="青色申告特別控除、65万円を受けるための条件",
         lead="青色申告にすると控除が受けられると聞いても、金額が10万円・55万円・65万円のどれになるかは条件で変わります。65万円を受けるための要件と、今後の変更点を整理します。",
         app="kigyouojisan"),
    dict(slug="densenkan-mage-hankei-saisho", topic="仕事の道具", date="2026-08-18",
         title="電線管の曲げ半径の最小値 — 内径の何倍まで曲げていいか",
         lead="曲げ角度と位置は計算どおりに出せても、どこまで小さい半径で曲げていいかは別の話です。内線規程が定める「内径の6倍以上」という基本の考え方と、小さく曲げすぎたときに起きることを整理します。",
         app="magedori"),
    dict(slug="negoto-rokuon-doushitsu-purabashii", topic="毎日の記録", date="2026-08-18",
         title="寝言を録音すると、隣で寝ている人の声も入ってしまう",
         lead="自分の寝言を録るつもりでも、同じ部屋で寝ている人の声や会話が一緒に録れてしまうことがあります。マイクが音を拾う仕組みと、置き方の工夫、同居している人に伝えておきたいことを説明します。",
         app="negotouranai"),
    dict(slug="jitaku-jimusho-kaji-anbun", topic="起業・開業", date="2026-08-19",
         title="自宅を事務所にする個人事業主の「家事按分」の考え方",
         lead="家賃や電気代のように、プライベートと事業の両方で使っている支出は、事業で使った割合だけを経費にできます。これが家事按分です。何を対象にできるか、どう割合を決めるかを整理します。",
         app="kigyouojisan"),
    dict(slug="othello-kanzen-kaiseki", topic="ボードゲーム", date="2026-08-19",
         title="オセロに「必勝法」はあるのか — 2023年の完全解析が示したこと",
         lead="2023年、オセロというゲームそのものの結論が計算によって示されました。「必勝法」があるゲームなのか、それとも「引き分けにしかならない」ゲームなのか。発表された内容と、対人戦での意味を整理します。",
         app="othello"),
]


def shared():
    src = (ROOT / "guides" / "transparent-png-white.html").read_text()
    head = src.split('<header class="site-head">')[1].split("</header>")[0]
    foot = src.split('<footer class="site-foot">')[1].split("</footer>")[0]
    return head, foot


def sync_shared():
    head, foot = shared()
    for p in sorted((ROOT / "guides").glob("*.html")):
        s = p.read_text()
        s = re.sub(r'(<header class="site-head">).*?(</header>)',
                   lambda m: m.group(1) + head + m.group(2), s, flags=re.S)
        s = re.sub(r'(<footer class="site-foot">).*?(</footer>)',
                   lambda m: m.group(1) + foot + m.group(2), s, flags=re.S)
        p.write_text(s)
        print("共通パーツを同期:", p.name)


def index_page():
    head, foot = shared()
    rows = []
    for g in GUIDES:
        a = BY_SLUG[g["app"]]
        rows.append(
            f'      <a class="work rise mt-l" href="/guides/{g["slug"]}">\n'
            f'        <img class="work-icon" src="/assets/icons/{a["slug"]}.png" width="512" height="512"'
            f' alt="" loading="lazy" decoding="async">\n'
            f'        <div>\n'
            f'          <p class="meta">{g["date"]} · {g["topic"]}</p>\n'
            f'          <h3>{g["title"]}</h3>\n'
            f'          <p>{g["lead"]}</p>\n'
            f'          <span class="go">続きを読む →</span>\n'
            f'        </div>\n'
            f'      </a>')
    body = "\n\n".join(rows)

    items = "".join(
        f'    {{ "@type": "ListItem", "position": {i+1}, "url": "https://tokyo357.com/guides/{g["slug"]}" }}'
        + (",\n" if i < len(GUIDES) - 1 else "\n") for i, g in enumerate(GUIDES))

    return f"""<!DOCTYPE html>
<html lang="ja" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>解決のヒント ｜ 株式会社サウナ / Sauna Inc.</title>
<meta name="description" content="iPhoneでよくある「うまくいかない」を、原因から切り分けて説明します。背景透過が白くなる、タイムラインが時系列に戻らない、締切に間に合わないなど。株式会社サウナ（Sauna Inc.）がアプリ開発の過程で調べたことをそのまま公開しています。">
<link rel="canonical" href="https://tokyo357.com/guides/">
<meta name="theme-color" content="#14100E">
<meta property="og:type" content="website">
<meta property="og:site_name" content="株式会社サウナ / Sauna Inc.">
<meta property="og:title" content="解決のヒント ｜ 株式会社サウナ">
<meta property="og:description" content="iPhoneでよくある「うまくいかない」を、原因から切り分けて説明します。">
<meta property="og:url" content="https://tokyo357.com/guides/">
<meta property="og:image" content="https://tokyo357.com/assets/og/home.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/style.css?v={VER}">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "解決のヒント",
  "url": "https://tokyo357.com/guides/",
  "itemListElement": [
{items}  ]
}}
</script>
</head>
<body>
<a class="skip" href="#main">本文へスキップ</a>

<header class="site-head">{head}</header>

<main id="main" class="doc">
  <div class="wrap">

    <div class="doc-head">
      <p class="updated">SAUNA INC. ／ GUIDES</p>
      <h1>解決のヒント</h1>
      <p class="lede">アプリを作るとき、私たちはまず既存アプリの低評価レビューを読み込んで、
      利用者が実際にどこで詰まっているかを数えます。そこで分かったことは、アプリを使う人だけでなく、
      同じ問題で困っている人すべてに役立つはずです。調べたことをそのまま公開しています。</p>
    </div>

{body}

  </div>
</main>

<footer class="site-foot">{foot}</footer>

<script src="/assets/site.js?v={VER}" defer></script>
</body>
</html>
"""



def require_todays_ranks():
    """ランキングの記録を飛ばして記事だけ足すのを防ぐ。

    プロンプトで「必ず最初に実行する」と指示しても2日連続で飛ばされたため、
    仕組みで止める。記事を足すには check_ranks.py を先に走らせるしかない。
    どうしても回避したいときだけ SKIP_RANK_GUARD=1 を付ける。
    """
    import datetime
    import json
    import os

    if os.environ.get("SKIP_RANK_GUARD") == "1":
        return
    f = ROOT / "tools" / "ranks.json"
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    checked = None
    if f.exists():
        try:
            data = json.loads(f.read_text())
            checked = {v.get("checked") for v in data.values()}
        except Exception:
            checked = None
    if not checked or today not in checked:
        raise SystemExit(
            f"\n中断しました。今日（{today}）のランキングが記録されていません。\n"
            f"  現在の記録: {sorted(checked) if checked else 'なし'}\n\n"
            f"先にこれを実行してください:\n"
            f"  python3 tools/check_ranks.py {today}\n\n"
            f"順位の記録は毎日取らないと最高順位を取り逃します。\n"
            f"（どうしても回避する場合のみ SKIP_RANK_GUARD=1 を付ける）\n"
        )


def main():
    require_todays_ranks()
    sync_shared()
    (ROOT / "guides" / "index.html").write_text(index_page())
    print("生成: guides/index.html (/guides/)")


if __name__ == "__main__":
    main()
