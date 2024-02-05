"""
This example schema is for use in the ehrQL tutorial.
"""

import datetime

from ehrql.tables import Constraint, EventFrame, PatientFrame, Series, table


__all__ = [
    "clinical_events",
    "hospitalisations",
    "patient_address",
    "patients",
    "prescriptions",
]


@table
class clinical_events(EventFrame):
    """TODO."""

    code = Series(str)
    system = Series(str)
    date = Series(datetime.date)
    numeric_value = Series(float)


@table
class hospitalisations(EventFrame):
    """TODO."""

    date = Series(datetime.date)
    code = Series(str)
    system = Series(str)


@table
class patient_address(EventFrame):
    """TODO."""

    patientaddress_id = Series(int)
    date_start = Series(datetime.date)
    date_end = Series(datetime.date)
    index_of_multiple_deprivation_rounded = Series(int)
    has_postcode = Series(bool)


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


@table
class prescriptions(EventFrame):
    """TODO."""

    prescribed_dmd_code = Series(str)
    processing_date = Series(datetime.date)
