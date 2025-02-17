import argparse
import logging
import psycopg2
from psycopg2 import sql, OperationalError, DatabaseError
import pandas as pd
import dataclasses
from typing import List
from record import Record

# ログの設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def insert_jobs_from_csv(csv_file: str, db_params: dict):
    try:
        logging.info(f"CSVファイル {csv_file} を読み込み中...")
        df = pd.read_csv(csv_file)
    except Exception as e:
        logging.error(f"CSVファイルの読み込みに失敗しました: {e}")
        return

    try:
        records = [Record(**row.to_dict()) for _, row in df.iterrows()]
        logging.info(f"{len(records)} 件のレコードを処理します。")
        insert_jobs_in_bulk(records, db_params)
    except Exception as e:
        logging.error(f"レコード処理中にエラーが発生しました: {e}")

def insert_jobs_in_bulk(records: List[Record], db_params: dict):
    try:
        logging.info("データベースに接続中...")
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
    except OperationalError as e:
        logging.error(f"データベースへの接続に失敗しました: {e}")
        return

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

    batch_size = 500
    try:
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            data = [dataclasses.asdict(record) for record in batch]
            cur.executemany(query, data)
            logging.info(f"{len(data)} 件のレコードを挿入しました。")

        conn.commit()
        logging.info("すべてのレコードを正常にコミットしました。")
    except DatabaseError as e:
        logging.error(f"データベース処理中にエラーが発生しました: {e}")
        conn.rollback()
        logging.info("トランザクションをロールバックしました。")
    finally:
        cur.close()
        conn.close()
        logging.info("データベース接続を閉じました。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Insert job records from CSV into PostgreSQL.")
    parser.add_argument("-f", "--file", required=True, help="Path to the CSV file")
    parser.add_argument("--dbname", required=True, help="Database name")
    parser.add_argument("--user", required=True, help="Database user")
    parser.add_argument("--password", required=True, help="Database password")
    parser.add_argument("--host", required=True, default="localhost", help="Database host (default: localhost)")
    parser.add_argument("--port", required=True, default="5432", help="Database port (default: 5432)")

    args = parser.parse_args()

    db_params = {
        "dbname": args.dbname,
        "user": args.user,
        "password": args.password,
        "host": args.host,
        "port": args.port,
    }

    insert_jobs_from_csv(args.file, db_params)
