from pathlib import Path

import pytest

import ehrql
from ehrql.query_engines.local_file import LocalFileQueryEngine
from ehrql.query_language import EventFrame
from ehrql.tables import core, tpp


# Example csv files are given for all core tables (although the tutorial imports them from the tpp module)
CORE_TABLES = [getattr(core, table) for table in core.__all__]
# Example csv files are given for these tables that are currently only available for tpp
TPP_TABLES = [tpp.addresses, tpp.practice_registrations]

EXAMPLE_TABLES = CORE_TABLES + TPP_TABLES
EXAMPLE_DATA_DIR = Path(ehrql.__file__).parent / "example-data"


@pytest.mark.parametrize("ql_table", EXAMPLE_TABLES)
def test_populate_database_using_example_data(ql_table: EventFrame):
    # The engine populates the database with the example data and validates the column specs in the process
    engine = LocalFileQueryEngine(EXAMPLE_DATA_DIR)
    engine.populate_database([ql_table._qm_node])
