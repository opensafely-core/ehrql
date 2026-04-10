from ehrql.backends.emisv2 import EMISV2Backend


def test_emisv2_backend_modify_temp_table_schema():
    username = "my_test_user"
    backend = EMISV2Backend()
    query_engine = backend.get_query_engine(
        f"trino://{username}:password@example.com:443/some_database"
    )
    assert query_engine.temp_table_schema == username
