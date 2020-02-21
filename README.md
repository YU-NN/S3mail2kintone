# loperaio kintone
## 商談メールから情報を抽出し、kintoneアプリに自動登録
### 目次
- 概要
- どんな感じで登録されるのか？？
- フローの各段階の設定についての説明
- 商談ステータス−`確認用`から本番用への移行の仕方
- 送信されてくるメールの店舗名と登録されている店舗名が異なる事への対応の仕方

### 概要
- 送られてきた商談メールから「店舗名」「車両名」「お客様名」「メール本文」を取得し、<br>Kintoneの「商談ステータス−`確認用`」に登録する。

- 送られてくる`商談メールは2種類`あり、「グーネット」と「カーセンサー」。

- ざっくりとした流れ(フロー)は、<br>`メール送信` → `SES` → `S3` → `Lambda` → `Kintoneアプリ`

### どんな感じで登録されるのか？？
送られてくる2種類のメール、グーネットとカーセンサーの各フォーマットと、情報の取り出し方を示す。<br>


「グーネット」の場合、<br>
- 「店舗名」は「ロペライオグループ　ロペシティセントラルスクエア店／（株）ロペライオ　御中」の部分<br>
- 「お客様名」は「■お客様情報」の「お名前：」の部分<br>
- 「車両名」は「■車両情報」の「依頼車輌：」の部分<br>
から取り出している。<br>

```
■■■━━━━━━━━━━━━━━━━━━━━━━━
グーネット中古車見積りサービス ご回答依頼のお知らせ
━━━━━━━━━━━━━━━━━━━━━━━━■■■
■問合せ番号： UC2019122906021919
■問合せ方法： パソコン
■車庫証明：
■納車情報：
■下取車情報：
■見積・問合せ情報
依頼種別： 見積り
■車輌情報
依頼車輌： メルセデス・ベンツ Ｍ・ベンツ ＣＬＡ１８０　ＡＭＧスタイル　ＡＭＧプレミアムＰＫＧ　禁煙
年式： 2018年
走行距離： 1.1万K
価格： 285.9万円
カラー： ポーラーホワイト
管理番号：
■お客様情報
お名前： 本部
住所： 埼玉県戸田市
年代：
性別：
購入予定時期：
希望時間帯：
ロペライオグループ　ロペシティセントラルスクエア店／（株）ロペライオ　御中
いつもお世話になっております。
グーネットお客様センターです。
グーネット中古車等で貴社の掲載車両をご覧になったお客様より
見積り・問合せ依頼がございましたのでご案内します。
下記アドレスからMOTORGATEを開き、
上記問合せ番号のお客様へのご回答処理をお願い致します。
正式回答の自動回答設定をしている車輌につきましては、
追加連絡にて、質問に対する回答をお願い致します。
http://motorgate.jp/
※問合せ依頼に対するご回答は、お客様がお待ちですので、
ご依頼後48時間以内の処理をお願い致します。
！▲このメールに対する返信は受付致しかねます▲！
_______________________________________________________
(株)プロトコーポレーション　PROTO CORPORATION
 ◇PROTOサポートセンター
 │TEL：050-3786-4400
 │mail：customer_c@goo-net.com
_______________________________________________________
```

「カーセンサー」の場合、<br>
- 「店舗名」は「ロペライオグループ　ロペシティセントラルスクエア店／（株）ロペライオ　御中」の部分<br>
- 「お客様名」は「■お客様情報」の「お名前：」の部分<br>
- 「車両名」は「＜新着問い合わせ物件＞」の「【】」の中の部分<br>
から取り出している。<br>

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
　◆ C-MATCH　お問合せが届きました ◆
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ロペライオグループ／ロペシティ西宮／（株）うかいや様
カーセンサーnet C-MATCHをご利用いただき、ありがとうございます。
以下のようにカスタマーからの問合わせが入っています。
C-MATCHでご確認の上、ご回答お願いします。
　　　　　　　↓
https://c-match.carsensor.net/
C-MATCH携帯版はこちら
http://c-match.carsensor.net/m/
◎新着件数:1件
＜新着問合せ物件＞
https://www.carsensor.net/cgi-bin/CS/CSif3.cgi?CMDCD=1&BKKN=VU2720011124&SHOP=316066014U
【レンジローバーイヴォーク　295.9万円　H26　白】
■依頼者　　: 中川皓之(大阪府)
■依頼種別　: 【見】
■内容詳細　:
■カーセンサーからの追加情報■性別：不明　年代：不明
-----------------------------------
＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
　カーセンサー お客様サポートセンター
　　営業時間　（平日）　10:00～20:00
　　　　　　　（土日祝）10:00～18:00
　TEL 0120-757-839（または096-311-5544）
　FAX 096-311-5590
　Mailto:support@carsensor.net
　　株式会社リクルートマーケティングパートナーズ
＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
```
