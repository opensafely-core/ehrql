import pytest

from databuilder.query_engines.sqlite import SQLiteQueryEngine
from databuilder.query_language import Dataset

from ..conftest import QueryEngineFixture
from ..lib.databases import InMemorySQLiteDatabase
from ..lib.in_memory import InMemoryDatabase, InMemoryQueryEngine
from ..lib.mock_backend import EventLevelTable, PatientLevelTable
from . import tables


@pytest.fixture(
    scope="session",
    params=["in_memory", "sqlite"],
)
def engine(request):
    name = request.param
    if name == "in_memory":
        return QueryEngineFixture(name, InMemoryDatabase(), InMemoryQueryEngine)
    elif name == "sqlite":
        return QueryEngineFixture(name, InMemorySQLiteDatabase(), SQLiteQueryEngine)
    else:
        assert False


@pytest.fixture
def spec_test(request, engine):
    def run_test(table_data, series, expected_results, population=None):
        # Create SQLAlchemy model instances for each row of each table in table_data.
        input_data = []
        for table, s in table_data.items():
            model = {
                "patient_level_table": PatientLevelTable,
                "event_level_table": EventLevelTable,
            }[table.qm_node.name]
            input_data.extend(model(**row) for row in parse_table(s))

        # Create a Dataset whose population is every patient in table p, with a single
        # variable which is the series under test.
        dataset = Dataset()
        if population:
            dataset.set_population(population)
        else:
            # When the population hasn't been explicitly specified (as it won't be in most specs), we add a patient
            # record for every patient that is mentioned only in event records. This makes it simpler to define the
            # data for specs which only need to mention event records (but which otherwise would give unhelpful results
            # because the patients wouldn't be included in the universe). We also then need to include a variable which
            # references those patients via a patient table in order to include them in the universe.
            populate_missing_patients(input_data)
            dataset.set_population(~tables.p.patient_id.is_null())
            dataset._hidden = tables.p.b1
        dataset.v = series

        # Populate database tables.
        engine.setup(*input_data)

        # Extract data, and check it's as expected.
        results = {r["patient_id"]: r["v"] for r in engine.extract(dataset)}
        assert results == expected_results

    return run_test


def populate_missing_patients(input_data):
    all_patient_ids = {i.PatientId for i in input_data}
    patient_table_ids = {
        i.PatientId for i in input_data if isinstance(i, PatientLevelTable)
    }
    missing_ids = all_patient_ids - patient_table_ids
    input_data.extend(PatientLevelTable(PatientId=id_) for id_ in missing_ids)


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
