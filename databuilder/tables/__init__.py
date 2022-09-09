import datetime

from databuilder.contracts.constraints import (
    CategoricalConstraint,
    FirstOfMonthConstraint,
    NotNullConstraint,
    UniqueConstraint,
)
from databuilder.query_language import EventFrame, PatientFrame, Series, table

__all__ = [
    "CategoricalConstraint",
    "FirstOfMonthConstraint",
    "NotNullConstraint",
    "UniqueConstraint",
    "EventFrame",
    "PatientFrame",
    "Series",
    "table",
]


# TODO: This is destined for removal see:
# https://github.com/opensafely-core/databuilder/issues/701
@table
class patients(PatientFrame):
    date_of_birth = Series(datetime.date)
    date_of_death = Series(datetime.date)
    sex = Series(str)
