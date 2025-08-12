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
        description="A pseudonymised identifier for the student’s MAT",
        constraints=[Constraint.NotNull()],
    )
    school_id = Series(
        str,
        description="A pseudonymised identifier for the student’s school",
        constraints=[Constraint.NotNull()],
    )
    year_group = Series(
        int,
        description="Current year group",
    )
    gender = Series(
        str,
        description="Gender",
        constraints=[
            Constraint.Categorical(["M", "F"]),
        ],
    )
    ks2_maths_score = Series(
        int,
        description="KS2 maths assessment score",
    )
    ks2_reading_score = Series(
        int,
        description="KS2 reading assessment score",
    )
    reading_age = Series(
        float,
        description="Reading age",
    )
    pp = Series(
        bool,
        description="Pupil Premium status",
    )
    eal = Series(
        bool,
        description="English as Additional Language",
    )
    send = Series(
        bool,
        description="Indicates whether student is on SEND register",
    )
    ehcp = Series(
        bool,
        description="Indicates whether student has EHCP",
    )
    lac = Series(
        bool,
        description="Indicates whether student is Looked After Child",
    )
    attendance = Series(
        int,
        description="Attendance percentage for current year",
        constraints=[Constraint.ClosedRange(0, 100)],
    )


@table
class results(EventFrame):
    """
    Assessment result records for students.
    """

    class_id = Series(
        str,
        description="A pseudonymised identifier for the class",
        constraints=[Constraint.NotNull()],
    )
    teacher_id = Series(
        str,
        description="A pseudonymised identifier for the class's teacher, or null if the class had multiple teachers",
    )
    academic_year = Series(
        int,
        description="Academic year of the assessment",
    )
    year_group = Series(
        int,
        description="Year group when assessment taken",
    )
    subject = Series(
        str,
        description="The subject of the assessment",
        constraints=[Constraint.NotNull()],
    )
    date = Series(
        datetime.date,
        description="Date the assessment was taken",
    )
    score = Series(
        float,
        description="Score as a percentage",
    )
