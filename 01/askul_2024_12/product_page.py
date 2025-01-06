from typing import List
from bs4 import BeautifulSoup
from dataclasses import dataclass
import re

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


@dataclass(frozen=True)
class ProductProperty:
    label: str
    value: str


@dataclass
class Product:
    sales_unit: str
    properties: List[ProductProperty]
    price_tax_included: str
    price_tax_excluded: str
    product_number: str = ""

    def __init__(
        self,
        sales_unit: str,
        propertirs: List[ProductProperty],
        price_tax_included: float,
        price_tax_excluded: float,
        product_number: str = "",  # デフォルト値を持つ引数
    ):
        self.sales_unit = sales_unit
        self.properties = propertirs
        self.price_tax_included = price_tax_included
        self.price_tax_excluded = price_tax_excluded
        self.product_number = product_number
    
    def get_maker(self) -> str:
        for property in self.properties:
            if property.label == "メーカー名":
                return property.value
        return ""
    
    def get_description(self) -> str:
        for property in self.properties:
            if property.label == "商品の特徴":
                return property.value
        return ""

    def get_units_per_box(self) -> int:
        tag_text = self.soup.select_one("#tano-other-variation > p").get_text(strip=True)

        pattern = r'\d+'
        matches = re.findall(pattern, tag_text)
        if len(matches) == 1:
            return int(matches[0])
        elif len(matches) == 2:
            return int(matches[1])
        elif len(matches) == 4:
            return int(matches[2])
        else:
            return 1
    
    def get_boxes_per_case(self) -> int:
        tag_text = self.soup.select_one("#tano-other-variation > p").get_text(strip=True)

        pattern = r'\d+'
        matches = re.findall(pattern, tag_text)
        if len(matches) == 1:
            return 1
        elif len(matches) == 2:
            return 1
        elif len(matches) == 4:
            return int(matches[3])
        else:
            return 0


class ProductPage:
    soup: BeautifulSoup

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    def _price_tax_included(self) -> str:
        return self.soup.select_one("p.a-price.-large.js-bottomTrackingAddComparison_targetPrice > span.a-price_value").get_text(
            strip=True
        ).replace("￥", "")

    def _price_tax_excluded(self) -> str:
        tag_text = self.soup.select_one(
            "div.o-colBox.-margin8 > p.a-text"
        ).get_text(strip=True)
        return tag_text.replace("／￥", "").replace("（税抜き）", "")
    
    def _sales_unit(self) -> str:
        return self.soup.select_one("h2.a-heading_text").get_text(strip=True)

    def _properties(self) -> List[ProductProperty]:
        properties: List[ProductProperty] = []
        # trタグごとに解析
        for tr in self.soup.select('tr.o-table_tr'):
            # th と td をそれぞれ CSS セレクタで取得
            ths = tr.select('th.o-table_th')
            tds = tr.select('td.o-table_td')

            # th と td がペアになっている場合に抽出
            for th, td in zip(ths, tds):
                label = th.get_text(strip=True)
                value = td.get_text(strip=True)
                property = ProductProperty(label=label, value=value)
                properties.append(property)
        return properties

    def get_product(self) -> Product:
        properties = self._properties()
        price_tax_included = self._price_tax_included()
        price_tax_excluded = self._price_tax_excluded()
        sales_unit = self._sales_unit()
        product = Product(
            propertirs=properties,
            price_tax_included=price_tax_included,
            price_tax_excluded=price_tax_excluded,
            sales_unit=sales_unit
        )
        return product


if __name__ == "__main__":
    try:
        card_board_response = requests.get(
            "https://www.askul.co.jp/p/223801/",
            headers=HEADERS,
        )
        card_board_response.encoding = card_board_response.apparent_encoding
        card_board_response.raise_for_status()  # ステータスコードがエラーの場合例外を発生
    except requests.exceptions.RequestException as e:
        print("error occured on requests.get(ranking_url, headers=HEADERS): ", e)

    product_page = ProductPage(html=card_board_response.text)
    print(product_page.get_product())
