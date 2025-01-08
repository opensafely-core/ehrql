import json
from pathlib import Path

import pytest

from ehrql.__main__ import main


FIXTURES_PATH = Path(__file__).parents[1] / "fixtures" / "good_definition_files"


@pytest.mark.parametrize(
    "definition_type,definition_file",
    [
        ("dataset", FIXTURES_PATH / "dataset_definition.py"),
        ("measures", FIXTURES_PATH / "measure_definitions.py"),
        ("test", FIXTURES_PATH / "assurance.py"),
    ],
)
def test_serialize_definition(definition_type, definition_file, capsys):
    main(
        [
            "serialize-definition",
            "--definition-type",
            definition_type,
            str(definition_file),
        ]
    )
    stdout, stderr = capsys.readouterr()
    # We rely on tests elsewhere to ensure that the serialization is working correctly;
    # here we just want to check that we return valid JSON
    assert json.loads(stdout)
    # We shouldn't be producing any warnings or any other output
    assert stderr == ""
