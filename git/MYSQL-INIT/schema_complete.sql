-- =============================================================
-- Cleveland_Clinic Hospital Database - Complete Schema
-- Combines SQLscript.sql + database.sql additions into one file.
-- Fix applied: added the missing lab_reports -> surgeries foreign
-- key (billing had it, lab_reports was missing it even though the
-- same validated Case ID relationship applies to both tables).
-- =============================================================

CREATE DATABASE IF NOT EXISTS Cleveland_Clinic;
USE Cleveland_Clinic;

CREATE TABLE `patients` (
  `patient_id` varchar(6) PRIMARY KEY,
  `date_of_registration` date,
  `date_of_first_consultation` date,
  `date_of_latest_consultation` date,
  `overall_satisfaction_rating` int,
  `admission` varchar(3),
  `surgery_underwent` varchar(3),
  `total_number_of_visits` int,
  `future_visit_flag` boolean
);

CREATE TABLE `doctors` (
  `doctor_id` varchar(8) PRIMARY KEY,
  `doctor_name` varchar(100),
  `specialization` varchar(50),
  `qualification` varchar(10),
  `surgery_experience` int,
  `practicing_branch` varchar(5) NOT NULL
);

CREATE TABLE `branches` (
  `branch_id` varchar(5) PRIMARY KEY,
  `location` varchar(50),
  `ot_available` varchar(3),
  `inhouse_anesthetician` varchar(3),
  `no_of_ots` int,
  `inhouse_pharmacy` varchar(3),
  `inhouse_nutritionist` varchar(3),
  `inpatient_rooms` int,
  `luxury_suite_rooms` varchar(3),
  `prayer_room` varchar(3),
  `kids_play_area` varchar(3)
);

CREATE TABLE `surgeries` (
  `case_id` bigint PRIMARY KEY,
  `serial_no` int,
  `patient_id` varchar(6),
  `doctor_id` varchar(8),
  `branch_id` varchar(5),
  `surgery_type` varchar(50),
  `surgery_date` date,
  `anesthesia_type` varchar(20),
  `surgery_outcome` varchar(20),
  `surgery_duration_hours` int,
  `recovery_period_days` int
);

CREATE TABLE `billing` (
  `claim_id` bigint PRIMARY KEY,
  `serial_no` int,
  `patient_id` varchar(6),
  `case_id` bigint NOT NULL,
  `branch_id` varchar(5),
  `total_bill` decimal(10,2),
  `insurance_provider` varchar(50),
  `amount_covered` decimal(10,2),
  `out_of_pocket_expenses` decimal(10,2),
  `claim_status` varchar(20)
);

CREATE TABLE `lab_reports` (
  `report_id` bigint PRIMARY KEY,
  `serial_no` int,
  `case_id` bigint NOT NULL,
  `patient_id` varchar(6),
  `branch_id` varchar(5),
  `test_name` varchar(50),
  `test_date` date,
  `result` varchar(20)
);

CREATE TABLE `appointments` (
  `serial_no` int PRIMARY KEY,
  `case_id` bigint,
  `patient_id` varchar(6),
  `branch_id` varchar(4),
  `date_of_consultation` date,
  `requested_doctor_id` varchar(7),
  `consulted_doctor_id` varchar(7),
  `reason_for_visit` varchar(50),
  `diagnosis` varchar(100),
  `prescribed_medication` varchar(100),
  `followup_required` varchar(3),
  `nutritionist_recommended` varchar(3)
);

CREATE TABLE `prescriptions` (
  `bill_id` bigint PRIMARY KEY,
  `serial_no` int,
  `patient_id` varchar(6),
  `doctor_id` varchar(8),
  `medication_name` varchar(50),
  `dosage` varchar(10),
  `quantity` int,
  `pharmacy_availability` varchar(3),
  `issued_date` date
);

CREATE TABLE `doctor_branch_visits` (
  `doctor_id` varchar(8) NOT NULL,
  `branch_id` varchar(5) NOT NULL,
  PRIMARY KEY (`doctor_id`, `branch_id`)
);

-- Foreign keys: only added where real, validated relationships exist
-- (see annotated validation notebook for the evidence behind each one)
ALTER TABLE `billing` ADD FOREIGN KEY (`case_id`) REFERENCES `surgeries` (`case_id`);
ALTER TABLE `lab_reports` ADD FOREIGN KEY (`case_id`) REFERENCES `surgeries` (`case_id`);  -- FIX: was missing
ALTER TABLE `doctor_branch_visits` ADD FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`);
ALTER TABLE `doctor_branch_visits` ADD FOREIGN KEY (`branch_id`) REFERENCES `branches` (`branch_id`);
ALTER TABLE `doctors` ADD FOREIGN KEY (`practicing_branch`) REFERENCES `branches` (`branch_id`);

-- =============================================================
-- Verification queries (run after the ETL load, not part of schema creation)
-- =============================================================
-- SHOW TABLES;
-- SELECT COUNT(*) FROM branches;              -- expect 100
-- SELECT COUNT(*) FROM doctors;                -- expect 200
-- SELECT COUNT(*) FROM doctor_branch_visits;   -- expect 384
-- SELECT COUNT(*) FROM patients;               -- expect 2300
-- SELECT COUNT(*) FROM patients WHERE future_visit_flag = 1;  -- expect 134
-- SELECT COUNT(*) FROM surgeries;              -- expect 1500
-- SELECT COUNT(*) FROM billing;                -- expect 5000
-- SELECT COUNT(*) FROM lab_reports;            -- expect 7500
-- SELECT COUNT(*) FROM appointments;           -- expect 12000
-- SELECT COUNT(*) FROM prescriptions;          -- expect 9000
