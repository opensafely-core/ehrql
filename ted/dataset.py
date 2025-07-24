from ehrql import create_dataset
from ehrql.tables.ted import results, students


dataset = create_dataset()

# We're only interested in assessments from 2022 or 2023, from classes with a single
# teacher.
results = results.where(
    results.academic_year.is_in([2022, 2023]) & (results.teacher_id.is_not_null())
)

# Our dataset should only contain students from MAT1 that have an assessment.
dataset.define_population((students.mat_id == "MAT01") & results.exists())

# The dataset will contain one row per pupil, with columns about demographic
# information, SEND status, pupil premium status, attendance, and baseline attainment.
dataset.school_id = students.school_id
dataset.Gender = students.gender
dataset.EAL = students.eal
dataset.SEN = students.send
dataset.PP = students.pp
dataset.attendance = students.attendance
dataset.baseline = students.ks2_reading_score

# We will also extract information about the results into a separate table.
dataset.add_event_table(
    "results",
    date=results.date,
    teacher_id=results.teacher_id,
    class_id=results.class_id,
    subject=results.subject,
    score=results.score,
)
