from databuilder.__main__ import main


def test_test_connection(monkeypatch, database, capsys):
    monkeypatch.setenv("BACKEND", "tpp")
    monkeypatch.setenv("DATABASE_URL", database.host_url())
    argv = ["test-connection"]
    main(argv)
    out, _ = capsys.readouterr()
    assert "SUCCESS" in out
