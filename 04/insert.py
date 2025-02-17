import psycopg2
from psycopg2 import sql
import pandas as pd
import dataclasses
from datetime import datetime
import sys
from typing import List


@dataclasses.dataclass
class Record:
    detail_fetched: str
    link: str
    title: str
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
    age_requirement_min: str
    age_requirement_max: str
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
    casual_interview: str
    company_briefing: str
    aptitude_test: str
    selection_flow: str
    fee_text: str
    success_point: str
    payment_terms: str
    refund_policy: str
    theoretical_salary_policy: str
    body: str
    reproduce_prohibit: str
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


def insert_jobs_from_csv(csv_file: str):
    # CSVファイルをpandasで読み込み
    df = pd.read_csv(csv_file)

    # レコードをList[Record]に変換
    records = []
    for _, row in df.iterrows():
        record = Record(
            detail_fetched=row["detail_fetched"],
            link=row["link"],
            title=row["title"],
            company_name=row["company_name"],
            company_url=row["company_url"],
            industry=row["industry"],
            category=row["category"],
            salary_range=row["salary_range"],
            work_location=row["work_location"],
            application_qualifications=row["application_qualifications"],
            job_description=row["job_description"],
            screening_speed=row["screening_speed"],
            planned_hires=row["planned_hires"],
            pass_rate=row["pass_rate"],
            age_requirement_min=row["age_requirement_min"],
            age_requirement_max=row["age_requirement_max"],
            gender_requirement=row["gender_requirement"],
            nationality_requirement=row["nationality_requirement"],
            requirement_tags=row["requirement_tags"],
            created_at=pd.to_datetime(row["created_at"]),
            updated_at=pd.to_datetime(row["updated_at"]),
            position_details=row["position_details"],
            position_level=row["position_level"],
            establishment_year=row["establishment_year"],
            company_phase=row["company_phase"],
            employees_count=row["employees_count"],
            listing_status=row["listing_status"],
            company_address=row["company_address"],
            holidays_count=row["holidays_count"],
            regular_holidays=row["regular_holidays"],
            benefits=row["benefits"],
            smoking_measures=row["smoking_measures"],
            casual_interview=row["casual_interview"],
            company_briefing=row["company_briefing"],
            aptitude_test=row["aptitude_test"],
            selection_flow=row["selection_flow"],
            fee_text=row["fee_text"],
            success_point=row["success_point"],
            payment_terms=row["payment_terms"],
            refund_policy=row["refund_policy"],
            theoretical_salary_policy=row["theoretical_salary_policy"],
            body=row["body"],
            reproduce_prohibit=row["reproduce_prohibit"],
            handling_agency=row["handling_agency"],
            posted_date=row["posted_date"],
            pr_points=row["pr_points"],
            organization_structure=row["organization_structure"],
            document_rejection_reasons=row["document_rejection_reasons"],
            high_likelihood_hire=row["high_likelihood_hire"],
            interview_rejection_reasons=row["interview_rejection_reasons"],
            agent_info_document_points=row["agent_info_document_points"],
            agent_info_interview_first=row["agent_info_interview_first"],
            agent_info_interview_final=row["agent_info_interview_final"],
            body_text=row["body_text"],
            job_status=row["job_status"],
            rubric=row["rubric"],
            body_format=row["body_format"],
        )
        records.append(record)

    # レコードを500行ごとにバルクインサート
    insert_jobs_in_bulk(records)


def insert_jobs_in_bulk(records: List[Record]):
    conn = psycopg2.connect(
        dbname="mydatabase",
        user="myuser",  # ユーザー名
        password="mypassword",  # パスワード
        host="localhost",  # ホスト
        port="5432",  # ポート
    )

    cur = conn.cursor()

    query = sql.SQL(
        """
        INSERT INTO jobs (
            detail_fetched, link, title, company_name, company_url, industry, category, salary_range, 
            work_location, application_qualifications, job_description, screening_speed, 
            planned_hires, pass_rate, age_requirement_min, age_requirement_max, gender_requirement, 
            nationality_requirement, requirement_tags, created_at, updated_at, position_details, 
            position_level, establishment_year, company_phase, employees_count, listing_status, 
            company_address, holidays_count, regular_holidays, benefits, smoking_measures, 
            casual_interview, company_briefing, aptitude_test, selection_flow, fee_text, success_point, 
            payment_terms, refund_policy, theoretical_salary_policy, body, reproduce_prohibit, 
            handling_agency, posted_date, pr_points, organization_structure, document_rejection_reasons, 
            high_likelihood_hire, interview_rejection_reasons, agent_info_document_points, 
            agent_info_interview_first, agent_info_interview_final, body_text, job_status, rubric, body_format
        ) 
        VALUES (
            %(detail_fetched)s, %(link)s, %(title)s, %(company_name)s, %(company_url)s, %(industry)s, %(category)s, %(salary_range)s, 
            %(work_location)s, %(application_qualifications)s, %(job_description)s, %(screening_speed)s, 
            %(planned_hires)s, %(pass_rate)s, %(age_requirement_min)s, %(age_requirement_max)s, %(gender_requirement)s, 
            %(nationality_requirement)s, %(requirement_tags)s, %(created_at)s, %(updated_at)s, %(position_details)s, 
            %(position_level)s, %(establishment_year)s, %(company_phase)s, %(employees_count)s, %(listing_status)s, 
            %(company_address)s, %(holidays_count)s, %(regular_holidays)s, %(benefits)s, %(smoking_measures)s, 
            %(casual_interview)s, %(company_briefing)s, %(aptitude_test)s, %(selection_flow)s, %(fee_text)s, %(success_point)s, 
            %(payment_terms)s, %(refund_policy)s, %(theoretical_salary_policy)s, %(body)s, %(reproduce_prohibit)s, 
            %(handling_agency)s, %(posted_date)s, %(pr_points)s, %(organization_structure)s, %(document_rejection_reasons)s, 
            %(high_likelihood_hire)s, %(interview_rejection_reasons)s, %(agent_info_document_points)s, 
            %(agent_info_interview_first)s, %(agent_info_interview_final)s, %(body_text)s, %(job_status)s, %(rubric)s, %(body_format)s
        );
    """
    )

    # 500行ごとにバルクインサート
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        data = [dataclasses.asdict(record) for record in batch]
        cur.executemany(query, data)

    conn.commit()
    cur.close()
    conn.close()


# コマンドライン引数を取得
if len(sys.argv) < 2:
    print("Usage: python script.py <csv_file>")
else:
    csv_file = sys.argv[1]
    insert_jobs_from_csv(csv_file)
