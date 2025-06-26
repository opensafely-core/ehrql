import contextlib


def test_dump_example_data(call_cli, tmp_path):
    with contextlib.chdir(tmp_path):
        call_cli("dump-example-data")
    filenames = [path.name for path in (tmp_path / "example-data").iterdir()]
    assert "patients.csv" in filenames


def test_dump_example_data_to_custom_dir(call_cli, tmp_path):
    with contextlib.chdir(tmp_path):
        call_cli("dump-example-data", "-d", "custom-dir")
    filenames = [path.name for path in (tmp_path / "custom-dir").iterdir()]
    assert "patients.csv" in filenames
