import datetime

from databuilder.tables import (
    CategoricalConstraint,
    FirstOfMonthConstraint,
    NotNullConstraint,
    PatientFrame,
    Series,
    table,
)

__all__ = ["patients"]


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
    sex = Series(
        str,
        description="Patient's sex as defined by the options: male, female, intersex, unknown.",
        implementation_notes_to_add_to_description=(
            'Specify how this has been determined, e.g. "sex at birth", or "current sex".'
        ),
        constraints=[
            NotNullConstraint(),
            CategoricalConstraint("female", "male", "intersex", "unknown"),
        ],
    )
    date_of_death = Series(
        datetime.date,
        description=(
            "Patient's year and month of death, provided in format YYYY-MM-01. "
            "The day will always be the first of the month."
        ),
        constraints=[FirstOfMonthConstraint()],
    )
