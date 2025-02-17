import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import dataclasses
from typing import List, Dict
from collections import defaultdict
import argparse

from datetime import datetime

@dataclasses.dataclass
class Record:
    link: str
    title: str
    detail_fetched: bool
    company_name: str
    company_url: str
    industry: str
    category: str
    salary_range: str
    work_location: str
    application_qualifications: str
    job_description: str
    screening_speed: str
    planned_hires: str
    pass_rate: str
    age_requirement_min: int
    age_requirement_max: int
    gender_requirement: str
    nationality_requirement: str
    requirement_tags: str
    created_at: datetime
    updated_at: datetime
    position_details: str
    position_level: str
    establishment_year: str
    company_phase: str
    employees_count: str
    listing_status: str
    company_address: str
    holidays_count: str
    regular_holidays: str
    benefits: str
    smoking_measures: str
    casual_interview: bool
    company_briefing: str
    aptitude_test: bool
    selection_flow: str
    fee_text: str
    success_point: str
    payment_terms: str
    refund_policy: str
    theoretical_salary_policy: str
    body: str
    reproduce_prohibit: bool
    handling_agency: str
    posted_date: str
    pr_points: str
    organization_structure: str
    document_rejection_reasons: str
    high_likelihood_hire: str
    interview_rejection_reasons: str
    agent_info_document_points: str
    agent_info_interview_first: str
    agent_info_interview_final: str
    body_text: str
    job_status: str
    rubric: str
    body_format: str
    
    def to_json(self) -> dict:
        return dataclasses.asdict(self)
    

@dataclasses.dataclass
class JobDetail:
    company_url: str
    job_description: str
    gender_requirement: str
    nationality_requirement: str
    establishment_year: str
    employees_count: str
    company_address: str
    holidays_count: str
    benefits: str
    smoking_measures: str
    casual_interview: bool
    company_briefing: bool
    aptitude_test: bool
    selection_flow: str
    fee_text: str
    refund_policy: str
    theoretical_salary_policy: str
    body: str
    body_text: str
    reproduce_prohibit: bool
    posted_date: str
    pr_points: str
    interview_rejection_reasons: str

    def to_json(self) -> dict:
        return dataclasses.asdict(self)

def fetch_page_source(url: str, cookies: Dict[str, str] = None) -> JobDetail:
    """ 指定したURLの求人情報を取得し、解析してJobDetailオブジェクトを返す """
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    company_details = extract_table_data(soup, 2, ["ホームページ", "本社所在地", "設立年月日", "従業員数", "会社の特徴"])
    job_details = extract_table_data(soup, 1, ["仕事内容", "福利厚生", "受動喫煙対策", "休日休暇", "選考内容"])
    agent_details = extract_table_data(soup, 0, ["性別", "外国籍の必要資格・経験", "成功報酬条件", "理論年収の定義", "返金規定（紹介手数料）", "面接お見送り理由", "その他備考"])
    
    holidays_count = extract_holidays(job_details.get("休日休暇", ""))
    casual_interview = "カジュアル面談の有無 : 状況に応じてある" in job_details.get("選考内容", "")
    company_briefing = "会社説明会の有無: あり" in job_details.get("選考内容", "")
    aptitude_test = "適性テストの有無: あり" in job_details.get("選考内容", "")
    reproduce_prohibit = "転載禁止" in agent_details.get("その他備考", "")
    posted_date = soup.select_one(".posted-date").text if soup.select_one(".posted-date") else ""
    
    body_text = soup.select_one(".post-content")
    body_text.select_one(".panel.panel-default").decompose()
    
    return JobDetail(
        company_url=company_details.get("ホームページ", ""),
        job_description=job_details.get("仕事内容", ""),
        gender_requirement=agent_details.get("性別", ""),
        nationality_requirement=agent_details.get("外国籍の必要資格・経験", ""),
        establishment_year=company_details.get("設立年月日", ""),
        employees_count=company_details.get("従業員数", ""),
        company_address=company_details.get("本社所在地", ""),
        holidays_count=holidays_count,
        benefits=job_details.get("福利厚生", ""),
        smoking_measures=job_details.get("受動喫煙対策", ""),
        casual_interview=casual_interview,
        company_briefing=company_briefing,
        aptitude_test=aptitude_test,
        selection_flow=job_details.get("選考内容", ""),
        fee_text=agent_details.get("成功報酬条件", ""),
        refund_policy=agent_details.get("返金規定（紹介手数料）", ""),
        theoretical_salary_policy=agent_details.get("理論年収の定義", ""),
        body=response.text,
        body_text=body_text.get_text(),
        reproduce_prohibit=reproduce_prohibit,
        posted_date=posted_date,
        pr_points=company_details.get("会社の特徴", ""),
        interview_rejection_reasons=agent_details.get("面接お見送り理由", "")
    )

