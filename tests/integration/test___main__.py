from databuilder.__main__ import main


def test_test_connection(monkeypatch, mssql_database, capsys):
    monkeypatch.setenv("BACKEND", "databuilder.backends.tpp.TPPBackend")
    monkeypatch.setenv("DATABASE_URL", mssql_database.host_url())
    argv = ["test-connection"]
    main(argv)
    out, _ = capsys.readouterr()
    assert "SUCCESS" in out
