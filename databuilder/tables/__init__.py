from databuilder.query_language import EventFrame, PatientFrame, Series, table
from databuilder.query_model.table_schema import Constraint

# Temporarily provide constraints under their previous names
CategoricalConstraint = Constraint.Categorical
FirstOfMonthConstraint = Constraint.FirstOfMonth
NotNullConstraint = Constraint.NotNull
UniqueConstraint = Constraint.Unique

__all__ = [
    "CategoricalConstraint",
    "Constraint",
    "FirstOfMonthConstraint",
    "NotNullConstraint",
    "UniqueConstraint",
    "EventFrame",
    "PatientFrame",
    "Series",
    "table",
]
