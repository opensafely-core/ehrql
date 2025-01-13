import contextlib


def test_dump_example_data(call_cli, tmp_path):
    with contextlib.chdir(tmp_path):
        call_cli("dump-example-data")
    filenames = [path.name for path in (tmp_path / "example-data").iterdir()]
    assert "patients.csv" in filenames
