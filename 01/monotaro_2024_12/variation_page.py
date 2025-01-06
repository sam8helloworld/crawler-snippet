from typing import List
from bs4 import BeautifulSoup
from dataclasses import dataclass
import requests
from . import monotaro

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

@dataclass
class Variation():
    product_page_url: str
    
    def __init__(self, product_page_url: str):
        self.product_page_url = product_page_url

class VariationPage:
    soup: BeautifulSoup

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    def get_variations(self) -> List[Variation]:
        variation_tags = self.soup.select(
            "table.Table.Table--MaxWidth.u-FontSize--Default > tbody > tr.Table__Row.Table__Row--Hover.data-ee-sku"
        )
        variations: List[Variation] = []
        for v, variation_tag in enumerate(variation_tags):
            print(f"{v+1} つ目のバリエーションを確認中...")
            # なぜかスクレイピング時にバリエーションのリンクが取得できないことがある
            a_tag = variation_tag.select_one("a.TextLink")
            if a_tag is None:
                continue
            else:
                product_page_url = monotaro.SITE_BASE_URL + variation_tag.select_one("a.TextLink").get(
                    "href"
                )
                variation = Variation(product_page_url=product_page_url)
                variations.append(variation)
        return variations



if __name__ == "__main__":
    try:
        card_board_response = requests.get(
            "https://www.monotaro.com/g/04051814/",
            headers=HEADERS,
        )
        card_board_response.raise_for_status()  # ステータスコードがエラーの場合例外を発生
    except requests.exceptions.RequestException as e:
        print("error occured on requests.get(ranking_url, headers=HEADERS): ", e)

    variation_page = VariationPage(html=card_board_response.text)
    print(variation_page.get_variations())