from pathlib import Path

import pytest

import ehrql
from ehrql.query_engines.local_file import LocalFileQueryEngine
from ehrql.query_language import BaseFrame
from ehrql.tables import core


# Example CSV files are given for all core tables
EXAMPLE_TABLES = [getattr(core, table) for table in core.__all__]

EXAMPLE_DATA_DIR = Path(ehrql.__file__).parent / "example-data"


@pytest.mark.parametrize("ql_table", EXAMPLE_TABLES)
def test_populate_database_using_example_data(ql_table: BaseFrame):
    # The engine populates the database with the example data and validates the column
    # specs in the process
    engine = LocalFileQueryEngine(EXAMPLE_DATA_DIR)
    engine.populate_database([ql_table._qm_node], allow_missing_columns=False)
