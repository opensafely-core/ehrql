from pathlib import Path

import pytest

from ehrql.__main__ import main
from tests.lib.inspect_utils import function_body_as_string


FIXTURES_PATH = Path(__file__).parents[2] / "fixtures" / "good_definition_files"


def test_generate_dataset_disallows_reading_file_outside_working_directory(
    tmp_path, monkeypatch, capsys
):
    csv_file = tmp_path / "file.csv"
    csv_file.write_text("patient_id,i\n1,10\n2,20")

    @function_body_as_string
    def code():
        from ehrql import create_dataset
        from ehrql.tables import PatientFrame, Series, table_from_file

        @table_from_file("<CSV_FILE>")
        class test_table(PatientFrame):
            i = Series(int)

        dataset = create_dataset()
        dataset.define_population(test_table.exists_for_patient())
        dataset.configure_dummy_data(population_size=2)
        dataset.i = test_table.i

    code = code.replace('"<CSV_FILE>"', repr(str(csv_file)))

    dataset_file = tmp_path / "sub_dir" / "dataset_definition.py"
    dataset_file.parent.mkdir(parents=True, exist_ok=True)
    dataset_file.write_text(code)

    monkeypatch.chdir(dataset_file.parent)
    with pytest.raises(Exception) as e:
        main(["generate-dataset", str(dataset_file)])
    assert "is not contained within the directory" in str(e.value)


@pytest.mark.parametrize("legacy", [True, False])
def test_generate_dataset_passes_dummy_data_config(tmp_path, caplog, legacy):
    @function_body_as_string
    def code():
        from ehrql import create_dataset
        from ehrql.tables.core import patients

        dataset = create_dataset()
        dataset.define_population(patients.exists_for_patient())
        dataset.sex = patients.sex

        dataset.configure_dummy_data(population_size=2, timeout=3, **{})

    code = code.replace("**{}", "legacy=True" if legacy else "")
    dataset_file = tmp_path / "dataset_definition.py"
    dataset_file.write_text(code)

    main(
        [
            "generate-dataset",
            str(dataset_file),
            "--output",
            str(tmp_path / "output.csv"),
        ]
    )

    logs = caplog.text
    assert "Attempting to generate 2 matching patients" in logs
    assert "timeout: 3s" in logs
    if legacy:
        assert "Using legacy dummy data generation" in logs
    else:
        assert "Using next generation dummy data generation" in logs
