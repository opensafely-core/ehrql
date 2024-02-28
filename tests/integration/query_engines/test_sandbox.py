from pathlib import Path

from ehrql.query_engines.in_memory_database import PatientColumn
from ehrql.query_engines.sandbox import SandboxQueryEngine
from ehrql.tables import PatientFrame, Series, table


FIXTURES = Path(__file__).parents[2] / "fixtures" / "local_file_engine"


@table
class patients(PatientFrame):
    sex = Series(str)


def test_csv_query_engine_evaluate():
    query_engine = SandboxQueryEngine(FIXTURES)
    result = query_engine.evaluate(patients.sex)
    assert result == PatientColumn({1: "M", 2: "F", 3: None})
