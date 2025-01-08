## Get Starting
README.mdファイルがあるディレクトリで全てのコマンドは実行してください。

pythonの仮想環境を作ります。目的はpythonのライブラリをPCのグローバルな環境にインストールするのではなく、一時的なサンドボックスにインストールするためです。
```
python3 -m venv venv
source venv/bin/activate
```

仮想環境が有効化された状態で以下のコマンドで関連ライブラリをインストールします。
```
pip3 install -r requirements.txt
```

以下のスクリプトを実行するとそれぞれダンボール・ベーキングペーパー・緩衝材のスクレイピングとcsvの出力が行われます。

```
# ダンボールのスクリプト同時実行
python3 cmd_card_board_askul.py & python3 cmd_card_board_monotaro.py & python3 cmd_card_board_tanomail.py & python3 cmd_card_board_kaunet.py & wait

# ベーキングペーパーのスクリプト同時実行
python3 cmd_baking_paper_askul.py & python3 cmd_baking_paper_monotaro.py & python3 cmd_baking_paper_tanomail.py & python3 cmd_baking_paper_kaunet.py　& wait

# 緩衝材のスクリプト同時実行
python3 cmd_cushioning_package_askul.py & python3 cmd_cushioning_package_monotaro.py & python3 cmd_cushioning_package_tanomail.py & python3 cmd_cushioning_package_kaunet.py & wait
```

※ もし「たのめーる」のダンボールのcsvのみ出力したい、という場合

```
python3 cmd_card_board_tanomail.py
```

のようにコマンドを個別に実行可能です。

## python環境構築
https://prog-8.com/docs/python-env
https://qiita.com/toranoko92114/items/08b287e54bdc36943375

## 実行環境
Python 3.13.0

## 注意
これは2024年12月24日現在の「たのめーる」「モノタロウ」「アスクル」「カウネット」のhtml構造に依存したクローラーです。
https://www.tanomail.com/
https://www.monotaro.com/
https://www.askul.co.jp/
https://www.kaunet.com/


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
- [x] カウネット
  - [x] ダンボール
  - [x] ベーキングペーパー
  - [x] プチプチ(エアパッキン)
  - [x] 追加プロパティの取得
  - [x] 今後の修正用のモジュール化
