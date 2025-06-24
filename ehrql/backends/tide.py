import sqlalchemy

import ehrql.tables.tide
from ehrql.backends.base import MappedTable, SQLBackend
from ehrql.query_engines.mssql import MSSQLQueryEngine


class TIDEBackend(SQLBackend):
    """
    The ehrQL TIDE backend provides access to education data from the TIDE
    dataset, including pupil demographics and assessment results.
    """

    display_name = "TIDE"
    query_engine_class = MSSQLQueryEngine
    patient_join_column = "pupil_id"
    implements = [
        ehrql.tables.tide,
    ]

    def column_kwargs_for_type(self, type_):
        """Override to set collation for string types to match SQL Server defaults"""
        if type_ is str:
            return {
                "type_": sqlalchemy.String(collation="SQL_Latin1_General_CP1_CS_AS")
            }
        return super().column_kwargs_for_type(type_)

    pupils = MappedTable(
        source="pupils",
        columns={
            "patient_id": "pupil_id",
            "mat_id": "mat_id",
            "gender": "gender",
            "date_of_birth": "date_of_birth",
            "eal": "eal",
            "send": "send",
            "pupil_premium": "pupil_premium",
            "attendance": "attendance",
        },
    )

    assessments = MappedTable(
        source="assessments",
        columns={
            "patient_id": "pupil_id",
            "date": "date",
            "teacher_id": "teacher_id",
            "subject": "subject",
            "result": "result",
        },
    )
