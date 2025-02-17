import requests
from bs4 import BeautifulSoup
import dataclasses
from typing import List, Dict, Optional
import re
import pandas as pd
import argparse
import logging

# ログ設定
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)


@dataclasses.dataclass
class Job:
    title: str
    link: str
    company_name: str
    industry: str
    salary_range: str
    work_location: str
    application_qualifications: str
    planned_hires: str
    age_requirement_min: int
    age_requirement_max: int

    def to_json(self) -> Dict[str, Optional[str]]:
        return dataclasses.asdict(self)


def fetch_page_source(
    url: str, session: requests.Session, cookies: Optional[Dict[str, str]] = None
) -> List[Job]:
    """指定したURLにアクセスし、ページ内の求人情報を取得する。"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        response = session.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        content = soup.select("#content")
        if len(content) < 2:
            logging.error(f"[ERROR] 'content' セクションが見つかりません: {url}")
            return []

        jobs_content = content[1].select(".panel-body")
        return [extract_job_details(job_content) for job_content in jobs_content]
    except Exception as e:
        logging.error(f"[ERROR] ページの取得に失敗: {url} - {e}")
        return []


def extract_job_details(job_content) -> Job:
    """求人情報を解析し、Job オブジェクトを作成する。"""
    try:
        title = job_content.select_one(".job_detail_h3").text.strip()
        link = job_content.select_one(".job_detail_h3 > a").get("href", "")
    except Exception as e:
        logging.error(f"[ERROR] タイトルまたはリンクの取得に失敗: {e}")
        title, link = "", ""

    job_details = {}
    try:
        table = job_content.find("table", {"id": "job_detail_table"})
        if table:
            for row in table.find_all("tr"):
                header = row.find("th")
                value = row.find("td")
                if header and value:
                    key = header.get_text(strip=True)
                    val = value.get_text(" ", strip=True)
                    job_details[key] = val
    except Exception as e:
        logging.error(f"[ERROR] 詳細テーブルの解析に失敗: {e}")

    try:
        company_name = job_details.get("企業名", "")
        industry = job_details.get("業界", "")
        salary_range = job_details.get("年収", "")
        work_location = job_details.get("想定勤務地詳細", "")
        application_qualifications = job_details.get("応募資格", "")
        planned_hires = job_details.get("募集人数", "")
        age = job_details.get("年齢", "")
    except Exception as e:
        logging.error(f"[ERROR] 求人情報の取得に失敗: {e}")
        (
            company_name,
            industry,
            salary_range,
            work_location,
            application_qualifications,
            planned_hires,
            age,
        ) = ("", "", "", "", "", "", "")

    try:
        numbers = list(map(int, re.findall(r"[0-9０-９]+", age)))
        age_requirement_min = min(numbers) if numbers else 0
        age_requirement_max = max(numbers) if numbers else 0
    except Exception as e:
        logging.error(f"[ERROR] 年齢情報の解析に失敗: {e}")
        age_requirement_min, age_requirement_max = 0, 0

    return Job(
        title=title,
        link=link,
        company_name=company_name,
        industry=industry,
        salary_range=salary_range,
        work_location=work_location,
        application_qualifications=application_qualifications,
        planned_hires=planned_hires,
        age_requirement_min=age_requirement_min,
        age_requirement_max=age_requirement_max,
    )


def parse_cookies(cookie_str: str) -> Dict[str, str]:
    """クッキー文字列を辞書型に変換"""
    cookies = {}
    for pair in cookie_str.split(";"):
        key_value = pair.strip().split("=", 1)
        if len(key_value) == 2:
            cookies[key_value[0]] = key_value[1]
    return cookies


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description="Job Scraper Script")
    parser.add_argument(
        "-p", "--page_max", type=int, required=True, help="Page Max Num"
    )
    parser.add_argument(
        "-c", "--cookie", type=str, required=True, help="Session Cookie"
    )

    args = parser.parse_args()
    page_max = args.page_max
    session_cookie = args.cookie

    session = requests.Session()
    cookies = parse_cookies(session_cookie) if session_cookie else None

    job_list: List[Job] = []
    for page in range(1, page_max + 1):
        url = f"https://careerbank-jobsearch.com/page/{page}"
        job_list.extend(fetch_page_source(url, session, cookies))

    # pandasを使用してCSVに保存
    df = pd.DataFrame([job.to_json() for job in job_list])
    df.to_csv("job_list.csv", index=False, encoding="utf-8-sig")
    print("CSVファイル 'job_list.csv' に出力しました。")


if __name__ == "__main__":
    main()
