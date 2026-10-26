"""
Heterogeneous Operational Data Generator
Simulates University Subsystems:
1. SIS (Student Information System) - Relational format
2. LMS (Learning Management System) - Semi-structured JSON/NoSQL format
3. Examination Portal - Relational/Tabular format
4. Finance & Accounts - CSV Export format
"""

import numpy as np
import pandas as pd


def generate_heterogeneous_sources(num_students=1200, random_seed=42):
    """
    Generates synthetic datasets modeling disparate enterprise university sources.
    """
    np.random.seed(random_seed)
    student_ids = [f"STU_{i:04d}" for i in range(1001, 1001 + num_students)]

    # 1. SIS (Student Information System)
    departments = ['CSE', 'ECE', 'MECH', 'CIVIL', 'IT']
    admission_types = ['Merit_Counseling', 'Management_Quota', 'Sports_Scholarship', 'Lateral_Entry']
    
    sis_records = []
    for sid in student_ids:
        sis_records.append({
            'student_id': sid,
            'department': np.random.choice(departments, p=[0.35, 0.25, 0.15, 0.10, 0.15]),
            'admission_type': np.random.choice(admission_types, p=[0.60, 0.25, 0.05, 0.10]),
            'batch_year': np.random.choice([2023, 2024, 2025, 2026], p=[0.25, 0.25, 0.25, 0.25]),
            'hostel_resident': np.random.choice(['Hosteller', 'DayScholar'], p=[0.45, 0.55])
        })
    df_sis = pd.DataFrame(sis_records)

    # 2. LMS (Learning Management System: Moodle/Canvas style JSON)
    lms_records = []
    for sid in student_ids:
        # Correlation: Hosteller or Merit often have higher LMS activity
        attendance_val = np.random.beta(a=7, b=2) * 100  # Skewed towards high attendance
        if attendance_val >= 85:
            attn_band = "High (>85%)"
        elif attendance_val >= 75:
            attn_band = "Moderate (75-85%)"
        else:
            attn_band = "Low (<75%)"

        lms_records.append({
            'student_id': sid,
            'course_id': np.random.choice(['CS301_Algorithms', 'EC202_Signals', 'ME105_Thermodynamics', 'IT401_Cloud'], p=[0.4, 0.25, 0.15, 0.2]),
            'attendance_rate': round(attendance_val, 1),
            'attendance_band': attn_band,
            'quiz_submissions': np.random.choice(['All_Submitted', 'Partial_Submitted', 'None_Submitted'], p=[0.7, 0.2, 0.1]),
            'lms_engagement': np.random.choice(['Highly_Engaged', 'Moderate_Engaged', 'Inactive'], p=[0.55, 0.35, 0.10])
        })
    df_lms = pd.DataFrame(lms_records)

    # 3. Examination & Grading Portal
    exam_records = []
    for _, lms_row in df_lms.iterrows():
        sid = lms_row['student_id']
        attn = lms_row['attendance_band']
        quiz = lms_row['quiz_submissions']

        # Ground truth correlation: High attendance + All Quizzes -> High Grade
        if attn == "High (>85%)" and quiz == "All_Submitted":
            grade = np.random.choice(['A_Excellent', 'B_Good', 'C_Average'], p=[0.65, 0.30, 0.05])
            sgpa = round(np.random.uniform(8.2, 9.8), 2)
            backlogs = 0
        elif attn == "Low (<75%)":
            grade = np.random.choice(['C_Average', 'F_Fail'], p=[0.40, 0.60])
            sgpa = round(np.random.uniform(4.0, 6.5), 2)
            backlogs = np.random.choice([1, 2, 3], p=[0.5, 0.3, 0.2])
        else:
            grade = np.random.choice(['A_Excellent', 'B_Good', 'C_Average', 'F_Fail'], p=[0.20, 0.50, 0.25, 0.05])
            sgpa = round(np.random.uniform(6.5, 8.2), 2)
            backlogs = np.random.choice([0, 1], p=[0.85, 0.15])

        exam_records.append({
            'student_id': sid,
            'grade': grade,
            'sgpa': sgpa,
            'backlog_count': backlogs,
            'hall_ticket_issued': 'Yes' if backlogs < 3 else 'Withheld'
        })
    df_exam = pd.DataFrame(exam_records)

    # 4. Finance & Accounts (CSV Style)
    finance_records = []
    for sid in student_ids:
        fee_stat = np.random.choice(['Paid_In_Full', 'Scholarship_Exempt', 'Pending_Dues'], p=[0.75, 0.15, 0.10])
        finance_records.append({
            'student_id': sid,
            'fee_status': fee_stat,
            'scholarship_grant': 'Govt_PostMatric' if fee_stat == 'Scholarship_Exempt' else 'None',
            'library_due_status': np.random.choice(['Clear', 'Fined'], p=[0.90, 0.10])
        })
    df_finance = pd.DataFrame(finance_records)

    return df_sis, df_lms, df_exam, df_finance


def extract_etl_transactions(df_sis, df_lms, df_exam, df_finance):
    """
    Extracts unified attribute tokens across heterogeneous tables into
    transactional itemsets for Association Rule Mining.
    """
    merged = df_sis.merge(df_lms, on='student_id') \
                   .merge(df_exam, on='student_id') \
                   .merge(df_finance, on='student_id')

    transactions = []
    for _, row in merged.iterrows():
        txn = [
            f"Dept={row['department']}",
            f"AdminType={row['admission_type']}",
            f"Course={row['course_id']}",
            f"AttnBand={row['attendance_band']}",
            f"Quiz={row['quiz_submissions']}",
            f"LMS={row['lms_engagement']}",
            f"Grade={row['grade']}",
            f"Fee={row['fee_status']}",
            f"Hostel={row['hostel_resident']}"
        ]
        transactions.append(txn)

    return transactions, merged
