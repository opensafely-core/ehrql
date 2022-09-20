import datetime

from databuilder.codes import SNOMEDCTCode
from databuilder.column_specs import ColumnSpec, get_categories, get_column_specs
from databuilder.query_model import (
    AggregateByPatient,
    Column,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    TableSchema,
)


def test_get_column_specs():
    patients = SelectPatientTable(
        "patients",
        schema=TableSchema(
            date_of_birth=Column(datetime.date),
            code=Column(SNOMEDCTCode),
            category=Column(
                SNOMEDCTCode,
                categories=(SNOMEDCTCode("abc"), SNOMEDCTCode("def")),
            ),
        ),
    )
    variables = dict(
        population=AggregateByPatient.Exists(patients),
        dob=SelectColumn(patients, "date_of_birth"),
        code=SelectColumn(patients, "code"),
        category=SelectColumn(patients, "category"),
    )
    column_specs = get_column_specs(variables)
    assert column_specs == {
        "patient_id": ColumnSpec(type=int, nullable=False, categories=None),
        "dob": ColumnSpec(type=datetime.date, nullable=True, categories=None),
        "code": ColumnSpec(type=str, nullable=True, categories=None),
        "category": ColumnSpec(type=str, nullable=True, categories=("abc", "def")),
    }


events = SelectTable(
    "events",
    schema=TableSchema(
        event_type=Column(str, categories=("a", "b", "c")),
        event_name=Column(str),
    ),
)
event_type = SelectColumn(events, "event_type")


def test_get_categories_default_implementation():
    assert get_categories(AggregateByPatient.Exists(events)) is None


def test_get_categories_for_select_column():
    assert get_categories(event_type) == ("a", "b", "c")


def test_get_categories_for_min_max():
    assert get_categories(AggregateByPatient.Min(event_type)) == ("a", "b", "c")
    assert get_categories(AggregateByPatient.Max(event_type)) == ("a", "b", "c")
