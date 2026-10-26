"""
Data Warehouse Loader: Consolidated Star Schema
Transforms clean staged data into:
- Fact_StudentAcademicPerformance
- Dim_Student
- Dim_Course
- Dim_Department
- Dim_Time
"""

import pandas as pd
import numpy as np


def build_star_schema(fact_source_df):
    """
    Constructs a formal Enterprise Star Schema with Surrogate Keys.
    """
    df = fact_source_df.copy()

    # 1. Dim_Department
    dept_unique = df['department'].unique()
    dim_department = pd.DataFrame({
        'department_key': range(1, len(dept_unique) + 1),
        'department_code': dept_unique,
        'department_name': [f"Department of {d}" for d in dept_unique]
    })
    dept_map = dict(zip(dim_department['department_code'], dim_department['department_key']))

    # 2. Dim_Course
    course_unique = df['course_id'].unique()
    dim_course = pd.DataFrame({
        'course_key': range(101, 101 + len(course_unique)),
        'course_code': course_unique,
        'credits': [4 if '301' in c or '401' in c else 3 for c in course_unique]
    })
    course_map = dict(zip(dim_course['course_code'], dim_course['course_key']))

    # 3. Dim_Student
    dim_student = df[['student_id', 'admission_type', 'batch_year']].drop_duplicates().reset_index(drop=True)
    dim_student['student_key'] = range(10001, 10001 + len(dim_student))
    student_map = dict(zip(dim_student['student_id'], dim_student['student_key']))

    # 4. Dim_Time (Academic Calendar Dimension)
    dim_time = pd.DataFrame([
        {'time_key': 202601, 'academic_year': 2025, 'semester': 'Odd (Fall)', 'quarter': 'Q1'},
        {'time_key': 202602, 'academic_year': 2026, 'semester': 'Even (Spring)', 'quarter': 'Q2'}
    ])

    # 5. Fact_StudentAcademicPerformance
    df['department_key'] = df['department'].map(dept_map)
    df['course_key'] = df['course_id'].map(course_map)
    df['student_key'] = df['student_id'].map(student_map)
    df['time_key'] = 202602  # Current semester key
    df['fact_id'] = range(1, len(df) + 1)

    grade_point_map = {'A_Excellent': 10.0, 'B_Good': 8.0, 'C_Average': 6.0, 'F_Fail': 0.0}
    df['gpa_point'] = df['grade'].map(grade_point_map).fillna(5.0)

    fact_table = df[[
        'fact_id', 'student_key', 'department_key', 'course_key', 'time_key',
        'attendance_band', 'quiz_submissions', 'lms_engagement',
        'grade', 'sgpa', 'gpa_point', 'backlog_count', 'fee_status'
    ]]

    return {
        'fact_student_performance': fact_table,
        'dim_student': dim_student,
        'dim_course': dim_course,
        'dim_department': dim_department,
        'dim_time': dim_time
    }
