from pathlib import Path

import pytest

from tests.lib.inspect_utils import function_body_as_string


FIXTURES_PATH = Path(__file__).parents[1] / "fixtures" / "good_definition_files"


def test_assure(call_cli):
    captured = call_cli("assure", FIXTURES_PATH / "assurance.py")
    assert "All OK" in captured.out


def test_assure_with_test_failures(call_cli, tmp_path):
    @function_body_as_string
    def dataset_definition_with_tests():
        from ehrql import create_dataset
        from ehrql.tables.core import patients

        dataset = create_dataset()
        dataset.define_population(patients.sex == "female")

        test_data = {  # noqa: F841
            1: {
                "patients": {"sex": "male"},
                "expected_in_population": True,
            },
        }

    test_data_file = tmp_path / "dataset_definition.py"
    test_data_file.write_text(dataset_definition_with_tests)

    with pytest.raises(SystemExit):
        call_cli("assure", test_data_file)
    output = call_cli.readouterr().err
    # Assurance test results are written to stderr
    assert "AssuranceTestError" in output
    assert "Validate test data: All OK!" in output
    assert "Validate results: Found errors with 1 patient" in output
