import pytest
import sqlalchemy

from ehrql.backends.emis import EMISBackend
from ehrql.backends.tpp import TPPBackend
from ehrql.utils.sqlalchemy_query_utils import add_setup_and_cleanup_queries


def _get_select_all_query(request, backend, database):
    try:
        qm_table = request.function._table
    except AttributeError:  # pragma: no cover
        raise RuntimeError(
            f"Function '{request.function.__name__}' needs the "
            f"`@register_test_for(table)` decorator applied"
        )

    query_engine = backend.get_query_engine(database.host_url())
    sql_table = query_engine.get_table(qm_table)
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
            queries = add_setup_and_cleanup_queries([select_all_query])
            for query in queries:
                if query is not select_all_query:
                    connection.execute(query)
                else:
                    cursor = connection.execute(select_all_query)
                    results = sorted(
                        [row._asdict() for row in cursor], key=lambda x: x["patient_id"]
                    )
        return results

    return _select_all


@pytest.fixture
def select_all_emis(request, trino_database):
    backend = EMISBackend()
    select_all_query = _get_select_all_query(request, backend, trino_database)
    return _select_all_fn(select_all_query, trino_database)


@pytest.fixture
def select_all_tpp(request, mssql_database):
    backend = TPPBackend(
        environ={
            "TEMP_DATABASE_NAME": "temp_tables",
            # Disable GP activation filtering for tests using this fixture
            "EHRQL_PERMISSIONS": '["include_gp_unactivated"]',
        }
    )
    select_all_query = _get_select_all_query(request, backend, mssql_database)
    return _select_all_fn(select_all_query, mssql_database)
