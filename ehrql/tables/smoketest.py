"""
This tiny schema is used to write a [minimal dataset definition][smoketest_repo] that
can function as a basic end-to-end test (or "smoke test") of the OpenSAFELY platform
across all available backends.

[smoketest_repo]: https://github.com/opensafely/test-age-distribution
"""

import datetime

from ehrql.tables import Constraint, PatientFrame, Series, table


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
        constraints=[Constraint.FirstOfMonth(), Constraint.NotNull()],
    )
