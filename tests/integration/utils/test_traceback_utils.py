import re
from pathlib import Path

import pytest

import databuilder
from databuilder.main import CommandError, load_module
from databuilder.tables.beta import smoketest

FIXTURES = Path(__file__).parents[2] / "fixtures" / "bad_dataset_definitions"


def test_traceback_starts_with_user_code():
    filename = FIXTURES / "bad_import.py"
    message = f'Traceback (most recent call last):\n  File "{filename}"'
    with pytest.raises(CommandError, match=re.escape(message)):
        load_module(filename)


def test_traceback_ends_with_user_code():
    filename = FIXTURES / "bad_types.py"
    with pytest.raises(CommandError) as excinfo:
        load_module(filename)
    # We shouldn't have any references to databuilder code in the traceback
    databuilder_root = str(Path(databuilder.__file__).parent)
    assert not re.search(re.escape(databuilder_root), str(excinfo.value))


def test_references_to_failed_imports_from_databuilder_are_not_stripped_out():
    filename = FIXTURES / "bad_import.py"
    with pytest.raises(CommandError) as excinfo:
        load_module(filename)
    # We tried to import a name from `smoketest` which doesn't exist, though the module
    # itself does. Therefore this module should be visible in the traceback.
    assert re.search(re.escape(smoketest.__file__), str(excinfo.value))
