import datetime

from databuilder.tables import Constraint, PatientFrame, Series, table

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

    def age_on(self, date):
        """
        Patient's age as an integer, in whole elapsed calendar years, as it would be on
        the supplied date.

        Note that this takes no account of whether the patient is alive at the given
        date. In particular, it may return negative values if the date is before the
        patient's date of birth.
        """
        return (date - self.date_of_birth).years
