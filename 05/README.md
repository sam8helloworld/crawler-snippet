# ChatGPTの自動実行

## 実行フロー
1. ブラウザを開く
2. 指定されたURLを開く
    - チャットIDが指定されている場合はチャット画面を開く
    - チャットIDが指定されていない場合は新規チャット画面を開く
3. ファイルで指定されたプロンプトをテキストエリアに入力する
4. Enterキーで実行する
5. 実行完了するまで待つ
    - 実行前に現状の `article.[data-testid="conversation-turn-X"]` の最後部の要素を取得し現状の最新のturn数を取得する
    - 実行後はn秒毎に `article.[data-testid="conversation-turn-X+1"]` 内の `button[data-testid="copy-turn-action-button"]` が表示されているか確認する
        - Deep Researchが指定された場合は3分おきに完了しているかhtml要素で確認する
        - o1 proが指定された場合は1分おきに完了しているかhtml要素で確認する
        - その他のモデルが指定された場合は10秒おきに完了しているかhtml要素で確認する
6. 応答結果をターミナルに表示する
    - mdモードが指定された場合はコピーアイコンでclipboardにmdを貼り付けてその内容を表示する
    - mdモードが指定されない場合は応答のinnerTextを表示する
7. プログラムを終了する