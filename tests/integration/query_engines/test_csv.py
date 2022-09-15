import datetime

import pytest
import sqlalchemy
from sqlalchemy.orm import Session, declarative_base

from databuilder.ehrql import Dataset
from databuilder.query_engines.csv import CSVQueryEngine, orm_instances_from_csv_lines
from databuilder.query_language import compile
from databuilder.sqlalchemy_types import TYPE_MAP, Integer, type_from_python_type
from databuilder.tables import EventFrame, PatientFrame, Series, table


def test_csv_query_engine(tmp_path):
    tmp_path.joinpath("patients.csv").write_text(
        "\n".join(
            [
                # Columns like `extra_column` which aren't in the schema should just be
                # ignored
                "patient_id,sex,extra_column",
                "1,M,a",
                "2,F,b",
                "3,,",
            ]
        ),
    )
    tmp_path.joinpath("events.csv").write_text(
        "\n".join(
            [
                "patient_id,score",
                "1,2",
                "1,3",
                "1,4",
                "2,5",
                "2,10",
            ]
        ),
    )

    @table
    class patients(PatientFrame):
        sex = Series(str)

    @table
    class events(EventFrame):
        score = Series(int)
        # Columns in the schema which aren't in the CSV should just end up NULL
        expected_missing = Series(bool)

    dataset = Dataset()
    dataset.sex = patients.sex
    dataset.total_score = events.score.sum_for_patient()
    # Check that missing columns end up NULL
    dataset.missing = events.take(events.expected_missing.is_null()).count_for_patient()

    dataset.set_population(patients.exists_for_patient())
    variable_definitions = compile(dataset)

    query_engine = CSVQueryEngine(tmp_path)
    results = query_engine.get_results(variable_definitions)

    assert list(results) == [
        (1, "M", 9, 3),
        (2, "F", 15, 2),
        (3, None, None, 0),
    ]


def test_csv_query_engine_create_missing(tmp_path):
    @table
    class patients(PatientFrame):
        sex = Series(str)

    @table
    class events(EventFrame):
        date = Series(datetime.date)
        code = Series(str)

    dataset = Dataset()
    dataset.sex = patients.sex
    dataset.set_population(events.exists_for_patient())
    variable_definitions = compile(dataset)

    query_engine = CSVQueryEngine(
        tmp_path, config={"DATABUILDER_CREATE_MISSING_CSV": "True"}
    )
    results = query_engine.get_results(variable_definitions)

    assert list(results) == []

    assert tmp_path.joinpath("patients.csv").read_text() == "patient_id,sex\n"
    assert tmp_path.joinpath("events.csv").read_text() == "patient_id,date,code\n"


@pytest.mark.parametrize(
    "type_,csv_value,expected_value",
    [
        (bool, '""', None),
        (bool, "0", False),
        (bool, "1", True),
        (int, "123", 123),
        (float, "1.23", 1.23),
        (str, "foo", "foo"),
        (datetime.date, "2020-10-20", datetime.date(2020, 10, 20)),
    ],
)
def test_orm_instances_from_csv_lines(type_, csv_value, expected_value):
    column_type = type_from_python_type(type_)

    class Model(declarative_base()):
        __tablename__ = "test"
        pk = sqlalchemy.Column(Integer(), primary_key=True)
        value = sqlalchemy.Column(column_type)

    csv_lines = ["value", csv_value]
    instances = orm_instances_from_csv_lines(Model, csv_lines)

    engine = CSVQueryEngine(None).engine
    Model.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(instances)
        session.flush()
        result = session.query(Model.value).scalar()

    assert result == expected_value


def test_orm_instances_from_csv_lines_params_are_exhaustive():
    # This is dirty but useful, I think. It checks that the parameters to the test
    # include at least one of every type in `sqlalchemy_types`.
    params = test_orm_instances_from_csv_lines.pytestmark[0].args[1]
    types = [arg[0] for arg in params]
    assert set(types) == set(TYPE_MAP)
