"""
This is the minimal schema required to run the OpenSAFELY system smoke test.
All backends should implement this schema.
"""

import datetime

from .. import FirstOfMonthConstraint, NotNullConstraint, PatientFrame, Series, table

__all__ = [
    "patients",
]


@table
class patients(PatientFrame):

    date_of_birth = Series(
        datetime.date,
        description=(
            "Patient's year and month of birth, provided in format YYYY-MM-01. "
            "The day will always be the first of the month."
        ),
        constraints=[FirstOfMonthConstraint(), NotNullConstraint()],
    )
