import textwrap

import pytest

from tests.lib.inspect_utils import function_body_as_string


def test_debug(call_cli, tmp_path):
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
    captured = call_cli(
        "debug",
        definition_path,
        "--dummy-tables",
        dummy_data_path,
    )
    assert captured.out == ""


def test_debug_rejects_unknown_display_format(call_cli, tmp_path):
    dummy_data_path = tmp_path / "dummy-data"
    dummy_data_path.mkdir()
    definition_path = tmp_path / "show.py"
    definition_path.touch()
    with pytest.raises(SystemExit):
        call_cli(
            "debug",
            definition_path,
            "--dummy-tables",
            dummy_data_path,
            "--display-format",
            "badformat",
        )
    captured = call_cli.readouterr()
    assert "badformat' is not a supported display format" in captured.err


def test_debug_show(tmp_path, call_cli):
    @function_body_as_string
    def definition():
        from ehrql import create_dataset, show
        from ehrql.tables.core import patients

        dataset = create_dataset()
        year = patients.date_of_birth.year
        show(dataset, label="Number")
        dataset.define_population(year > 1980)

    definition_path = tmp_path / "show.py"
    definition_path.write_text(definition)

    DUMMY_DATA = textwrap.dedent(
        """\
        patient_id,date_of_birth
        1,1980-06-01
        2,1985-06-01
        """
    )
    dummy_tables_path = tmp_path / "dummy_tables"
    dummy_tables_path.mkdir()
    dummy_tables_path.joinpath("patients.csv").write_text(DUMMY_DATA)

    captured = call_cli(
        "debug",
        definition_path,
        "--dummy-tables",
        dummy_tables_path,
    )

    expected = textwrap.dedent(
        """\
        Show line 6: Number
        patient_id
        -----------------
        """
    ).strip()
    assert captured.err.strip() == expected
