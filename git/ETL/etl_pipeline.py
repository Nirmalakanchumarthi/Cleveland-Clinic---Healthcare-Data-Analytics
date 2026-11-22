import os
import time
import ast
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from urllib.parse import quote_plus

DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = quote_plus(os.environ.get("DB_PASSWORD", "changeme"))
DB_HOST = os.environ.get("DB_HOST", "mysql")
DB_NAME = os.environ.get("DB_NAME", "Cleveland_Clinic")
DATE_FMT = "%m/%d/%Y"
CSV_FOLDER = "/app/data"

engine = create_engine(f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

def wait_for_db(max_retries=30, delay_seconds=2):
    """MySQL takes a few seconds to initialize; retry until it accepts connections."""
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect():
                print("Database is ready.")
                return
        except OperationalError:
            print(f"Database not ready yet (attempt {attempt}/{max_retries}), retrying...")
            time.sleep(delay_seconds)
    raise RuntimeError("Database never became ready - aborting ETL run.")

    CSV_FOLDER = "/app/data"   # where the Dockerfile will copy your CSVs inside the container


def load_csv(name):
    """Read one of the source CSVs."""
    return pd.read_csv(f"{CSV_FOLDER}/{name}")


def to_sql(df, table_name):
    """Push a dataframe into a MySQL table and report how many rows went in."""
    df.to_sql(table_name, engine, if_exists="append", index=False, chunksize=1000)
    print(f"  -> loaded {len(df)} rows into '{table_name}'")


def load_branches():
    df = load_csv("branches.csv").rename(columns={
        "Branch ID": "branch_id", "Location": "location",
        "OT_Available": "ot_available", "Inhouse Anesthetician": "inhouse_anesthetician",
        "No. of OTs": "no_of_ots", "Inhouse Pharmacy": "inhouse_pharmacy",
        "Inhouse Nutritionist": "inhouse_nutritionist", "Inpatient Rooms": "inpatient_rooms",
        "Luxury Suite Rooms": "luxury_suite_rooms", "Prayer Room": "prayer_room",
        "Kids Play Area": "kids_play_area",
    })
    cols = ["branch_id", "location", "ot_available", "inhouse_anesthetician",
            "no_of_ots", "inhouse_pharmacy", "inhouse_nutritionist",
            "inpatient_rooms", "luxury_suite_rooms", "prayer_room", "kids_play_area"]
    to_sql(df[cols], "branches")


def load_doctors():
    raw = load_csv("doctors.csv")
    df = raw.rename(columns={
        "Doctor Name": "doctor_name", "Doctor ID": "doctor_id",
        "Specialization": "specialization", "Qualification": "qualification",
        "Surgery Experience": "surgery_experience", "Practicing Branch": "practicing_branch",
    })
    cols = ["doctor_id", "doctor_name", "specialization", "qualification",
            "surgery_experience", "practicing_branch"]
    to_sql(df[cols], "doctors")
    return raw   # returned because the junction table below needs the original columns


def load_doctor_branch_visits(raw_doctors_df):
    df = raw_doctors_df[["Doctor ID", "Other Branches Visited"]].copy()
    df["Other Branches Visited"] = df["Other Branches Visited"].apply(ast.literal_eval)
    exploded = df.explode("Other Branches Visited").rename(columns={
        "Doctor ID": "doctor_id", "Other Branches Visited": "branch_id",
    })
    to_sql(exploded, "doctor_branch_visits")

def load_patients():
    df = load_csv("patients.csv").rename(columns={
        "Patient ID": "patient_id", "Date of Registration": "date_of_registration",
        "Date of First Consultation": "date_of_first_consultation",
        "Date of Latest Consultation": "date_of_latest_consultation",
        "Overall Satisfaction Rating": "overall_satisfaction_rating",
        "Admission": "admission", "Surgery Underwent": "surgery_underwent",
        "Total Number of Visits": "total_number_of_visits",
    })
    for col in ["date_of_registration", "date_of_first_consultation", "date_of_latest_consultation"]:
        df[col] = pd.to_datetime(df[col], format=DATE_FMT)

    # Flag (don't delete) the 134 rows whose "latest consultation" is in the future
    df["future_visit_flag"] = df["date_of_latest_consultation"] > pd.Timestamp.today()

    cols = ["patient_id", "date_of_registration", "date_of_first_consultation",
            "date_of_latest_consultation", "overall_satisfaction_rating", "admission",
            "surgery_underwent", "total_number_of_visits", "future_visit_flag"]
    to_sql(df[cols], "patients")


def load_surgeries():
    df = load_csv("surgeries.csv").rename(columns={
        "Case ID": "case_id", "Serial No": "serial_no", "Patient ID": "patient_id",
        "Doctor ID": "doctor_id", "Branch ID": "branch_id", "Surgery Type": "surgery_type",
        "Surgery Date": "surgery_date", "Anesthesia Type": "anesthesia_type",
        "Surgery Outcome": "surgery_outcome", "Surgery Duration (hours)": "surgery_duration_hours",
        "Recovery Period (days)": "recovery_period_days",
    })
    df["surgery_date"] = pd.to_datetime(df["surgery_date"], format=DATE_FMT)
    cols = ["case_id", "serial_no", "patient_id", "doctor_id", "branch_id", "surgery_type",
            "surgery_date", "anesthesia_type", "surgery_outcome", "surgery_duration_hours",
            "recovery_period_days"]
    to_sql(df[cols], "surgeries")


def load_billing():
    df = load_csv("billing.csv").rename(columns={
        "Claim ID": "claim_id", "Serial No": "serial_no", "Patient ID": "patient_id",
        "Case ID": "case_id", "Branch ID": "branch_id", "Total Bill": "total_bill",
        "Insurance Provider": "insurance_provider", "Amount Covered": "amount_covered",
        "Out-of-Pocket Expenses": "out_of_pocket_expenses", "Claim Status": "claim_status",
    })
    cols = ["claim_id", "serial_no", "patient_id", "case_id", "branch_id", "total_bill",
            "insurance_provider", "amount_covered", "out_of_pocket_expenses", "claim_status"]
    to_sql(df[cols], "billing")

def load_lab_reports():
    df = load_csv("lab_reports.csv").rename(columns={
        "Report ID": "report_id", "Serial No": "serial_no", "Case ID": "case_id",
        "Patient ID": "patient_id", "Branch ID": "branch_id", "Test Name": "test_name",
        "Test Date": "test_date", "Result": "result",
    })
    df["test_date"] = pd.to_datetime(df["test_date"], format=DATE_FMT)
    cols = ["report_id", "serial_no", "case_id", "patient_id", "branch_id",
            "test_name", "test_date", "result"]
    to_sql(df[cols], "lab_reports")


def load_appointments():
    df = load_csv("appointments.csv").rename(columns={
        "Serial No": "serial_no", "Case ID": "case_id", "Patient ID": "patient_id",
        "Branch ID": "branch_id", "Date of Consultation": "date_of_consultation",
        "Requested Doctor ID": "requested_doctor_id", "Consulted Doctor ID": "consulted_doctor_id",
        "Reason for Visit": "reason_for_visit", "Diagnosis": "diagnosis",
        "Prescribed Medication": "prescribed_medication", "Followup Required": "followup_required",
        "Nutritionist Recommended": "nutritionist_recommended",
    })
    df["date_of_consultation"] = pd.to_datetime(df["date_of_consultation"], format=DATE_FMT)
    cols = ["serial_no", "case_id", "patient_id", "branch_id", "date_of_consultation",
            "requested_doctor_id", "consulted_doctor_id", "reason_for_visit", "diagnosis",
            "prescribed_medication", "followup_required", "nutritionist_recommended"]
    to_sql(df[cols], "appointments")


def load_prescriptions():
    df = load_csv("prescriptions.csv").rename(columns={
        "Bill ID": "bill_id", "Serial No": "serial_no", "Patient ID": "patient_id",
        "Doctor ID": "doctor_id", "Medication Name": "medication_name", "Dosage": "dosage",
        "Quantity": "quantity", "Pharmacy Availability": "pharmacy_availability",
        "Issued Date": "issued_date",
    })
    df["issued_date"] = pd.to_datetime(df["issued_date"], format=DATE_FMT)
    cols = ["bill_id", "serial_no", "patient_id", "doctor_id", "medication_name",
            "dosage", "quantity", "pharmacy_availability", "issued_date"]
    to_sql(df[cols], "prescriptions")

if __name__ == "__main__":
    print("Waiting for MySQL to be ready...")
    wait_for_db()

    print("Loading branches...")
    load_branches()

    print("Loading doctors...")
    raw_doctors = load_doctors()

    print("Loading doctor_branch_visits...")
    load_doctor_branch_visits(raw_doctors)

    print("Loading patients...")
    load_patients()

    print("Loading surgeries...")
    load_surgeries()

    print("Loading billing...")
    load_billing()

    print("Loading lab_reports...")
    load_lab_reports()

    print("Loading appointments...")
    load_appointments()

    print("Loading prescriptions...")
    load_prescriptions()

    print("\nAll tables loaded successfully. ETL run complete.")