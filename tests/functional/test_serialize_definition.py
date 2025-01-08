import json
from pathlib import Path

import pytest


FIXTURES_PATH = Path(__file__).parents[1] / "fixtures" / "good_definition_files"


@pytest.mark.parametrize(
    "definition_type,definition_file",
    [
        ("dataset", FIXTURES_PATH / "dataset_definition.py"),
        ("measures", FIXTURES_PATH / "measure_definitions.py"),
        ("test", FIXTURES_PATH / "assurance.py"),
    ],
)
def test_serialize_definition(definition_type, definition_file, call_cli):
    captured = call_cli(
        "serialize-definition",
        "--definition-type",
        definition_type,
        definition_file,
    )
    # We rely on tests elsewhere to ensure that the serialization is working correctly;
    # here we just want to check that we return valid JSON
    assert json.loads(captured.out)
    # We shouldn't be producing any warnings or any other output
    assert captured.err == ""
