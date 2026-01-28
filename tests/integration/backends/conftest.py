import pytest
import sqlalchemy

from ehrql.backends.emis import EMISBackend
from ehrql.backends.tpp import TPPBackend


def _get_select_all_query(request, backend):
    try:
        qm_table = request.function._table
    except AttributeError:  # pragma: no cover
        raise RuntimeError(
            f"Function '{request.function.__name__}' needs the "
            f"`@register_test_for(table)` decorator applied"
        )

    sql_table = backend.get_table_expression(qm_table.name, qm_table.schema)
    columns = [
        # Using `type_coerce(..., None)` like this strips the type information from the
        # SQLAlchemy column meaning we get back the type that the column actually is in
        # database, not the type we've told SQLAlchemy it is.
        sqlalchemy.type_coerce(column, None).label(column.key)
        for column in sql_table.columns
    ]
    return sqlalchemy.select(*columns)


def _select_all_fn(select_all_query, database):
    def _select_all(*input_data):
        database.setup(*input_data)
        with database.engine().connect() as connection:
            results = connection.execute(select_all_query)
            return sorted(
                [row._asdict() for row in results], key=lambda x: x["patient_id"]
            )

    return _select_all


@pytest.fixture
def select_all_emis(request, trino_database):
    select_all_query = _get_select_all_query(request, EMISBackend())
    return _select_all_fn(select_all_query, trino_database)


@pytest.fixture
def select_all_tpp(request, mssql_database):
    backend = TPPBackend(environ={"TEMP_DATABASE_NAME": "temp_tables"})
    select_all_query = _get_select_all_query(request, backend)
    return _select_all_fn(select_all_query, mssql_database)
