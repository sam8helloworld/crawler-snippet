from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import sys
from bs4 import BeautifulSoup
import re

# Google検索のベースURL（「事業所 住所」の形式で検索する）
BASE_URL = "https://www.google.com/search?q={}"

# Seleniumのオプション設定
options = Options()
options.add_argument("--no-sandbox")  # サンドボックスモードを無効化（コンテナ環境向け）
options.add_argument("--disable-dev-shm-usage")  # メモリ使用量の制限を解除
options.add_argument("--start-maximized")  # ブラウザを最大化して起動
options.add_argument("--disable-blink-features=AutomationControlled")  # 自動化検出回避
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)  # User-Agentを指定して自動化検出を回避
options.add_argument("--remote-debugging-port=9222")  # リモートデバッグのポートを指定

# Chrome Webドライバー の インスタンスを生成
driver = webdriver.Chrome(options=options)

# ユーザーにCSVファイル名の入力を求める
csv_file = input("処理するCSVファイル名を入力してください: ")

# CSVファイルを読み込む
df = pd.read_csv(csv_file)

# 「事業所 住所」列が存在するか確認
if "事業所 住所" not in df.columns:
    print("エラー: CSVに「事業所 住所」列がありません")
    sys.exit(1)

# 各行ごとに処理を実施
for index, row in df.iterrows():
    full_address = str(row["事業所 住所"])  # 「事業所 住所」列の値を取得（文字列に変換）

    # 半角空白がある場合は、その前の部分のみを取得
    address = full_address.split(" ")[0]

    # BASE_URLを使って検索URLを作成
    search_url = BASE_URL.format(address)

    # 「郵便番号」列が空白の場合のみ処理
    if pd.isna(row.get("郵便番号", None)) or row["郵便番号"] == "":
        # SeleniumでGoogle検索を実行
        driver.get(search_url)

        try:
            # 指定したクラス（.aiAXrc）を待ち、HTMLを取得
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "aiAXrc"))
            )
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # 郵便番号を含むテキストを取得
            element = soup.find(class_="aiAXrc")
            if element:
                text = element.get_text()

                # 〒XXX-XXXX というフォーマットの郵便番号を抽出
                match = re.search(r"〒(\d{3}-\d{4})", text)
                if match:
                    zipcode = match.group(1)
                    df.at[index, "郵便番号"] = zipcode  # 取得した郵便番号を「郵便番号」列に格納

        except Exception as e:
            print(f"エラー: {address} の郵便番号取得に失敗しました - {e}")

# 更新されたデータフレームをCSVファイルに出力
output_file = "output.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")  # Excel対応のエンコーディング

print(f"処理が完了しました。結果は {output_file} に保存されました。")

# ブラウザを閉じる
driver.quit()
