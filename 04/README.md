# キャリアバンクジョブサーチのスクレイピング

## スクレイピングフロー
1. https://careerbank-jobsearch.com/page/{page_number}にアクセス
2. 1ページ50件の求人情報を参照
3. 全てのページで処理を行う
3. 全ての求人情報をcsvとして出力
4. csvを読み取り1件ずつ詳細ページの移動しDBを更新する

## 実行方法
### ライブラリインストール
必要なライブラリをインストールしてください。
その際はグローバル空間へのダウンロードにならないようvenvなどで仮想環境を作成してください。

参考リンク: https://qiita.com/fiftystorm36/items/b2fd47cf32c7694adc2e
```sh
pip3 install -r requirements.txt
```

### Cookieの取得
まずはブラウザ上でキャリアバンクジョブサーチに手動でログインしてください。
ログインした状態でブラウザの開発ツールのNetworkタブを開いてください。そこの一番上にあるネットワークをクリックし以下の手順でCookieを確認します。
Headersタブ > Request Headersセクション > Cookie
参考: https://qiita.com/shizen-shin/items/b619586a293de8cfe7da

Cookieの右側に「wordpress_test_cookie=...」から始まる文字列があるのでそれをコピーして取っておいてください。

### スクレイピング実行
以下何度か「コマンド実行」「ファイル出力」を行います。理由としては以下の3点です。
- 処理件数が多いのでPCのメモリサイズによっては全ての処理を行うと処理が途中で中断されてしまう可能性があること
- ログインセッションが切れる場合があること
- サイトの処理が高速ではないのでスクレイピングにかなりの時間がかかること


このコマンドは求人一覧ページから全ての求人の基本情報を取得しcsv出力します。
```sh
python3 list.py -p <求人一覧のページ数> -c "<先ほどコピーしたcookie>"
```
※ 求人一覧のページ数は2025/02/16時点で138ですが、実行時のページ数を入力ください。
実行すると `job_list.csv` というファイルが出力されます。このファイルは次のコマンド実行時に利用されます。

このコマンドはcsvファイルを読み取り求人詳細ページから情報を取得しcsv出力します。
```sh
python3 detail.py -f job_list.csv -m <処理するレコード数>　-c "<先ほどコピーしたcookie>"
```
※ `-m <処理するレコード数>`を省略すると10件のレコードが処理されます。
実行すると `output_jobs.csv` というファイルが出力されます。このファイルは次のコマンド実行時に利用されます。

このコマンドはcsvファイルを読み取りデータベースにデータを挿入します。
```sh
python3 insert.py output_jobs.csv
```

`insert.py` の実行前にファイル内のdatabaseの接続情報を修正してください。

```
conn = psycopg2.connect(
        dbname="mydatabase",
        user="myuser",  # ユーザー名
        password="mypassword",  # パスワード
        host="localhost",  # ホスト
        port="5432",  # ポート
    )
```


## テーブル項目と画面要素のマッピング
id -> 自動採番
(一覧)link -> 求人一覧のtitleのaタグ or 詳細を見るボタンのaタグ
(一覧)title -> 求人一覧のタイトル
detail_fetched -> FALSE
job_status -> 空でデフォルト値を代入
(一覧)company_name -> 求人一覧の企業名
(詳細)company_url -> 詳細ページの表のホームページ
(一覧)industry -> 求人一覧の業界
category -> 空文字
(一覧)salary_range -> 求人一覧の年収
(一覧)work_location -> 求人一覧の想定勤務地詳細
(一覧)application_qualifications -> 求人一覧の応募資格
(詳細)job_description -> 詳細ページの表の仕事内容
screening_speed -> 空でデフォルト値を代入
(一覧)planned_hires -> 求人一覧の募集人数
pass_rate -> 空でデフォルト値を代入
(一覧)age_requirement_min -> 求人一覧の年齢(数値のみを取得し、そのうちの最小の値)
(一覧)age_requirement_max -> 求人一覧の年齢(数値のみを取得し、そのうちの最小の値)
gender_requirement -> 詳細ページの表の性別('性別不問'/'男性'/'女性'/'女性限定'等にする)
nationality_requirement -> 詳細ページの表の外国籍の必要資格・経験(外国籍OK'/'外国籍NGにする)
requirement_tags -> 空文字
position_details -> 空文字
position_level -> 空文字
establishment_year -> 詳細ページの表の設立年月日
company_phase -> 空文字
employees_count -> 詳細ページの表の従業員数
listing_status -> 空文字
company_address -> 詳細ページの表の本社所在地
holidays_count -> 詳細ページの表の休日休暇(年間XXX日を切り出す)
regular_holidays -> 空文字
benefits -> 詳細ページの表の福利厚生
smoking_measures -> 詳細ページの表の受動喫煙対策
casual_interview -> 詳細ページの表の選考内容の中に「カジュアル面談の有無 : 状況に応じてある」の場合
company_briefing -> 詳細ページの表の選考内容の中に「会社説明会の有無: あり」の場合
aptitude_test -> 詳細ページの表の選考内容の中に「適性テストの有無: あり」の場合
selection_flow -> 詳細ページの表の選考内容の中の「〈選考フロー〉」から「〈補足情報〉」の間の文字列
fee_text -> 詳細ページの表の成功報酬条件
success_point -> 空文字
payment_terms -> 空文字
refund_policy -> 詳細ページの表の返金規定（紹介手数料）
theoretical_salary_policy ->  詳細ページの表の理論年収の定義
body -> 詳細ページのHTML
body_text -> 詳細ページのHTML.text()
reproduce_prohibit -> 詳細ページのその他備考に「転載禁止」が含まれているか
handling_agency -> 空文字
posted_date -> 詳細ページの求人更新日
pr_points -> 詳細ページの会社の特徴
organization_structure -> 空文字
document_rejection_reasons -> 空文字
high_likelihood_hire -> 詳細ページの表の内定者事例
interview_rejection_reasons -> 詳細ページの表の面接お見送り理由
agent_info_document_points -> 
agent_info_interview_first -> 
agent_info_interview_final -> 
created_at
updated_at