## Getting Started
Sheinの商品検索結果ページではSeleniumのテストブラウザでは画像の表示などが不安定になるので実ブラウザを操作することにする

```sh
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=./temp
```

```sh
python3 shein.py
```