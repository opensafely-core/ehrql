from datetime import date, datetime

import sqlalchemy

from ehrql.backends.emisv2 import EMISV2Backend
from ehrql.tables import emisv2
from ehrql.utils.sqlalchemy_query_utils import CreateTableAs, GeneratedTable
from tests.backend_schemas.emisv2.schema import (
    Patient,
)

from .helpers import (
    assert_types_correct,
    get_all_backend_columns,
    register_test_for,
)


def test_extract_smoketest_dataset_definition(trino_engine):
    trino_engine.setup(
        # Trino DBAPI's Binary() implementation takes a string and encodes it as UTF-8
        Patient(
            _pk=1,
            patient_id=bytes(range(16)).decode("utf-8"),
            date_of_birth=datetime(2000, 1, 1, 0, 0, 0, 0),
        ),
        Patient(
            _pk=2,
            patient_id=bytes(range(1, 17)).decode("utf-8"),
            date_of_birth=datetime(1900, 1, 1, 0, 0, 0, 0),
        ),
    )

    # This query is a copy of the smoketest dataset definition query in
    # tests/acceptance/external_studies/test-age-distribution/analysis/dataset_definition.py
    from ehrql import create_dataset
    from ehrql.tables.smoketest import patients

    index_year = 2022
    min_age = 18
    max_age = 80

    year_of_birth = patients.date_of_birth.year
    age = index_year - year_of_birth

    dataset = create_dataset()
    dataset.define_population((age >= min_age) & (age <= max_age))
    dataset.age = age

    results = trino_engine.extract(dataset, backend=EMISV2Backend())

    assert results == [{"patient_id": bytes(range(16)), "age": 22}]


def test_backend_columns_have_correct_types(trino_database):
    columns_with_types = get_all_backend_columns_with_types(trino_database)
    assert_types_correct(columns_with_types, trino_database)


def get_all_backend_columns_with_types(trino_database):
    """
    For every column on every table we expose in the backend, yield the SQLAlchemy type
    instance we expect to use for that column together with the type information that
    database has for that column so we can check they're compatible
    """
    table_names = set()
    column_types = {}
    queries = []
    for table, columns in get_all_backend_columns(EMISV2Backend(), trino_database):
        table_names.add(table)
        column_types.update({(table, c.key): c.type for c in columns})
        # Construct a query which selects every column in the table
        select_query = sqlalchemy.select(*[c.label(c.key) for c in columns])
        # Write the results of that query into a temporary table (it will be empty but
        # that's fine, we just want the types)
        # Trino doesn't support actual temporary tables, so really this temp table is
        # a real table that we drop after the test
        temp_table_name = f"temp_{table}"
        temp_table = GeneratedTable.from_query(temp_table_name, select_query)
        queries.append(
            (temp_table_name, temp_table, CreateTableAs(temp_table, select_query))
        )
    # Create all the underlying tables in the database without populating them
    trino_database.setup(metadata=Patient.metadata)
    # Note: we really ought to have something like the setup/cleanup call below to
    # handle materialized query tables (which we happen not to have any of in the EMIS
    # backend at present). But the structure of the `queries` list doesn't currently
    # allow for this and I think there's a wider refactor here which would make this
    # problem go away so I'm going to punt on it for now.
    # queries = add_setup_and_cleanup_queries(queries)
    with trino_database.engine().connect() as connection:
        # Create our "temporary" tables
        for temp_table_name, temp_table, query in queries:
            connection.execute(query)
            # Get the column names, types and collations for all columns in those tables
            query = sqlalchemy.text(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name=:t
                """
            )
            results = list(connection.execute(query, {"t": temp_table_name}))
            table_name = temp_table_name.replace("temp_", "")
            for column, type_name in results:
                column_type = column_types[table_name, column]
                column_args = {"type": type_name}
                yield table_name, column, column_type, column_args

            # Drop the temp table
            temp_table.drop(trino_database.engine())


@register_test_for(emisv2.patients)
def test_patients(select_all_emisv2):
    results = select_all_emisv2(
        Patient(
            _pk=1,
            patient_id=bytes(range(16)).decode("utf-8"),
            date_of_birth=datetime(2000, 1, 1, 0, 0, 0, 0),
            date_of_death=datetime(2023, 5, 12, 0, 0, 0, 0),
            sex="M",
        ),
    )
    assert results == [
        {
            "patient_id": bytes(range(16)),
            "date_of_birth": date(2000, 1, 1),
            "date_of_death": date(2023, 5, 12),
            "sex": "male",
        }
    ]
