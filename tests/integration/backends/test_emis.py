from datetime import date, datetime

import pytest
import sqlalchemy

from ehrql.backends.emis import EMISBackend
from ehrql.query_language import get_tables_from_namespace
from ehrql.tables.beta import emis
from ehrql.utils.sqlalchemy_query_utils import CreateTableAs, GeneratedTable
from tests.lib.emis_schema import (
    ObservationAllOrgsV2,
    PatientAllOrgsV2,
)


REGISTERED_TABLES = set()


# This slightly odd way of supplying the table object to the test function makes the
# tests introspectable in such a way that we can confirm that every table in the module
# is covered by a test
def register_test_for(table):
    def annotate_test_function(fn):
        REGISTERED_TABLES.add(table)
        fn._table = table
        return fn

    return annotate_test_function


@pytest.fixture
def select_all(request, trino_database):
    try:
        ql_table = request.function._table
    except AttributeError:  # pragma: no cover
        raise RuntimeError(
            f"Function '{request.function.__name__}' needs the "
            f"`@register_test_for(table)` decorator applied"
        )

    qm_table = ql_table._qm_node
    backend = EMISBackend()
    sql_table = backend.get_table_expression(qm_table.name, qm_table.schema)
    columns = [
        # Using `type_coerce(..., None)` like this strips the type information from the
        # SQLAlchemy column meaning we get back the type that the column actually is in
        # database, not the type we've told SQLAlchemy it is.
        sqlalchemy.type_coerce(column, None).label(column.key)
        for column in sql_table.columns
    ]
    select_all_query = sqlalchemy.select(*columns)

    def _select_all(*input_data):
        trino_database.setup(*input_data)
        with trino_database.engine().connect() as connection:
            results = connection.execute(select_all_query)
            return sorted(
                [row._asdict() for row in results], key=lambda x: x["patient_id"]
            )

    return _select_all


def test_backend_columns_have_correct_types(trino_database):
    columns_with_types = get_all_backend_columns_with_types(trino_database)
    mismatched = [
        f"{table}.{column} expects {column_type!r} but got {column_args!r}"
        for table, column, column_type, column_args in columns_with_types
        if not types_compatible(column_type, column_args)
    ]
    nl = "\n"
    assert not mismatched, (
        f"Mismatch between columns returned by backend queries"
        f" queries and those expected:\n{nl.join(mismatched)}\n\n"
    )


def types_compatible(column_type, column_args):
    """
    Is this given SQLAlchemy type instance compatible with the supplied dictionary of
    column arguments?
    """
    # It seems we use this sometimes for the patient ID column where we don't care what
    # type it is
    if isinstance(column_type, sqlalchemy.sql.sqltypes.NullType):
        return True
    elif isinstance(column_type, sqlalchemy.Float):
        return column_args["type"] == "real"
    elif isinstance(column_type, sqlalchemy.Date):
        return column_args["type"] == "date"
    elif isinstance(column_type, sqlalchemy.String):
        return column_args["type"].startswith("varchar")
    else:
        assert False, f"Unhandled type: {column_type}"


def get_all_backend_columns_with_types(trino_database):
    """
    For every column on every table we expose in the backend, yield the SQLAlchemy type
    instance we expect to use for that column together with the type information that
    database has for that column so we can check they're compatible
    """
    table_names = set()
    column_types = {}
    queries = []
    for table, columns in get_all_backend_columns():
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


def get_all_backend_columns():
    backend = EMISBackend()
    for _, table in get_all_tables():
        qm_table = table._qm_node
        table_expr = backend.get_table_expression(qm_table.name, qm_table.schema)
        yield qm_table.name, table_expr.columns


@register_test_for(emis.clinical_events)
def test_clinical_events(select_all):
    results = select_all(
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
def test_patients(select_all):
    results = select_all(
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
    missing = [
        name for name, table in get_all_tables() if table not in REGISTERED_TABLES
    ]
    assert not missing, f"No tests for tables: {', '.join(missing)}"


def get_all_tables():
    # in future we're likely to need to get tables from more than one
    # module (e.g. emis.raw)
    for module in [emis]:
        for name, table in get_tables_from_namespace(module):
            yield f"{module.__name__}.{name}", table
