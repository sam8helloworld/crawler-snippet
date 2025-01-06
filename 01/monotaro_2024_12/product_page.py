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
    properties: List[ProductProperty]
    price_tax_included: str
    price_tax_excluded: str
    description: str

    def __init__(
        self,
        maker_name: str,
        propertirs: List[ProductProperty],
        price_tax_included: float,
        price_tax_excluded: float,
        description: str,
    ):
        self.maker_name = maker_name
        self.properties = propertirs
        self.price_tax_included = price_tax_included
        self.price_tax_excluded = price_tax_excluded
        self.description = description
    
    def get_product_number(self) -> str:
        for property in self.properties:
            if property.label == "品番":
                return property.value
        return ""
    
    def get_description(self) -> str:
        if self.description != "":
            return self.description
        else:
            for property in self.properties:
                if property.label == "用途":
                    return property.value
        return ""

    def get_units_per_box(self) -> int:
        contents_text = ""
        for property in self.properties:
            if property.label == "内容量":
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
            if property.label == "内容量":
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
        # 取り扱い終了の場合金額が存在しない
        tags = self.soup.select("span.ReferencePrice.u-FontSize--Default.u-InlineBlock")
        for tag in tags:
            if "販売価格(税込)" in tag.get_text():
                tag_text = tag.get_text(strip=True).replace("販売価格(税込)", "")
                return tag_text.replace("￥", "")
        return ""

    def _price_tax_excluded(self) -> str:
        # 取り扱い終了の場合金額が存在しない
        tag = self.soup.select_one("span.Price.Price--Lg")
        if tag is None:
            return ""
        else:
            return (
                tag
                .get_text(strip=True)
                .replace("￥", "")
            )

    def _description(self) -> str:
        element = self.soup.select_one(".DescriptionText.u-FontSize--Md")
        return element.get_text(strip=True) if element else ""
    
    def _maker_name(self) -> str:
        tag = self.soup.select_one("a.TextLink.BrandText")

        if tag:
            tag_text = tag.get_text(strip=True)
        else:
            img_tag = self.soup.select_one("a.BrandCategoryLink img")
            if img_tag and img_tag.has_attr('title'):
                tag_text = img_tag['title']
            else:
                tag_text = ""  # imgタグやtitle属性がない場合は空文字を返す

        return tag_text

    def _properties(self) -> List[ProductProperty]:
        # chipの情報を全て取得する
        chip_tags = self.soup.select(
            "div.u-Table > div.AttributeLabel.u-InlineMarginClear > span.AttributeLabel__Wrap"
        )
        properties: List[ProductProperty] = []
        if len(chip_tags) == 0:
            # chipのテキスト情報を全て取得する
            text_tags = self.soup.select(
                "div.u-Table > .AttributeLabelItemArea > .AttributeLabelItem"
            )
            for text_tag in text_tags:
                label = (
                    text_tag.select_one(".AttributeLabelItem__Heading").get_text(
                        strip=True
                    )
                    if text_tag.select_one(".AttributeLabelItem__Heading")
                    else None
                )
                value = (
                    text_tag.select_one(".u-FontWeight--Bold").get_text(strip=True)
                    if text_tag.select_one(".u-FontWeight--Bold")
                    else None
                )
                property = ProductProperty(label=label, value=value)
                properties.append(property)
        else:
            for chip_tag in chip_tags:
                label = (
                    chip_tag.select_one(".AttributeLabel__Heading").get_text(strip=True)
                    if chip_tag.select_one(".AttributeLabel__Heading")
                    else None
                )
                value = (
                    chip_tag.get_text(strip=True).replace(label, "", 1).strip()
                    if label
                    else None
                )

                property = ProductProperty(label=label, value=value)
                properties.append(property)

        second_chip_tags = self.soup.select(
            "div.Section__Inner > div.AttributeLabel.u-InlineMarginClear > span.AttributeLabel__Wrap"
        )
        for chip_tag in second_chip_tags:
            label = (
                chip_tag.select_one(".AttributeLabel__Heading").get_text(strip=True)
                if chip_tag.select_one(".AttributeLabel__Heading")
                else None
            )
            value = (
                chip_tag.get_text(strip=True).replace(label, "", 1).strip()
                if label
                else None
            )

            property = ProductProperty(label=label, value=value)
            properties.append(property)
        # 重複削除
        return list(set(properties))

    def get_product(self) -> Product:
        maker_name = self._maker_name()
        properties = self._properties()
        price_tax_included = self._price_tax_included()
        price_tax_excluded = self._price_tax_excluded()
        description = self._description()
        product = Product(
            maker_name=maker_name,
            propertirs=properties,
            price_tax_included=price_tax_included,
            price_tax_excluded=price_tax_excluded,
            description=description,
        )
        return product


if __name__ == "__main__":
    try:
        card_board_response = requests.get(
            "https://www.monotaro.com/p/0924/3586/",
            headers=HEADERS,
        )
        card_board_response.encoding = card_board_response.apparent_encoding
        card_board_response.raise_for_status()  # ステータスコードがエラーの場合例外を発生
    except requests.exceptions.RequestException as e:
        print("error occured on requests.get(ranking_url, headers=HEADERS): ", e)

    product_page = ProductPage(html=card_board_response.text)
    print(product_page.get_product())
