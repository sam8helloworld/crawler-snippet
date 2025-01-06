from dataclasses import dataclass
from typing import List
from collections import Counter


@dataclass
class Product:
    ranking: int
    name: str
    product_number: str
    maker_name: str
    price_tax_included: float
    price_tax_excluded: float
    url: str
    site_name: str
    units_per_box: float  # 個数/小箱
    boxes_per_case: float  # 個数/ケース
    total: float
    description: str
    properties: List[tuple[str, str]]

    def __init__(
        self,
        ranking: int,
        name: str,
        product_number: str,
        maker_name: str,
        price_tax_included: float,
        price_tax_excluded: float,
        url: str,
        site_name: str,
        units_per_box: float,
        boxes_per_case: float,
        description: str,
        properties: List[tuple[str, str]],
    ):
        self.ranking = ranking
        self.name = name
        self.product_number = product_number
        self.maker_name = maker_name
        self.price_tax_included = price_tax_included
        self.price_tax_excluded = price_tax_excluded
        self.url = url
        self.site_name = site_name
        self.units_per_box = units_per_box
        self.boxes_per_case = boxes_per_case
        self.total = units_per_box * boxes_per_case  # 自動的に計算して設定
        self.description = description
        self.properties = properties

    def sort_tuples_by_frequency(self, tuples_list: List[tuple[str, str]]):
        # 1番目の要素をカウント
        counter = Counter(t[0] for t in tuples_list)
        # 頻度の多い順にソートしたキーのリストを返す
        return [item for item, _ in counter.most_common()]

    def search_tuple_by_first_element(
        self, tuples_list: List[tuple[str, str]], search_value: str
    ):
        return next((t[1] for t in tuples_list if t[0] == search_value), "")

    def to_json(self) -> dict:
        propertyKeys = self.sort_tuples_by_frequency(self.properties)
        
        data = {
            "ランキング": self.ranking,
            "商品名": self.name,
            "品番": self.product_number,
            "メーカー": self.maker_name,
            "価格(税込)": self.price_tax_included,
            "価格(税抜)": self.price_tax_excluded,
            "商品URL": self.url,
            "サイト名": self.site_name,
            "個数/小箱": self.units_per_box,
            "小箱/ケース": self.boxes_per_case,
            "合計個数": self.total,
            "説明文": self.description
        }
        # プロパティを追加
        for _, key in enumerate(propertyKeys, start=1):
            data[key] = self.search_tuple_by_first_element(self.properties, key)
        return data
