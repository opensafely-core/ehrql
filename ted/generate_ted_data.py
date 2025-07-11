#!/usr/bin/env python3

import argparse
import csv
import os
import random
from datetime import date, timedelta


def generate_students_csv(output_dir, num_students=100):
    """Generate CSV file for students table matching TED schema."""

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Sample data pools
    mat_ids = [f"MAT{i:03d}" for i in range(1, 4)]  # 3 different MATs
    school_ids = [f"SCH{i:03d}" for i in range(1, 51)]  # 50 different schools
    cohorts = [
        "Y7",
        "Y8",
        "Y9",
        "Y10",
        "Y11",
        "Y12",
        "Y13",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
    ]
    genders = ["M", "F"]

    with open(os.path.join(output_dir, "students.csv"), "w", newline="") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(
            [
                "patient_id",
                "mat_id",
                "school_id",
                "cohort",
                "gender",
                "ks2_maths_score",
                "ks2_reading_score",
                "cat_test_score",
                "reading_age",
                "pp",
                "eal",
                "send",
                "ehcp",
                "lac",
                "attendance",
            ]
        )

        # Generate student records
        for i in range(1, num_students + 1):
            patient_id = i
            mat_id = random.choice(mat_ids)
            school_id = random.choice(school_ids)
            cohort = random.choice(cohorts)
            gender = random.choice(genders)

            # Academic scores (some can be null)
            ks2_maths_score = (
                round(random.uniform(80, 120), 1) if random.random() > 0.1 else ""
            )
            ks2_reading_score = (
                round(random.uniform(80, 120), 1) if random.random() > 0.1 else ""
            )
            cat_test_score = (
                round(random.uniform(70, 140), 1) if random.random() > 0.3 else ""
            )
            reading_age = (
                round(random.uniform(8.0, 16.0), 1) if random.random() > 0.2 else ""
            )

            # Boolean fields (represented as T/F)
            pp = "T" if random.random() < 0.25 else "F"  # 25% pupil premium
            eal = "T" if random.random() < 0.15 else "F"  # 15% EAL
            send = "T" if random.random() < 0.12 else "F"  # 12% SEN
            ehcp = "T" if random.random() < 0.03 else "F"  # 3% EHCP
            lac = "T" if random.random() < 0.02 else "F"  # 2% LAC

            # Attendance percentage
            attendance = random.randint(70, 100)

            writer.writerow(
                [
                    patient_id,
                    mat_id,
                    school_id,
                    cohort,
                    gender,
                    ks2_maths_score,
                    ks2_reading_score,
                    cat_test_score,
                    reading_age,
                    pp,
                    eal,
                    send,
                    ehcp,
                    lac,
                    attendance,
                ]
            )

    print(f"Generated students.csv with {num_students} records")


def generate_results_csv(output_dir, num_students=100):
    """Generate CSV file for results table matching TED schema."""

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Sample data pools
    class_ids = [f"CLASS{i:03d}" for i in range(1, 101)]  # 100 different classes
    academic_years = [2022, 2023, 2024]
    year_groups = [
        "Y7",
        "Y8",
        "Y9",
        "Y10",
        "Y11",
        "Y12",
        "Y13",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
    ]
    assessment_types = [
        "GCSE",
        "A-Level",
        "Class test",
        "End of term",
        "End of year exam",
        "Mock exam",
        "Coursework",
    ]
    subjects = [
        "Mathematics",
        "English",
        "Science",
        "History",
        "Geography",
        "Art",
        "Music",
        "PE",
        "Computing",
        "French",
        "Spanish",
        "German",
    ]
    predicted_grades = [
        "9",
        "8",
        "7",
        "6",
        "5",
        "4",
        "3",
        "2",
        "1",
        "A*",
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "U",
    ]
    teacher_ids = [f"TEACHER{i:03d}" for i in range(1, 51)]  # 50 different teachers

    with open(os.path.join(output_dir, "results.csv"), "w", newline="") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(
            [
                "patient_id",
                "class_id",
                "academic_year",
                "year_group",
                "assessment_type",
                "subject",
                "num_questions",
                "date",
                "score",
                "predicted_grade",
                "teacher_id",
            ]
        )

        # Generate multiple results per student
        for i in range(1, num_students + 1):
            patient_id = i

            # Generate 3-8 results per student
            num_results = random.randint(3, 8)

            for _ in range(num_results):
                class_id = random.choice(class_ids)
                academic_year = random.choice(academic_years)
                year_group = random.choice(year_groups)
                assessment_type = random.choice(assessment_types)
                subject = random.choice(subjects)

                # Number of questions (some can be null)
                num_questions = random.randint(10, 100) if random.random() > 0.2 else ""

                # Date in the academic year
                start_date = date(academic_year, 9, 1)
                end_date = date(academic_year + 1, 7, 31)
                random_date = start_date + timedelta(
                    days=random.randint(0, (end_date - start_date).days)
                )

                # Score (some can be null)
                if num_questions:
                    score = (
                        round(random.uniform(0, float(num_questions)), 1)
                        if random.random() > 0.1
                        else ""
                    )
                else:
                    score = (
                        round(random.uniform(0, 100), 1)
                        if random.random() > 0.1
                        else ""
                    )

                predicted_grade = (
                    random.choice(predicted_grades) if random.random() > 0.1 else ""
                )
                teacher_id = random.choice(teacher_ids) if random.random() > 0.2 else ""

                writer.writerow(
                    [
                        patient_id,
                        class_id,
                        academic_year,
                        year_group,
                        assessment_type,
                        subject,
                        num_questions,
                        random_date.strftime("%Y-%m-%d"),
                        score,
                        predicted_grade,
                        teacher_id,
                    ]
                )

    print(f"Generated results.csv with assessment records for {num_students} students")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate TED schema CSV files for ehrQL testing"
    )
    parser.add_argument(
        "output_dir",
        help="Directory to write CSV files to",
    )
    parser.add_argument(
        "--num-students",
        type=int,
        default=100,
        help="Number of students to generate (default: 100)",
    )

    args = parser.parse_args()

    generate_students_csv(args.output_dir, args.num_students)
    generate_results_csv(args.output_dir, args.num_students)
    print(f"CSV files generated successfully in {args.output_dir}/ directory")
