-- =============================================================
-- Hospital Project: Automated Report Queries (Task 2)
-- Run these against the Cleveland_Clinic database after the ETL
-- load (db_con_commented.ipynb) has completed successfully.
-- =============================================================

USE Cleveland_Clinic;

-- -------------------------------------------------------------
-- 1. Common Diagnoses Report
-- Groups all appointments by diagnosis, most frequent first.
-- Verified result: 10 diagnoses, Arthritis highest (1260 of 12,000).
-- -------------------------------------------------------------
SELECT diagnosis, COUNT(*) AS diagnosis_count
FROM appointments
GROUP BY diagnosis
ORDER BY diagnosis_count DESC;


-- -------------------------------------------------------------
-- 2. Revenue Report - overall summary
-- Verified result: Total Revenue $128,137,627.30; ~60% insurance
-- covered, ~40% out-of-pocket; 5000 total claims.
-- -------------------------------------------------------------
SELECT
    SUM(total_bill) AS total_revenue,
    SUM(amount_covered) AS total_covered_by_insurance,
    SUM(out_of_pocket_expenses) AS total_out_of_pocket,
    COUNT(*) AS total_claims
FROM billing;

-- -------------------------------------------------------------
-- 2b. Revenue Report - by branch
-- Verified result: 10 branches, revenue evenly spread
-- ($11.7M-$13.9M), CL09 highest, SU08 lowest.
-- -------------------------------------------------------------
SELECT
    branch_id,
    SUM(total_bill) AS branch_revenue,
    COUNT(*) AS claim_count
FROM billing
GROUP BY branch_id
ORDER BY branch_revenue DESC;


-- -------------------------------------------------------------
-- 3. Patient Visits Report - by month
-- Verified result: steady ~220-280 visits/month across the full
-- Jan 2020 - Dec 2023 range, no major seasonal trend.
-- -------------------------------------------------------------
SELECT
    DATE_FORMAT(date_of_consultation, '%Y-%m') AS visit_month,
    COUNT(*) AS total_visits
FROM appointments
GROUP BY visit_month
ORDER BY visit_month;
