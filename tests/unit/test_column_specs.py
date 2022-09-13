import datetime

from databuilder.codes import SNOMEDCTCode
from databuilder.column_specs import ColumnSpec, get_column_specs
from databuilder.query_model import (
    AggregateByPatient,
    SelectColumn,
    SelectPatientTable,
    TableSchema,
)


def test_get_column_specs():
    patients = SelectPatientTable(
        "patients",
        schema=TableSchema({"date_of_birth": datetime.date, "code": SNOMEDCTCode}),
    )
    variables = dict(
        population=AggregateByPatient.Exists(patients),
        dob=SelectColumn(patients, "date_of_birth"),
        code=SelectColumn(patients, "code"),
    )
    column_specs = get_column_specs(variables)
    assert column_specs == {
        "patient_id": ColumnSpec(type=int, nullable=False),
        "dob": ColumnSpec(type=datetime.date, nullable=True),
        "code": ColumnSpec(type=str, nullable=True),
    }
