CREATE TABLE jobs (
  id serial PRIMARY KEY,
  detail_fetched boolean NOT NULL DEFAULT false,
  link text,
  title text,
  company_name text,
  company_url text,
  industry text,
  category text,
  salary_range text,
  work_location text,
  application_qualifications text,
  job_description text,
  screening_speed text,
  planned_hires text,
  pass_rate text,
  age_requirement_min integer,
  age_requirement_max integer,
  gender_requirement text,
  nationality_requirement text,
  requirement_tags text,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  position_details text,
  position_level text,
  establishment_year text,
  company_phase text,
  employees_count text,
  listing_status text,
  company_address text,
  holidays_count text,
  regular_holidays text,
  benefits text,
  smoking_measures text,
  casual_interview boolean,
  company_briefing text,
  aptitude_test boolean,
  selection_flow text,
  fee_text text,
  success_point text,
  payment_terms text,
  refund_policy text,
  theoretical_salary_policy text,
  body text,
  reproduce_prohibit boolean DEFAULT false,
  handling_agency text,
  posted_date text,
  pr_points text,
  organization_structure text,
  document_rejection_reasons text,
  high_likelihood_hire text,
  interview_rejection_reasons text,
  agent_info_document_points text,
  agent_info_interview_first text,
  agent_info_interview_final text,
  body_text text,
  job_status character varying(50) NOT NULL DEFAULT 'progress'::character varying,
  rubric text,
  body_format text
);