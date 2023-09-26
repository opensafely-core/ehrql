import csv
from datetime import date

import pytest
import sqlalchemy

from ehrql import Dataset
from ehrql.query_language import PatientFrame, Series, table_from_file, table_from_rows
from ehrql.query_model.nodes import Value
from ehrql.tables.beta.core import clinical_events, patients


def test_handles_degenerate_population(engine):
    # Specifying a population of "False" is obviously silly, but it's more work to
    # identify and reject just this kind of silliness than it is to handle it gracefully
    engine.setup(metadata=sqlalchemy.MetaData())
    variables = dict(
        population=Value(False),
        v=Value(1),
    )
    assert engine.extract_qm(variables) == []


def test_handles_inline_patient_table(engine, tmp_path):
    # Test that a temporary inline patient table, as used by table_from_rows and
    # table_from_file decorators is created and is correctly acessible

    engine.populate(
        {
            patients: [
                dict(patient_id=1, date_of_birth=date(1980, 1, 1)),
                dict(patient_id=2, date_of_birth=date(1990, 2, 2)),
                dict(patient_id=3, date_of_birth=date(2000, 3, 3)),
                dict(patient_id=4, date_of_birth=date(2010, 4, 4)),
            ]
        }
    )

    file_rows = [
        ("patient_id", "i", "s", "d"),
        (1, 10, "a", date(2021, 1, 1)),
        (2, 20, "b", date(2022, 2, 2)),
        (3, None, "c", date(2023, 3, 3)),
        (4, 40, "d", None),
    ]

    file_path = tmp_path / "test.csv"
    with file_path.open("w") as f:
        writer = csv.writer(f)
        writer.writerows(file_rows)

    @table_from_file(file_path)
    class test_table(PatientFrame):
        i = Series(int)
        s = Series(str)
        d = Series(date)

    dataset = Dataset()
    dataset.define_population(
        patients.exists_for_patient() & test_table.exists_for_patient()
    )

    dataset.n = test_table.i + (test_table.i * 10)
    dataset.age = patients.age_on(test_table.d)
    dataset.s = test_table.s

    results = engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "age": 41, "n": 110, "s": "a"},
        {"patient_id": 2, "age": 32, "n": 220, "s": "b"},
        {"patient_id": 3, "age": 23, "n": None, "s": "c"},
        {"patient_id": 4, "age": None, "n": 440, "s": "d"},
    ]


def test_handles_inline_patient_table_with_different_patients(engine):
    engine.populate(
        {
            patients: [
                dict(patient_id=1, sex="female"),
            ]
        }
    )

    # This inline table contains patients which are not in the patients table
    @table_from_rows(
        [
            (1, 10),
            (2, 20),
            (3, 30),
        ]
    )
    class test_table(PatientFrame):
        i = Series(int)

    dataset = Dataset()
    dataset.define_population(test_table.exists_for_patient())
    dataset.n = test_table.i + 100
    dataset.sex = patients.sex

    results = engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "n": 110, "sex": "female"},
        {"patient_id": 2, "n": 120, "sex": None},
        {"patient_id": 3, "n": 130, "sex": None},
    ]


def test_cleans_up_temporary_tables(engine):
    # Cleanup doesn't apply to the in-memory engine
    if engine.name == "in_memory":
        pytest.skip()

    engine.populate(
        {
            clinical_events: [
                dict(patient_id=1, date=date(2000, 1, 1)),
                dict(patient_id=1, date=date(2001, 1, 1)),
                dict(patient_id=2, date=date(2002, 1, 1)),
            ]
        }
    )
    original_tables = _get_tables(engine)

    @table_from_rows(
        [
            (1, 10),
            (2, 20),
        ]
    )
    class inline_table(PatientFrame):
        i = Series(int)

    dataset = Dataset()
    dataset.define_population(clinical_events.exists_for_patient())
    dataset.n = clinical_events.count_for_patient()
    dataset.i = inline_table.i

    results = engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "n": 2, "i": 10},
        {"patient_id": 2, "n": 1, "i": 20},
    ]

    # Check that the tables we're left with match those we started with
    final_tables = _get_tables(engine)
    assert final_tables == original_tables


def _get_tables(engine):
    inspector = sqlalchemy.inspect(engine.sqlalchemy_engine())
    return sorted(inspector.get_table_names())
