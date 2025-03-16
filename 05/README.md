# ChatGPTの自動実行

## 実行準備
まずは以下を参考にpythonの仮想環境を構築してください。
参考: https://qiita.com/fiftystorm36/items/b2fd47cf32c7694adc2e

仮想環境を起動後以下のコマンド実行して必要なライブラリをインストールしてください。
```
python3 install -r requirements.txt
```

このスクリプトでは実際にブラウザを開くのでPCにインストールされているChromeの実行ファイルを指定する必要があります。
`cmd.py` の以下の箇所をWindowsかMacかで修正してください。

```python
chrome_path = r'"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"'
```

**Windowsの場合**
Chromeのexeファイルへのパスを指定してください。
以下のような場所にあります。
`C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`

**Macの場合**
基本的には以下のパスを指定します。
`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` 


## 実行方法
ChatGPTとの対話を行う際は以下のコマンドを実行してください。
```
python3 cmd --file <プロンプトが記載されたファイルパス>
```

※ 必要に応じて以下のオプションをコマンドに追加してください。
+ --model=<モデル名> : ChatGPTで実行可能なモデル名を指定してください 
+ --research : このオプションを追加するとDeep Researchモードで実行します
+ --md : このオプションを追加するとChatGPTの回答をmarkdown形式で出力します
+ --chatid=<チャットID> : 特定のチャットで対話を行う場合はこのオプションを指定してください

初回実行時はChatGPTへのログインが求められるので手動でログインしてください。2回目以降はログインセッションが保持されます。
ログインセッションは `user_data_dir_temp` というディレクトリに出力され、プログラムから参照されます。

### 注意点
以前以下のような質問を頂きました。
> コマンドを実行してからログインするといフローですが、逆にログインした状態でコマンドを実行するというフローは難しいのでしょうか。

普段利用しているブラウザでChatGPTにログインした状態でコマンドを実行するという旨と理解しています。
Seleniumの仕様として1つのGoogleアカウント(=Profile)に対して開かれているブラウザでログインしている間は、SeleniumではそのProfileを利用できない、という仕様があります。
なので対応としては以下の2通りがあります。
- コマンド実行時に利用するProfileでログインしているChromeを閉じる
- 一時的にprofileを作成し、ログインする(一度ログインすると2度目以降はセッションが切れるまでログイン不要)

前者だとブラウザを毎回閉じないとエラーになってしまうので、今回は後者を採用しています。

### 対応しているmodel名
- gpt-4o
- gpt-4o-jawbone
- gpt-4-5
- o1
- o3-mini
- o3-mini-high
- o1-pro
- gpt-4o-mini
- gpt-4


## 今後の利用想定

> 想定利用としては、ChatGPTの応答に応じて（for文等で）ルールベースで次のプロンプトを入力して、繰り返し対話をすることを想定しておりますが、今回は1ターンのみの実装で問題ございません。関数として切り出せる形で実装していただけますと幸いです。

`chat_gpt_automation.py` というファイルに `ChatGPTAutomation` というclassを作成しています。
このclassはChatGPTへの操作を関数として切り出しているものです。

今後の想定としてはあるルールベースでChatGPTの応答に対してさらにプロンプトを入力し、実行するというフローを想定されていると思います。
以下のように `ChatGPTAutomation` を利用して都度必要な処理をご記載ください。

```python
chatgpt = ChatGPTAutomation()

chatgpt.toggle_research() # Deep ResearchをON
chatgpt.change_model() # モデル名を指定
chatgpt.send_prompt() # プロンプトを送信し結果を待つ
result = chatgpt.last_response_markdown() # 応答結果を取得する

## ~~~ resultを確認し次のプロンプトを選ぶ処理 ~~~

chatgpt.toggle_research() # Deep ResearchをON
chatgpt.change_model() # モデル名を指定
chatgpt.send_prompt() # プロンプトを送信し結果を待つ
result = chatgpt.last_response_markdown() # 応答結果を取得する
```