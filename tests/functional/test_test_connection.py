def test_test_connection(mssql_database, call_cli):
    env = {
        "BACKEND": "ehrql.backends.tpp.TPPBackend",
        "DATABASE_URL": mssql_database.host_url(),
    }
    captured = call_cli("test-connection", environ=env)
    assert "SUCCESS" in captured.out