def extract_table_data(soup: BeautifulSoup, index: int, keys: List[str]) -> Dict[str, str]:
    """ 指定したインデックスのテーブルからデータを抽出 """
    details = defaultdict(str)
    tables = soup.find_all("table", class_="table table-hover")
    if len(tables) > index:
        for row in tables[index].find_all("tr"):
            header = row.find("th")
            value = row.find("td")
            if header and value:
                key = header.get_text(strip=True)
                if key in keys:
                    details[key] = value.get_text(" ", strip=True).replace("\n", " ")
    return details

def extract_holidays(text: str) -> str:
    """ 正規表現を使って年間休日を抽出 """
    match = re.search(r"年間休⽇.*?(\d+)", text)
    return match.group(1) if match else "年間休日不明"

def parse_cookies(cookie_str: str) -> Dict[str, str]:
    cookies = {}
    for pair in cookie_str.split(";"):
        key_value = pair.strip().split("=", 1)
        if len(key_value) == 2:
            cookies[key_value[0]] = key_value[1]
    return cookies

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Job Scraper Script")
    parser.add_argument("-f", "--file", type=str, required=True, help="CSV file containing job links")
    parser.add_argument("-c", "--cookie", type=str, help="Session Cookie")
    parser.add_argument("-m", "--max", type=int, help="Max Process Count", default=10)
    args = parser.parse_args()

    session = requests.Session()
    cookies = parse_cookies(args.cookie) if args.cookie else None

    df = pd.read_csv(args.file)
    
    job_details: List[Record] = []
    for index, row in df.iterrows():
        if index == args.max:
            break
        print(f'{index+1}個目処理中....')
        job_detail = fetch_page_source(row["link"], cookies)
        if job_detail:
            job_details.append(
                Record(
                    link=row["link"],
                    title=row["title"],
                    detail_fetched=True,
                    company_name=row["company_name"],
                    company_url=job_detail.company_url,
                    industry=row["industry"],
                    category=None,
                    salary_range=row["salary_range"],
                    work_location=row["work_location"],
                    application_qualifications=row["application_qualifications"],
                    job_description=job_detail.job_description,
                    screening_speed=None,
                    planned_hires=row["planned_hires"],
                    pass_rate=None,
                    age_requirement_min=row["age_requirement_min"],
                    age_requirement_max=row["age_requirement_max"],
                    gender_requirement=job_detail.gender_requirement,
                    nationality_requirement=job_detail.nationality_requirement,
                    requirement_tags=None,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    position_details=None,
                    position_level=None,
                    establishment_year=job_detail.establishment_year,
                    company_phase=None,
                    employees_count=job_detail.employees_count,
                    listing_status=None,
                    company_address=job_detail.company_address,
                    holidays_count=job_detail.holidays_count,
                    regular_holidays=None,
                    benefits=job_detail.benefits,
                    smoking_measures=job_detail.smoking_measures,
                    casual_interview=job_detail.casual_interview,
                    company_briefing="Yes" if job_detail.company_briefing else "No",
                    aptitude_test=job_detail.aptitude_test,
                    selection_flow=job_detail.selection_flow,
                    fee_text=job_detail.fee_text,
                    success_point=None,
                    payment_terms=None,
                    refund_policy=job_detail.refund_policy,
                    theoretical_salary_policy=job_detail.theoretical_salary_policy,
                    body=job_detail.body,
                    reproduce_prohibit=job_detail.reproduce_prohibit,
                    handling_agency=None,
                    posted_date=job_detail.posted_date,
                    pr_points=job_detail.pr_points,
                    organization_structure=None,
                    document_rejection_reasons=None,
                    high_likelihood_hire=None,
                    interview_rejection_reasons=job_detail.interview_rejection_reasons,
                    agent_info_document_points=None,
                    agent_info_interview_first=None,
                    agent_info_interview_final=None,
                    body_text=job_detail.body_text,
                    job_status=None,
                    rubric=None,
                    body_format=None,
                )
            )
    
    output_file = "output_jobs.csv"
    pd.DataFrame([job.to_json() for job in job_details]).to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"CSVファイル '{output_file}' に出力しました。")
