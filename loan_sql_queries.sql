-- ============================================================
--  LOAN DISBURSEMENT PROJECT — SQL QUERIES
--  Database: loan_disbursement.db (SQLite)
--  Table: loan_applications
--  Author: Pratik Rana | Data Analyst Portfolio Project
-- ============================================================

-- Q1: Overall KPI Summary
SELECT
  COUNT(*) AS total_applications,
  SUM(CASE WHEN Isdisbursed = 'Disbursed' THEN 1 ELSE 0 END) AS total_disbursed,
  SUM(CASE WHEN Isdisbursed = 'Not Disbursed' THEN 1 ELSE 0 END) AS total_not_disbursed,
  ROUND(100.0 * SUM(CASE WHEN Isdisbursed = 'Disbursed' THEN 1 ELSE 0 END) / COUNT(*), 2) AS disbursement_rate_pct,
  SUM(CASE WHEN Member_Pass = 'Pass' THEN 1 ELSE 0 END) AS cb_pass_count,
  SUM(CASE WHEN Member_Pass = 'Fail' THEN 1 ELSE 0 END) AS cb_fail_count
FROM loan_applications;

-- Q2: Branch-wise Disbursement Performance
SELECT
  BRANCHNAME,
  COUNT(*) AS total_applications,
  SUM(CASE WHEN Isdisbursed = 'Disbursed' THEN 1 ELSE 0 END) AS disbursed,
  SUM(CASE WHEN Isdisbursed = 'Not Disbursed' THEN 1 ELSE 0 END) AS not_disbursed,
  ROUND(100.0 * SUM(CASE WHEN Isdisbursed = 'Disbursed' THEN 1 ELSE 0 END) / COUNT(*), 2) AS disbursement_rate_pct,
  SUM(CASE WHEN Member_Pass = 'Pass' THEN 1 ELSE 0 END) AS cb_pass,
  SUM(CASE WHEN Member_Pass = 'Fail' THEN 1 ELSE 0 END) AS cb_fail
FROM loan_applications
GROUP BY BRANCHNAME
ORDER BY disbursement_rate_pct DESC;

-- Q3: Field Executive (FE) Performance Ranking
SELECT
  FeName AS field_executive,
  BRANCHNAME,
  COUNT(*) AS total_cases,
  SUM(CASE WHEN Isdisbursed = 'Disbursed' THEN 1 ELSE 0 END) AS disbursed,
  SUM(CASE WHEN Isdisbursed = 'Not Disbursed' THEN 1 ELSE 0 END) AS not_disbursed,
  ROUND(100.0 * SUM(CASE WHEN Isdisbursed = 'Disbursed' THEN 1 ELSE 0 END) / COUNT(*), 2) AS conversion_rate_pct,
  SUM(CASE WHEN Member_Pass = 'Pass' THEN 1 ELSE 0 END) AS cb_pass,
  SUM(CASE WHEN Member_Pass = 'Fail' THEN 1 ELSE 0 END) AS cb_fail
FROM loan_applications
GROUP BY FeName, BRANCHNAME
ORDER BY conversion_rate_pct DESC;

-- Q4: CGT Pipeline Funnel Breakdown
SELECT
  CGTRemark AS pipeline_stage,
  COUNT(*) AS total_applications,
  SUM(CASE WHEN Isdisbursed = 'Disbursed' THEN 1 ELSE 0 END) AS disbursed,
  SUM(CASE WHEN Isdisbursed = 'Not Disbursed' THEN 1 ELSE 0 END) AS pending
FROM loan_applications
GROUP BY CGTRemark
ORDER BY total_applications DESC;

-- Q5: Loan Cycle Analysis (New vs Repeat Borrowers)
SELECT
  CASE Cycle
    WHEN 0 THEN 'New Borrower (Cycle 0)'
    WHEN 1 THEN 'Repeat Borrower (Cycle 1)'
    ELSE 'Senior Borrower (Cycle 2+)'
  END AS borrower_type,
  COUNT(*) AS total,
  SUM(CASE WHEN Isdisbursed = 'Disbursed' THEN 1 ELSE 0 END) AS disbursed,
  ROUND(100.0 * SUM(CASE WHEN Isdisbursed = 'Disbursed' THEN 1 ELSE 0 END) / COUNT(*), 2) AS disbursement_rate_pct
FROM loan_applications
GROUP BY Cycle
ORDER BY Cycle;

-- Q6: Top 10 Credit Bureau Failure Reasons
SELECT
  CBRemark AS cb_remark,
  COUNT(*) AS total_failed_members,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_total_failures
FROM loan_applications
WHERE Member_Pass = 'Fail'
GROUP BY CBRemark
ORDER BY total_failed_members DESC
LIMIT 10;

-- Q7: Center-wise Top Performers
SELECT
  CENTERNAME,
  BRANCHNAME,
  COUNT(*) AS total_applications,
  SUM(CASE WHEN Isdisbursed = 'Disbursed' THEN 1 ELSE 0 END) AS disbursed,
  ROUND(100.0 * SUM(CASE WHEN Isdisbursed = 'Disbursed' THEN 1 ELSE 0 END) / COUNT(*), 2) AS rate_pct
FROM loan_applications
GROUP BY CENTERNAME, BRANCHNAME
ORDER BY disbursed DESC
LIMIT 15;

-- Q8: Members with Multiple Applications (Duplicate Check)
SELECT
  Client_id, Name, Mobile,
  COUNT(*) AS application_count,
  SUM(CASE WHEN Isdisbursed = 'Disbursed' THEN 1 ELSE 0 END) AS times_disbursed
FROM loan_applications
GROUP BY Client_id
HAVING application_count > 1
ORDER BY application_count DESC
LIMIT 20;

-- Q9: GRT Completion Rate
SELECT
  BRANCHNAME,
  SUM(CASE WHEN CGTRemark = 'Grt Complete' THEN 1 ELSE 0 END) AS grt_complete,
  SUM(CASE WHEN CGTRemark != 'Grt Complete' AND CGTRemark != 'Not IN CGT' THEN 1 ELSE 0 END) AS grt_in_progress,
  COUNT(*) AS total,
  ROUND(100.0 * SUM(CASE WHEN CGTRemark = 'Grt Complete' THEN 1 ELSE 0 END) / COUNT(*), 2) AS grt_completion_rate
FROM loan_applications
GROUP BY BRANCHNAME;

-- Q10: Applications Created by Month
SELECT
  strftime('%Y-%m', CB_Create_date) AS creation_month,
  COUNT(*) AS total_applications,
  SUM(CASE WHEN Isdisbursed = 'Disbursed' THEN 1 ELSE 0 END) AS disbursed
FROM loan_applications
WHERE CB_Create_date IS NOT NULL
GROUP BY creation_month
ORDER BY creation_month;
