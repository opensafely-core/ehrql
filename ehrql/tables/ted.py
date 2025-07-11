"""
This schema defines the data available in the
OpenSAFELY-TED backend for education datasets.
"""

import datetime

from ehrql.tables import Constraint, EventFrame, PatientFrame, Series, table


__all__ = [
    "results",
    "students",
]


@table
class students(PatientFrame):
    """
    Students in the education dataset.
    """

    mat_id = Series(
        str,
        description="Multi-Academy Trust identifier for the student.",
        constraints=[Constraint.NotNull()],
    )
    school_id = Series(
        str,
        description="School identifier.",
        constraints=[Constraint.NotNull()],
    )
    cohort = Series(
        str,
        description="The year group the student is in e.g. Y7 or 7.",
    )
    gender = Series(
        str,
        description="Student's gender (M/F).",
        constraints=[
            Constraint.Categorical(["M", "F"]),
        ],
    )
    ks2_maths_score = Series(
        float,
        description="KS2 maths assessment score - raw if possible but might be scaled.",
    )
    ks2_reading_score = Series(
        float,
        description="KS2 reading assessment score - raw if possible but might be scaled.",
    )
    cat_test_score = Series(
        float,
        description="CAT test score if available.",
    )
    reading_age = Series(
        float,
        description="Reading age if available.",
    )
    pp = Series(
        bool,
        description="Pupil Premium status (Y/N).",
    )
    eal = Series(
        bool,
        description="English as Additional Language (Y/N).",
    )
    send = Series(
        bool,
        description="Special Educational Need (Y/N).",
    )
    ehcp = Series(
        bool,
        description="Special Educational Need with EHCP (Education and Health Care Plan). This is the highest level of SEN classification (Y/N).",
    )
    lac = Series(
        bool,
        description="Looked After Child - a child in the care of the local authority (e.g. fostered) (Y/N).",
    )
    attendance = Series(
        int,
        description="% at school for the academic year.",
        constraints=[Constraint.ClosedRange(0, 100)],
    )


@table
class results(EventFrame):
    """
    Assessment result records for students.
    """

    class_id = Series(
        str,
        description="Class identifier.",
        constraints=[Constraint.NotNull()],
    )
    academic_year = Series(
        int,
        description="Academic year e.g. 22/23, 2022/2023. Sometimes only the final year is used e.g. 2024 = 23/24.",
    )
    year_group = Series(
        str,
        description="Year group.",
    )
    assessment_type = Series(
        str,
        description="Assessment type e.g. GCSE, class test, end of term, end of year exam.",
    )
    subject = Series(
        str,
        description="The subject of the assessment.",
        constraints=[Constraint.NotNull()],
    )
    num_questions = Series(
        int,
        description="Number of questions in test.",
    )
    date = Series(
        datetime.date,
        description="Date the assessment was taken.",
    )
    score = Series(
        float,
        description="Raw score.",
    )
    predicted_grade = Series(
        str,
        description="The grade that the student is expected to achieve at either the end of the year or for their GCSE in that subject.",
    )
    teacher_id = Series(
        str,
        description="Identifier for the teacher who taught the student. Present only when the result is for a class that was taught by a single teacher.",
    )
