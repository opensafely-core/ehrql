from ehrql.backends.emisv2 import EMISV2Backend


def test_emisv2_backend_modify_temp_table_schema():
    username = "my_test_user"
    backend = EMISV2Backend()
    query_engine = backend.get_query_engine(
        f"trino://{username}:password@example.com:443/some_database"
    )
    assert query_engine.temp_table_schema == username


def test_emisv2_backend_metadata():
    backend = EMISV2Backend(
        environ={"EHRQL_METADATA": '{"foo": "bar", "foo1": "bar1"}'}
    )
    query_engine = backend.get_query_engine(dsn=None)
    assert query_engine.get_sqlalchemy_execution_options() == {
        "connect_args": {"client_tags": ["foo=bar", "foo1=bar1"]}
    }
