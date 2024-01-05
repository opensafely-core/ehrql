import re
from pathlib import Path

import pytest

import ehrql
from ehrql.loaders import DefinitionError, load_module
from ehrql.tables import smoketest


FIXTURES = Path(__file__).parents[2] / "fixtures" / "bad_definition_files"


def test_traceback_starts_with_user_code():
    filename = FIXTURES / "bad_import.py"
    message = f'Traceback (most recent call last):\n  File "{filename}"'
    with pytest.raises(DefinitionError, match=re.escape(message)):
        load_module(filename)


def test_traceback_ends_with_user_code():
    filename = FIXTURES / "bad_types.py"
    with pytest.raises(DefinitionError) as excinfo:
        load_module(filename)
    # We shouldn't have any references to ehrql code in the traceback
    ehrql_root = str(Path(ehrql.__file__).parent)
    assert not re.search(re.escape(ehrql_root), str(excinfo.value))


def test_references_to_failed_imports_from_ehrql_are_not_stripped_out():
    filename = FIXTURES / "bad_import.py"
    with pytest.raises(DefinitionError) as excinfo:
        load_module(filename)
    # We tried to import a name from `smoketest` which doesn't exist, though the module
    # itself does. Therefore this module should be visible in the traceback.
    assert re.search(re.escape(smoketest.__file__), str(excinfo.value))


def test_traceback_filtering_handles_relative_paths():
    relative_filename = (FIXTURES / "bad_import.py").relative_to(Path.cwd())
    message = r'Traceback \(most recent call last\):\n  File ".*bad_import\.py"'
    with pytest.raises(DefinitionError, match=message):
        load_module(relative_filename)


def test_traceback_filtering_handles_syntax_errors():
    filename = FIXTURES / "bad_syntax.py"
    message = (
        r"^"
        f"Error loading file '{filename}':"
        r"\s+"
        f'File "{filename}", line 1'
        r"\s+"
        r"what even is a Python"
        r"[\s\^]+"
        r"SyntaxError: invalid syntax"
        r"$"
    )
    with pytest.raises(DefinitionError, match=message):
        load_module(filename)
