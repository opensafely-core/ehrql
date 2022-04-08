import pytest

from databuilder.query_engines.sqlite import SQLiteQueryEngine
from databuilder.query_language import Dataset

from ..conftest import QueryEngineFixture
from ..lib.databases import InMemorySQLiteDatabase
from ..lib.in_memory import InMemoryDatabase, InMemoryQueryEngine
from ..lib.mock_backend import EventLevelTable, PatientLevelTable


@pytest.fixture(
    scope="session",
    params=["in_memory", "sqlite"],
)
def engine(request):
    name = request.param
    if name == "in_memory":
        return QueryEngineFixture(name, InMemoryDatabase(), InMemoryQueryEngine)
    elif name == "sqlite":
        return QueryEngineFixture(
            name, InMemorySQLiteDatabase("test_db"), SQLiteQueryEngine
        )
    else:
        assert False


@pytest.fixture
def spec_test(request, engine):
    # While we're developing the SQLite engine we only expect a subset of the spec
    # tests, those we mark with `sql_spec`, to pass against it
    if engine.name == "sqlite":
        marks = [m.name for m in request.node.iter_markers()]
        if "sql_spec" not in marks:
            pytest.xfail()

    def run_test(table_data, series, expected_results):
        # Create SQLAlchemy model instances for each row of each table in table_data.
        input_data = []
        for table, s in table_data.items():
            model = {
                "patient_level_table": PatientLevelTable,
                "event_level_table": EventLevelTable,
            }[table.qm_node.name]
            input_data.extend(model(**row) for row in parse_table(s))

        # Populate database tables.
        engine.setup(*input_data)

        # Create a Dataset whose population is every patient in table p, with a single
        # variable which is the series under test.
        dataset = Dataset()
        dataset.use_unrestricted_population()
        dataset.v = series

        # Extract data, and check it's as expected.
        results = {r["patient_id"]: r["v"] for r in engine.extract(dataset)}
        assert results == expected_results

    return run_test


def parse_table(s):
    """Parse string containing table data, returning list of dicts.

    See test_conftest.py for examples.
    """

    header, _, *lines = s.strip().splitlines()
    col_names = [token.strip() for token in header.split("|")]
    col_names[0] = "PatientId"
    rows = [parse_row(col_names, line) for line in lines]
    return rows


def parse_row(col_names, line):
    """Parse string containing row data, returning list of values.

    See test_conftest.py for examples.
    """

    return {
        col_name: parse_value(col_name, token.strip())
        for col_name, token in zip(col_names, line.split("|"))
    }


def parse_value(col_name, value):
    """Parse string returning value of correct type for column.

    The desired type is determined by the name of the column.  An empty string indicates
    a null value.
    """

    if col_name == "PatientId" or col_name[0] == "i":
        parse = int
    elif col_name[0] == "b":
        parse = lambda v: {"T": True, "F": False}[v]  # noqa E731
    else:
        assert False

    return parse(value) if value else None
