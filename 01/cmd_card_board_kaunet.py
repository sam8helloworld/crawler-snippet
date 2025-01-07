from typing import List
import requests
import pandas as pd
from product import Product

from kaunet_2024_12.kaunet import CARDBOARD as KCARDBOARD
from kaunet_2024_12.ranking_page import RankingPage as KRankingPage
from kaunet_2024_12.variation_page import VariationPage as KVaroationPage
from kaunet_2024_12.product_page import  ProductPage as KProductPage

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# ダンボール
card_board_products: List[Product] = []
try:
    kaunet_card_board_response = requests.get(
        KCARDBOARD["url"],
        headers=HEADERS,
    )
    kaunet_card_board_response.encoding = kaunet_card_board_response.apparent_encoding
    kaunet_card_board_response.raise_for_status()  # ステータスコードがエラーの場合例外を発生
except requests.exceptions.RequestException as e:
    print("error occured on requests.get(ranking_url, headers=HEADERS): ", e)

ranking_page = KRankingPage(html=kaunet_card_board_response.text)
rankings = ranking_page.get_rankings()

for i, ranking in enumerate(rankings):
    try:
        variation_page_response = requests.get(
            ranking.variation_page_url,
            headers=HEADERS,
        )
        variation_page_response.encoding = variation_page_response.apparent_encoding
        variation_page_response.raise_for_status()  # ステータスコードがエラーの場合例外を発生
    except requests.exceptions.RequestException as e:
        print("error occured on requests.get(ranking_url, headers=HEADERS): ", e)
    variarion_page = KVaroationPage(html=variation_page_response.text)
    variations = variarion_page.get_variations()
    for v, variation in enumerate(variations):
        try:
            product_page_response = requests.get(
                variation.product_page_url,
                headers=HEADERS,
            )
            product_page_response.encoding = product_page_response.apparent_encoding
            product_page_response.raise_for_status()  # ステータスコードがエラーの場合例外を発生
        except requests.exceptions.RequestException as e:
            print("error occured on requests.get(ranking_url, headers=HEADERS): ", e)
        product_page = KProductPage(html=product_page_response.text)
        product = product_page.get_product()

        # Product構築
        product_for_csv = Product(
            ranking=ranking.rank,
            name=ranking.name,
            product_number=product.get_product_number(),
            maker_name=product.get_maker_name(),
            price_tax_included=product.price_tax_included,
            price_tax_excluded=product.price_tax_excluded,
            url=variation.product_page_url,
            site_name="カウネット",
            units_per_box=product.get_units_per_box(),
            boxes_per_case=product.get_boxes_per_case(),
            description=product.description,
            properties=[(prop.label, prop.value) for prop in product.properties]
        )
        card_board_products.append(product_for_csv)



csv_json = [product.to_json() for product in card_board_products]


# データフレームに変換
df = pd.DataFrame(csv_json)

# CSVファイルに保存
csv_file = "card_board_products(カウネット).csv"
df.to_csv(csv_file, index=False, encoding="utf-8-sig")

print(f"{csv_file} が作成されました。")