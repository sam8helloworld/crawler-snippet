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
    properties: List[ProductProperty]
    price_tax_included: str
    price_tax_excluded: str
    description: str

    def __init__(
        self,
        propertirs: List[ProductProperty],
        price_tax_included: float,
        price_tax_excluded: float,
        description: str,
    ):
        self.properties = propertirs
        self.price_tax_included = price_tax_included
        self.price_tax_excluded = price_tax_excluded
        self.description = description
    
    def get_maker_name(self) -> str:
        for property in self.properties:
            if property.label == "メーカー名":
                return property.value
        return ""
    
    def get_product_number(self) -> str:
        for property in self.properties:
            if property.label == "メーカー品番":
                return property.value
        return ""

    def get_units_per_box(self) -> int:
        contents_text = ""
        for property in self.properties:
            if property.label == "単位":
                contents_text = property.value
        
        if contents_text == "":
            return 0

        pattern = r'\d+'
        matches = re.findall(pattern, contents_text)
        if len(matches) == 1:
            return int(matches[0])
        elif len(matches) == 2:
            return int(matches[1])
        elif len(matches) == 3:
            return int(matches[1])
        else:
            return 1
    
    def get_boxes_per_case(self) -> int:
        contents_text = ""
        for property in self.properties:
            if property.label == "単位":
                contents_text = property.value
        
        if contents_text == "":
            return 0

        pattern = r'\d+'
        matches = re.findall(pattern, contents_text)
        if len(matches) == 1:
            return 1
        elif len(matches) == 2:
            return 1
        elif len(matches) == 3:
            return int(matches[2])
        else:
            return 0


class ProductPage:
    soup: BeautifulSoup

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    def _price_tax_included(self) -> str:
        tag = self.soup.select_one('span.tbl_order_item_price_tax span[itemprop="price"]')
        tag_text = tag.get_text(strip=True).replace("(税込)", "").replace("￥", "")
        return tag_text

    def _price_tax_excluded(self) -> str:
        tag = self.soup.select_one('span.tbl_order_item_price_tax_excluded')
        tag_text = tag.get_text(strip=True).replace("(税抜)", "").replace("￥", "")
        return tag_text

    def _description(self) -> str:
        element = self.soup.select_one('span[itemprop="description"]')
        return element.get_text(strip=True) if element else ""

    def _properties(self) -> List[ProductProperty]:
        # label, value ペアを格納するリスト
        data: List[ProductProperty] = []

        # テーブル行をループして情報を抽出
        for row in self.soup.select('table.tbl_base01 > tbody > tr'):
            label = row.select_one('th h3.product_descrip_area_h3')
            if label:
                label_text = label.get_text(strip=True)

                # 商品仕様の特別処理
                if label_text == "商品仕様" or label_text == "メーカー情報":
                    for dl in row.select('td dl'):
                        dt = dl.select_one('dt').get_text(strip=True)
                        dd = dl.select_one('dd').get_text(strip=True)
                        data.append(ProductProperty(label=dt, value=dd))
                else:
                    # 通常の処理
                    value_text = row.select_one('td').get_text(strip=True)
                    data.append(ProductProperty(label=label_text, value=value_text))
        return data

    def get_product(self) -> Product:
        properties = self._properties()
        price_tax_included = self._price_tax_included()
        price_tax_excluded = self._price_tax_excluded()
        description = self._description()
        product = Product(
            propertirs=properties,
            price_tax_included=price_tax_included,
            price_tax_excluded=price_tax_excluded,
            description=description,
        )
        return product


if __name__ == "__main__":
    try:
        card_board_response = requests.get(
            "https://www.kaunet.com/kaunet/goods/50631698/",
            headers=HEADERS,
        )
        card_board_response.encoding = card_board_response.apparent_encoding
        card_board_response.raise_for_status()  # ステータスコードがエラーの場合例外を発生
    except requests.exceptions.RequestException as e:
        print("error occured on requests.get(ranking_url, headers=HEADERS): ", e)

    product_page = ProductPage(html=card_board_response.text)
    print(product_page.get_product())
