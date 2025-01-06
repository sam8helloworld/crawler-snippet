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
    maker_name: str
    product_number: str
    sales_unit: str
    properties: List[ProductProperty]
    price_tax_included: str
    price_tax_excluded: str
    description: str

    def __init__(
        self,
        maker_name: str,
        product_number: str,
        sales_unit: str,
        propertirs: List[ProductProperty],
        price_tax_included: float,
        price_tax_excluded: float,
        description: str,
    ):
        self.maker_name = maker_name
        self.product_number = product_number
        self.sales_unit = sales_unit
        self.properties = propertirs
        self.price_tax_included = price_tax_included
        self.price_tax_excluded = price_tax_excluded
        self.description = description

    def get_units_per_box(self) -> int:
        # 正規表現パターン（数字と任意の単位）
        pattern1 = r"（(\d+)([^\d（）]+)：(\d+)([^\d（）]+)×(\d+)([^\d（）]+)）"  # 複雑な形式
        pattern2 = r"（(\d+)([^\d（）]+)）"  # 単純な形式
        pattern3 = r"(\d+)([^\d（）]+)"  # 最も簡単な形式

        # 最初のパターンでマッチ（複雑な形式）
        match = re.search(pattern1, self.sales_unit)
        if match:
            return match.group(3)

        # 次のパターンでマッチ（単純な形式）
        match = re.search(pattern2, self.sales_unit)
        if match:
            return match.group(1)

        # 最後のパターンでマッチ（最も簡単な形式）
        match = re.search(pattern3, self.sales_unit)
        if match:
            return match.group(1)

        # すべてのパターンでマッチしなければ 0 を返す
        return 0
    
    def get_boxes_per_case(self) -> int:
        # 正規表現パターン（数字と任意の単位）
        pattern1 = r"（(\d+)([^\d（）]+)：(\d+)([^\d（）]+)×(\d+)([^\d（）]+)）"  # 複雑な形式
        pattern2 = r"（(\d+)([^\d（）]+)）"  # 単純な形式
        pattern3 = r"(\d+)([^\d（）]+)"  # 最も簡単な形式

        # 最初のパターンでマッチ（複雑な形式）
        match = re.search(pattern1, self.sales_unit)
        if match:
            return match.group(5)

        # 次のパターンでマッチ（単純な形式）
        match = re.search(pattern2, self.sales_unit)
        if match:
            return 1

        # 最後のパターンでマッチ（最も簡単な形式）
        match = re.search(pattern3, self.sales_unit)
        if match:
            return 1

        # すべてのパターンでマッチしなければ 0 を返す
        return 0


class ProductPage:
    soup: BeautifulSoup

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")
    
    def _product_number(self) -> str:
        tag_text = self.soup.select_one("div.description_number.uk-margin-right").get_text(
            strip=True
        )
        return tag_text.split("：")[1]

    def _price_tax_included(self) -> str:
        return self.soup.select_one("span.uk-text-xlarge.text-price.uk-text-bold").get_text(
            strip=True
        )

    def _price_tax_excluded(self) -> str:
        tag_text = self.soup.select_one(
            "p.detail-desc_price--price.uk-text-right > span.uk-text-small:last-child"
        ).get_text(strip=True)
        return tag_text.split("円")[0]

    def _description(self) -> str:
        return self.soup.select_one(".description").get_text(strip=True)
    
    def _sales_unit(self) -> str:
        # 改行コードやタブがなぜか含まれている
        return self.soup.select_one("#tano-other-variation > p").get_text(strip=True).replace("\r", "").replace("\n", "").replace("\t", "").strip().split("：")[1]
    
    def _maker_name(self) -> str:
        tag_text = self.soup.select_one("div.description_maker").get_text(strip=True)
        return tag_text.split("：")[1]

    def _properties(self) -> List[ProductProperty]:
        data: List[ProductProperty] = []
        in_spec_section = False

        # 各<tr>をループしてthとtdを取得
        for row in self.soup.select('table.uk-table.uk-table-divider.uk-table-small.uk-table-middle > tbody > tr'):
            th = row.select('th')
            td = row.select('td')

            if th:
                label = th[0].get_text(strip=True)

                # '仕様' セクションの開始行
                if label == '仕様':
                    in_spec_section = True
                    th = th[1:]
                    if len(th) > 1 and len(td) > 1:
                        # 1行目の「仕様」行は無視して、以降はthとtdを交互に
                        for i in range(0, len(th)):
                            if i < len(td):  # thとtdが両方存在する場合
                                spec_label = th[i].get_text(strip=True)
                                spec_value = td[i].get_text(strip=True)
                                data.append(ProductProperty(label=spec_label, value=spec_value))
                    continue  # '仕様'ラベル行は無視

                if not in_spec_section:
                    # '概要'や'商品説明'などの通常の行
                    value = ' '.join([t.get_text(strip=True) for t in td])
                    data.append(ProductProperty(label=label, value=value))
            
            if in_spec_section:
                # '仕様' セクション内の行処理
                # N個目のthをlabel, N+1個目のtdをvalueにする
                if len(th) >= 1 and len(td) >= 1:
                    # 1行目の「仕様」行は無視して、以降はthとtdを交互に
                    for i in range(0, len(th)):
                        if i < len(td):  # thとtdが両方存在する場合
                            spec_label = th[i].get_text(strip=True)
                            spec_value = td[i].get_text(strip=True)
                            data.append(ProductProperty(label=spec_label, value=spec_value))

        return data

    def get_product(self) -> Product:
        maker_name = self._maker_name()
        product_number = self._product_number()
        properties = self._properties()
        price_tax_included = self._price_tax_included()
        price_tax_excluded = self._price_tax_excluded()
        description = self._description()
        sales_unit = self._sales_unit()
        product = Product(
            maker_name=maker_name,
            product_number=product_number,
            propertirs=properties,
            price_tax_included=price_tax_included,
            price_tax_excluded=price_tax_excluded,
            description=description,
            sales_unit=sales_unit
        )
        return product


if __name__ == "__main__":
    try:
        card_board_response = requests.get(
            "https://www.tanomail.com/product/1624656/",
            headers=HEADERS,
        )
        card_board_response.encoding = card_board_response.apparent_encoding
        card_board_response.raise_for_status()  # ステータスコードがエラーの場合例外を発生
    except requests.exceptions.RequestException as e:
        print("error occured on requests.get(ranking_url, headers=HEADERS): ", e)

    product_page = ProductPage(html=card_board_response.text)
    print(product_page.get_product())
