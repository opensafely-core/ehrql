from ehrql import create_dataset
from ehrql.tables.ted import results, students


dataset = create_dataset()

# We're only interested in assessments from 2022 or 2023, from classes with a single
# teacher.
results = results.where(
    results.academic_year.is_in([2022, 2023]) & (results.teacher_id.is_not_null())
)

# Our dataset should only contain students from MAT1 that have an assessment.
dataset.define_population((students.mat_id == "MAT001") & results.exists())

# The dataset will contain one row per pupil, with columns about demographic
# information, SEND status, pupil premium status, and attendance.
dataset.gender = students.gender
dataset.eal = students.eal
dataset.send = students.send
dataset.pp = students.pp
dataset.attendance = students.attendance

# We will also extract information about the results into a separate table.
dataset.add_event_table(
    "results",
    date=results.date,
    teacher_id=results.teacher_id,
    subject=results.subject,
    score=results.score,
)
