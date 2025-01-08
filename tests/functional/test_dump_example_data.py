import contextlib

from ehrql.__main__ import main


def test_dump_example_data(tmpdir):
    with contextlib.chdir(tmpdir):
        main(["dump-example-data"])
    filenames = [path.basename for path in (tmpdir / "example-data").listdir()]
    assert "patients.csv" in filenames
