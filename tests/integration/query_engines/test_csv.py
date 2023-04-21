from pathlib import Path

from ehrql import Dataset
from ehrql.query_engines.csv import CSVQueryEngine
from ehrql.query_engines.in_memory_database import PatientColumn
from ehrql.query_language import compile
from ehrql.tables import EventFrame, PatientFrame, Series, table


FIXTURES = Path(__file__).parents[2] / "fixtures" / "csv_engine"


@table
class patients(PatientFrame):
    sex = Series(str)


@table
class events(EventFrame):
    score = Series(int)
    # Columns in the schema which aren't in the CSV should just end up NULL
    expected_missing = Series(bool)


def test_csv_query_engine():
    dataset = Dataset()
    dataset.sex = patients.sex
    dataset.total_score = events.score.sum_for_patient()
    # Check that missing columns end up NULL
    dataset.missing = events.where(
        events.expected_missing.is_null()
    ).count_for_patient()

    dataset.define_population(patients.exists_for_patient())
    variable_definitions = compile(dataset)

    query_engine = CSVQueryEngine(FIXTURES)
    results = query_engine.get_results(variable_definitions)

    assert list(results) == [
        (1, "M", 9, 3),
        (2, "F", 15, 2),
        (3, None, None, 0),
    ]


def test_csv_query_engine_evaluate():
    query_engine = CSVQueryEngine(FIXTURES)
    result = query_engine.evaluate(patients.sex)
    assert result == PatientColumn({1: "M", 2: "F", 3: None})
