from datetime import date, datetime

import sqlalchemy

from ehrql import create_dataset
from ehrql.backends.emis import EMISBackend
from ehrql.query_engines.base_sql import get_setup_and_cleanup_queries
from ehrql.query_language import compile
from ehrql.tables import PatientFrame, Series, table_from_rows
from ehrql.tables.beta import emis
from ehrql.utils.sqlalchemy_query_utils import CreateTableAs, GeneratedTable
from tests.lib.emis_schema import (
    ObservationAllOrgsV2,
    PatientAllOrgsV2,
)

from .helpers import (
    assert_tests_exhaustive,
    assert_types_correct,
    get_all_backend_columns,
    register_test_for,
)


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
    for table, columns in get_all_backend_columns(EMISBackend()):
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
    trino_database.setup(metadata=PatientAllOrgsV2.metadata)
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


@register_test_for(emis.clinical_events)
def test_clinical_events(select_all_emis):
    results = select_all_emis(
        PatientAllOrgsV2(registration_id="1"),
        PatientAllOrgsV2(registration_id="2"),
        ObservationAllOrgsV2(
            registration_id="1",
            effective_date=datetime(2020, 10, 20, 14, 30, 5),
            snomed_concept_id=123,
            value_pq_1=0.5,
        ),
        ObservationAllOrgsV2(
            registration_id="2",
            effective_date=datetime(2022, 1, 15, 12, 30, 5),
            snomed_concept_id=567,
            value_pq_1=None,
        ),
    )
    assert results == [
        {
            "patient_id": "1",
            "date": date(2020, 10, 20),
            "snomedct_code": "123",
            "numeric_value": 0.5,
        },
        {
            "patient_id": "2",
            "date": date(2022, 1, 15),
            "snomedct_code": "567",
            "numeric_value": None,
        },
    ]


@register_test_for(emis.patients)
def test_patients(select_all_emis):
    results = select_all_emis(
        PatientAllOrgsV2(registration_id="1", date_of_birth=date(2020, 1, 1), gender=1),
        # duplicate registration ids are ignored
        PatientAllOrgsV2(registration_id="2", date_of_birth=date(2020, 1, 1), gender=1),
        PatientAllOrgsV2(registration_id="2", date_of_birth=date(2020, 1, 1), gender=1),
        PatientAllOrgsV2(
            registration_id="3",
            date_of_birth=date(1960, 1, 1),
            date_of_death=date(2020, 1, 1),
            gender=2,
        ),
        PatientAllOrgsV2(registration_id="4", date_of_birth=date(2020, 1, 1), gender=0),
        PatientAllOrgsV2(
            registration_id="5", date_of_birth=date(1978, 10, 13), gender=9
        ),
    )
    assert results == [
        {
            "patient_id": "1",
            "date_of_birth": date(2020, 1, 1),
            "sex": "male",
            "date_of_death": None,
        },
        {
            "patient_id": "3",
            "date_of_birth": date(1960, 1, 1),
            "sex": "female",
            "date_of_death": date(2020, 1, 1),
        },
        {
            "patient_id": "4",
            "date_of_birth": date(2020, 1, 1),
            "sex": "unknown",
            "date_of_death": None,
        },
        {
            "patient_id": "5",
            "date_of_birth": date(1978, 10, 13),
            "sex": "unknown",
            "date_of_death": None,
        },
    ]


def test_registered_tests_are_exhaustive():
    assert_tests_exhaustive(EMISBackend())


