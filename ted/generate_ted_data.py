import csv
import random
import sys
from pathlib import Path


random.seed(12345)

num_schools = 10
num_teachers_per_school = 25
num_classes_per_teacher = 10
num_students_per_school = 500
num_classes_per_student = 10

assert num_classes_per_student < num_teachers_per_school * num_classes_per_teacher

prob_send = 0.10
prob_pp = 0.15
prob_eal = 0.20


def main(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    students = []

    mat_id = "MAT01"
    academic_year = 2023

    for school_ix in range(num_schools):
        school_id = f"SCH{school_ix:02}"
        school_effect = random.gauss(sigma=10)
        teachers_by_id = {}
        classes = []

        for teacher_ix in range(num_teachers_per_school):
            teacher_id = f"TCH{school_ix:02}{teacher_ix:02}"
            teachers_by_id[teacher_id] = {"effect": random.gauss(sigma=5)}
            for class_ix in range(num_classes_per_teacher):
                class_id = f"CLS{school_ix:02}{teacher_ix:02}{class_ix:02}"
                classes.append(
                    {
                        "id": class_id,
                        "teacher_id": teacher_id,
                        "effect": random.gauss(sigma=20),
                    }
                )

        for _ in range(num_students_per_school):
            student_id = len(students)

            gender = random.choice(["M", "F"])
            eal = random.random() < prob_eal
            send = random.random() < prob_send
            pp = random.random() < prob_pp
            attendance = int(random.betavariate(19, 1) * 100)
            if send:
                baseline = int(random.betavariate(5, 10) * 100)
            else:
                baseline = int(random.betavariate(10, 5) * 100)

            pp_effect = -5 if pp else 0

            students.append(
                {
                    "patient_id": student_id,
                    "mat_id": mat_id,
                    "school_id": school_id,
                    "gender": gender,
                    "eal": "T" if eal else "F",
                    "send": "T" if send else "F",
                    "pp": "T" if pp else "F",
                    "attendance": attendance,
                    "ks2_reading_score": baseline,
                }
            )

            for cls in random.sample(classes, num_classes_per_student):
                class_id = cls["id"]
                teacher_id = cls["teacher_id"]

                teacher_effect = teachers_by_id[teacher_id]["effect"]
                class_effect = cls["effect"]

                score = int(
                    baseline + school_effect + teacher_effect + class_effect + pp_effect
                )
                score = max(0, min(score, 100))

                results.append(
                    {
                        "patient_id": student_id,
                        "school_id": school_id,
                        "teacher_id": teacher_id,
                        "class_id": class_id,
                        "academic_year": academic_year,
                        "score": score,
                    }
                )

    results_file = output_dir / "results.csv"
    students_file = output_dir / "students.csv"

    with open(students_file, "w") as f:
        writer = csv.DictWriter(f, students[0].keys())
        writer.writeheader()
        writer.writerows(students)

    with open(results_file, "w") as f:
        writer = csv.DictWriter(f, results[0].keys())
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
