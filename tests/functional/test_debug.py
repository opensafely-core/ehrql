from pathlib import Path

import pytest

from ehrql.__main__ import main
from tests.lib.inspect_utils import function_body_as_string


FIXTURES_PATH = Path(__file__).parents[2] / "fixtures" / "good_definition_files"


def test_debug(capsys, tmp_path):
    # Verify that the debug subcommand can be invoked.
    @function_body_as_string
    def definition():
        from ehrql import create_dataset
        from ehrql.tables.core import patients

        dataset = create_dataset()
        dataset.define_population(patients.date_of_birth.year > 1900)

    definition_path = tmp_path / "show.py"
    definition_path.write_text(definition)

    dummy_data_path = tmp_path / "dummy-data"
    dummy_data_path.mkdir()
    patients_table = dummy_data_path / "patients.csv"
    patients_table.write_text("patient_id,date_of_birth\n1,2020-10-01")
    argv = [
        "debug",
        str(definition_path),
        "--dummy-tables",
        str(dummy_data_path),
    ]
    main(argv)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_debug_rejects_unknown_display_format(capsys, tmp_path):
    dummy_data_path = tmp_path / "dummy-data"
    dummy_data_path.mkdir()
    definition_path = tmp_path / "show.py"
    definition_path.touch()
    argv = [
        "debug",
        str(definition_path),
        "--dummy-tables",
        str(dummy_data_path),
        "--display-format",
        "badformat",
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert "badformat' is not a supported display format" in captured.err
