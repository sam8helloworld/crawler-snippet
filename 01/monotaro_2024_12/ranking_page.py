from typing import List
from bs4 import BeautifulSoup
from dataclasses import dataclass
import requests
from . import monotaro

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


@dataclass
class Ranking:
    rank: int
    name: str
    variation_page_url: str

    def __init__(self, rank: int, name: str, variation_page_url: str):
        self.rank = rank
        self.name = name
        self.variation_page_url = variation_page_url


class RankingPage:
    soup: BeautifulSoup

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    def get_rankings(self) -> List[Ranking]:
        rankings: List[Ranking] = []
        for i, item in enumerate(
            self.soup.select(".SearchResultProduct.u-MarginBottom--16.data-ee-imp")
        ):
            if i >= 10:  # 10回で終了
                break
            rank = i + 1

            name_tag = item.select_one("div.ProductMainArea__Information > a")
            name = name_tag.get_text(strip=True)
            variation_page_url = monotaro.SITE_BASE_URL + name_tag.get("href")
            ranking = Ranking(
                rank=rank, name=name, variation_page_url=variation_page_url
            )
            rankings.append(ranking)
        return rankings


if __name__ == "__main__":
    try:
        card_board_response = requests.get(
            "https://www.monotaro.com/k/store/%E6%AE%B5%E3%83%9C%E3%83%BC%E3%83%AB/",
            headers=HEADERS,
        )
        card_board_response.raise_for_status()  # ステータスコードがエラーの場合例外を発生
    except requests.exceptions.RequestException as e:
        print("error occured on requests.get(ranking_url, headers=HEADERS): ", e)

    ranking_page = RankingPage(html=card_board_response.text)
    print(ranking_page.get_rankings())
