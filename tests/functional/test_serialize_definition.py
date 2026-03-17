import json
from pathlib import Path

import pytest


FIXTURES_PATH = Path(__file__).parents[1] / "fixtures" / "good_definition_files"


@pytest.mark.parametrize(
    "definition_file",
    [
        FIXTURES_PATH / "dataset_definition.py",
        FIXTURES_PATH / "measure_definitions.py",
        FIXTURES_PATH / "assurance.py",
    ],
)
def test_serialize_definition(definition_file, call_cli):
    captured = call_cli(
        "serialize-definition",
        definition_file,
    )
    # We rely on tests elsewhere to ensure that the serialization is working correctly;
    # here we just want to check that we return valid JSON
    assert json.loads(captured.out)
    # We shouldn't be producing any warnings or any other output
    assert captured.err == ""