def test_inline_table_includes_organisation_hash(trino_database):
    # This tests that EMIS's generated inline tables include a column
    # "hashed_organisation", where every row values is the value of the
    # EMIS_ORGANISATION_HASH environment variable
    trino_database.setup(
        PatientAllOrgsV2(registration_id="123abc", date_of_birth=date(2020, 1, 1)),
        PatientAllOrgsV2(registration_id="234abc", date_of_birth=date(2020, 1, 1)),
    )

    # Note that currently inline data tables always make patient_id an integer
    # so in this test, our patient ids from the backend DB are coerced to ints
    # In reality, this means inline tables won't be able to handle real EMIS
    # data (where patient ids are strings) but this will be dealt with
    # later
    # https://github.com/opensafely-core/ehrql/issues/743
    inline_data = [
        ("123abc", 100),
        ("234abc", 200),
    ]

    @table_from_rows(inline_data)
    class t(PatientFrame):
        n = Series(int)

    dataset = create_dataset()
    dataset.define_population(t.exists_for_patient())
    dataset.v = t.n

    backend = EMISBackend()
    query_engine = backend.query_engine_class(
        trino_database.host_url(),
        backend=backend,
    )

    variables = compile(dataset)

    results_query = query_engine.get_query(variables)
    inline_tables = [
        ch
        for ch in results_query.get_children()
        if isinstance(ch, GeneratedTable) and "inline_data" in ch.name
    ]
    assert len(set(inline_tables)) == 1
    inline_table = inline_tables[0]
    setup_queries, cleanup_queries = get_setup_and_cleanup_queries(results_query)

    with query_engine.engine.connect() as connection:
        for setup_query in setup_queries:
            connection.execute(setup_query)
        column_info = connection.execute(
            sqlalchemy.text(f"SHOW COLUMNS FROM {inline_table.name}")
        ).fetchall()
        assert column_info == [
            ("patient_id", "varchar", "", ""),
            ("n", "integer", "", ""),
            ("hashed_organisation", "varchar", "", ""),
        ]
        all_inline_results = connection.execute(
            sqlalchemy.text(f"select * from {inline_table.name}")
        ).fetchall()
        assert sorted(all_inline_results) == [
            ("123abc", 100, "emis_organisation_hash"),
            ("234abc", 200, "emis_organisation_hash"),
        ]

        for cleanup_query in cleanup_queries:
            connection.execute(cleanup_query)

    results = query_engine.get_results(variables)
    assert sorted(results) == [("123abc", 100), ("234abc", 200)]


def test_temp_table_includes_organisation_hash(trino_database):
    # This tests that EMIS's generated tables (created in `reify_query`)
    # include a column "hashed_organisation", where every row values is the
    # value of the EMIS_ORGANISATION_HASH environment variable
    trino_database.setup(
        PatientAllOrgsV2(registration_id="1", date_of_birth=date(2020, 1, 1)),
        PatientAllOrgsV2(registration_id="2", date_of_birth=date(2020, 1, 1)),
    )

    dataset = create_dataset()
    dataset.define_population(emis.patients.date_of_birth.is_not_null())

    backend = EMISBackend()
    query_engine = backend.query_engine_class(
        trino_database.host_url(),
        backend=backend,
    )

    variables = compile(dataset)
    results_query = query_engine.get_query(variables)
    temp_tables = [
        ch
        for ch in results_query.get_children()
        if isinstance(ch, GeneratedTable) and "tmp" in ch.name
    ]
    assert len(set(temp_tables)) == 1
    temp_table = temp_tables[0]
    setup_queries, cleanup_queries = get_setup_and_cleanup_queries(results_query)

    with query_engine.engine.connect() as connection:
        for setup_query in setup_queries:
            connection.execute(setup_query)
        column_info = connection.execute(
            sqlalchemy.text(f"SHOW COLUMNS FROM {temp_table.name}")
        ).fetchall()
        assert column_info == [
            ("patient_id", "varchar(128)", "", ""),
            ("hashed_organisation", "varchar(22)", "", ""),
        ]
        all_temp_table_results = connection.execute(
            sqlalchemy.text(f"select * from {temp_table.name}")
        ).fetchall()
        assert sorted(all_temp_table_results) == [
            ("1", "emis_organisation_hash"),
            ("2", "emis_organisation_hash"),
        ]

        for cleanup_query in cleanup_queries:
            connection.execute(cleanup_query)

    results = query_engine.get_results(variables)
    assert sorted(results) == [("1",), ("2",)]
