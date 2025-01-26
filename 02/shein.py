from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
from typing import List
from product import Product
import sys

from bs4 import BeautifulSoup

BASE_URL = "https://jp.shein.com/pdsearch/%E3%83%97%E3%83%AD%E3%82%B8%E3%82%A7%E3%82%AF%E3%82%BF%E3%83%BC/?ici=s1%60EditSearch%60%E3%83%97%E3%83%AD%E3%82%B8%E3%82%A7%E3%82%AF%E3%82%BF%E3%83%BC%60_fb%60d0%60PageHome&search_source=1&search_type=all&source=sort&src_identifier=st%3D2%60sc%3D%E3%83%97%E3%83%AD%E3%82%B8%E3%82%A7%E3%82%AF%E3%82%BF%E3%83%BC%60sr%3D0%60ps%3D1&src_module=search&src_tab_page_id=page_home1737861475186&sort=11&sourceStatus=1&force_suggest=1&page={}"

options = Options()
# 信頼性の高いブラウザ環境を作る設定
options.add_argument("--no-sandbox")  # サンドボックスモードを無効化
options.add_argument("--disable-dev-shm-usage")  # メモリ使用量の制限解除
options.add_argument("--start-maximized")  # ブラウザを最大化
options.add_argument("--disable-blink-features=AutomationControlled")  # 自動化検出回避
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)  # User-Agentを指定
# options.add_argument("--incognito")

options.add_argument("--remote-debugging-port=9222")

# Chrome Webドライバー の インスタンスを生成
driver = webdriver.Chrome(
    options=options,
)

driver.get(BASE_URL)

print("ブラウザを開きました。手動操作を行い、完了したらEnterキーを押してください。")
input("操作が完了したらEnterを押してください...")

# 商品情報を格納するリスト
products: List[Product] = []

for page_number in range(1, 4):
    url = BASE_URL.format(page_number)

    # WebドライバーでSheinの商品検索ページを起動
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#product-list-v2"))
    )
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

    html = driver.page_source.encode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # 商品リストの取得
    product_tags = soup.select(
        ".product-card.multiple-row-card.j-expose__product-item.hover-effect.product-list__item.product-list__item-new"
    )

    # 各商品を処理
    for index, product_tag in enumerate(product_tags):
        print(f"{index}個目の商品")
        try:
            # 商品リンクを取得
            product_link_tag = product_tag.select_one("a")
            relative_url = product_link_tag.get("href")
            product_url = (
                f"https://jp.shein.com{relative_url}"
                if relative_url.startswith("/")
                else relative_url
            )

            # 画像URLを取得
            image_tag = product_tag.select_one(".crop-image-container")
            image_url = f"https:{image_tag.get("data-before-crop-src")}"

            # 価格情報を取得
            price_tag = product_tag.select_one(".product-item__camecase-wrap")
            price_text = price_tag.text.replace("¥", "").strip()
            
            # SKUを取得
            sku_tag = product_tag.select_one(".S-product-card__img-container.j-expose__product-item-img.S-product-card__img-container_mask")
            sku_text = sku_tag.get("data-sku")
            
            # 商品データを保存
            product = Product(
                sku=sku_text,
                url=product_url,
                price=price_text,
                image_url=image_url,
            )
            products.append(product)

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            raise Exception(f"{filename}の{line_no}行目でエラーが発生しました。詳細：{e}")

# データをJSON形式に変換
csv_json = [product.to_json() for product in products]

# データフレームに変換
df = pd.DataFrame(csv_json)

# CSVファイルに保存
csv_file = "プロジェクター_画像.csv"
df.to_csv(csv_file, index=False, encoding="utf-8-sig")

print(f"{csv_file} が作成されました。")
