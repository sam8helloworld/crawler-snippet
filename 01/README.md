## Get Starting
README.mdファイルがあるディレクトリで全てのコマンドは実行してください。

```
pip3 install -r requirements.txt
```

```
# ベーキングペーパーのスクリプト同時実行
python3 cmd_baking_paper_askul.py & python3 cmd_baking_paper_monotaro.py & python3 cmd_baking_paper_tanomail.py & wait

# ダンボールのスクリプト同時実行
python3 cmd_card_board_askul.py & python3 cmd_card_board_monotaro.py & python3 cmd_card_board_tanomail.py & wait

# 緩衝材のスクリプト同時実行
python3 cmd_cushioning_package_askul.py & python3 cmd_cushioning_package_monotaro.py & python3 cmd_cushioning_package_tanomail.py & wait
```

## python環境構築
https://prog-8.com/docs/python-env
https://qiita.com/toranoko92114/items/08b287e54bdc36943375

## 実行環境
Python 3.13.0

## 注意
これは2024年12月24日現在の「たのめーる」「モノタロウ」「アスクル」のhtml構造に依存したクローラーです。
https://www.tanomail.com/
https://www.monotaro.com/
https://www.askul.co.jp/


たのめーるがhtml構造の変更を伴う修正をサイトに行った場合、このコードの動作は保証されません。

## 2025-01-06日現在の進捗
- [x] たのめーる
  - [x] ダンボール
  - [x] ベーキングペーパー
  - [x] プチプチ(エアパッキン)
  - [x] 追加プロパティの取得
  - [x] 今後の修正用のモジュール化
- [x] モノタロウ
  - [x] ダンボール
  - [x] ベーキングペーパー
  - [x] プチプチ(エアパッキン)
  - [x] 追加プロパティの取得
  - [x] 今後の修正用のモジュール化
- [x] アスクル
  - [x] ダンボール
  - [x] ベーキングペーパー
  - [x] プチプチ(エアパッキン)
  - [x] 追加プロパティの取得
  - [x] 今後の修正用のモジュール化
