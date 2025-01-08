import contextlib


def test_dump_example_data(call_cli, tmpdir):
    with contextlib.chdir(tmpdir):
        call_cli("dump-example-data")
    filenames = [path.basename for path in (tmpdir / "example-data").listdir()]
    assert "patients.csv" in filenames
