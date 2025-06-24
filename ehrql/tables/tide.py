"""
This schema defines the data available in the
OpenSAFELY-TIDE backend for education datasets.
"""

import datetime

from ehrql.tables import Constraint, EventFrame, PatientFrame, Series, table


__all__ = [
    "assessments",
    "pupils",
]


@table
class pupils(PatientFrame):
    """
    Pupils in the education dataset.
    """

    mat_id = Series(
        str,
        description="Multi-Academy Trust identifier for the pupil.",
        constraints=[Constraint.NotNull()],
    )
    gender = Series(
        str,
        description="Pupil's gender.",
        constraints=[
            Constraint.Categorical(["female", "male", "unknown"]),
            Constraint.NotNull(),
        ],
    )
    date_of_birth = Series(
        datetime.date,
        description="Pupil's date of birth.",
        constraints=[Constraint.FirstOfMonth(), Constraint.NotNull()],
    )
    eal = Series(
        bool,
        description="Whether the pupil has English as an Additional Language (EAL).",
    )
    send = Series(
        bool,
        description="Whether the pupil has Special Educational Needs and Disabilities (SEND).",
    )
    pupil_premium = Series(
        bool,
        description="Whether the pupil is eligible for pupil premium funding.",
    )
    attendance = Series(
        int,
        description="Pupil's attendance percentage.",
        constraints=[Constraint.ClosedRange(0, 100)],
    )


@table
class assessments(EventFrame):
    """
    Assessment records for pupils.
    """

    date = Series(
        datetime.date,
        description="The date the assessment was taken.",
    )
    teacher_id = Series(
        str,
        description="Identifier for the teacher who taught the pupil.",
        constraints=[Constraint.NotNull()],
    )
    subject = Series(
        str,
        description="The subject of the assessment.",
        constraints=[Constraint.NotNull()],
    )
    result = Series(
        float,
        description="The assessment result as a percentage (0-100), or null if no result recorded.",
        constraints=[Constraint.ClosedRange(0, 100)],
    )
