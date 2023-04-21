import datetime

from ehrql.tables import Constraint, PatientFrame, Series, table


__all__ = ["patients"]


@table
class patients(PatientFrame):
    date_of_birth = Series(
        datetime.date,
        description="Patient's date of birth, rounded to first of month",
        constraints=[Constraint.FirstOfMonth(), Constraint.NotNull()],
    )
    sex = Series(
        str,
        description="Patient's sex",
        implementation_notes_to_add_to_description=(
            'Specify how this has been determined, e.g. "sex at birth", or "current sex".'
        ),
        constraints=[
            Constraint.NotNull(),
            Constraint.Categorical(["female", "male", "intersex", "unknown"]),
        ],
    )
    date_of_death = Series(
        datetime.date,
        description="Patient's date of death",
    )
