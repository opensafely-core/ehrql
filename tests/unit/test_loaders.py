import sys
from functools import partial
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from ehrql import loaders
from ehrql.loaders import DefinitionError
from ehrql.measures.measures import DisclosureControlConfig
from ehrql.query_language import DummyDataConfig


FIXTURES_GOOD = Path(__file__).parents[1] / "fixtures" / "good_definition_files"
FIXTURES_BAD = Path(__file__).parents[1] / "fixtures" / "bad_definition_files"
FIXTURES_SANDBOX = Path(__file__).parents[1] / "fixtures" / "sandbox"


# Parameterize all tests over all three of the isolated subprocess, subprocess and
# unsafe versions of the loader functions so we can check they all behave the same
@pytest.fixture(
    params=[
        pytest.param(
            ("subprocess", True),
            marks=pytest.mark.skipif(
                not sys.platform.startswith("linux"),
                reason="Subprocess isolation only works on Linux",
            ),
        ),
        ("subprocess", False),
        ("unsafe", None),
    ]
)
def funcs(request):
    default_kwargs = {"user_args": (), "environ": {}}
    loader_type, use_isolation = request.param
    if loader_type == "subprocess":
        funcs = SimpleNamespace(
            load_dataset_definition=partial(
                loaders.load_dataset_definition, **default_kwargs
            ),
            load_measure_definitions=partial(
                loaders.load_measure_definitions, **default_kwargs
            ),
            load_test_definition=partial(
                loaders.load_test_definition, **default_kwargs
            ),
            load_debug_definition=partial(
                loaders.load_debug_definition, **default_kwargs
            ),
        )
    elif loader_type == "unsafe":
        funcs = SimpleNamespace(
            load_dataset_definition=partial(
                loaders.load_definition_unsafe, "dataset", **default_kwargs
            ),
            load_measure_definitions=partial(
                loaders.load_definition_unsafe, "measures", **default_kwargs
            ),
            load_test_definition=partial(
                loaders.load_definition_unsafe, "test", **default_kwargs
            ),
            load_debug_definition=partial(
                loaders.load_definition_unsafe, "debug", **default_kwargs
            ),
        )
    else:
        assert False
    with patch.object(loaders, "isolation_is_supported", return_value=use_isolation):
        yield funcs


def test_load_dataset_definition(funcs, capsys):
    filename = FIXTURES_GOOD / "dataset_definition.py"
    variables, dummy_data_config = funcs.load_dataset_definition(filename)
    assert isinstance(variables, dict)
    assert isinstance(dummy_data_config, DummyDataConfig)
    # Check the subprocess doesn't emit warnings
    assert capsys.readouterr().err == ""


def test_load_dataset_definition_with_print(funcs, capsys):
    filename = FIXTURES_GOOD / "dataset_definition_with_print.py"
    variables, dummy_data_config = funcs.load_dataset_definition(filename)
    assert isinstance(variables, dict)
    assert isinstance(dummy_data_config, DummyDataConfig)
    out, err = capsys.readouterr()
    assert "user stdout" not in out
    assert "user stdout" in err


def test_load_measure_definitions(funcs, capsys):
    filename = FIXTURES_GOOD / "measure_definitions.py"
    (
        measures,
        dummy_data_config,
        disclosure_control_config,
    ) = funcs.load_measure_definitions(filename)
    assert isinstance(measures, list)
    assert isinstance(dummy_data_config, DummyDataConfig)
    assert isinstance(disclosure_control_config, DisclosureControlConfig)
    # Check the subprocess doesn't emit warnings
    assert capsys.readouterr().err == ""


def test_load_test_definition(funcs, capsys):
    filename = FIXTURES_GOOD / "assurance.py"
    variables, test_data = funcs.load_test_definition(filename)
    assert isinstance(variables, dict)
    assert isinstance(test_data, dict)
    # Check the subprocess doesn't emit warnings
    assert capsys.readouterr().err == ""


def test_load_debug_dataset_definition(funcs, capsys):
    filename = FIXTURES_GOOD / "debug_definition.py"
    funcs.load_debug_definition(
        filename, dummy_tables_path=FIXTURES_SANDBOX, render_format="ascii"
    )
    # debug() messages are sent to stderr during the loading process
    assert (
        capsys.readouterr().err.strip()
        == """
Debug line 8:
'Hello'
""".strip()
    )
    assert capsys.readouterr().out == ""


def test_load_dataset_definition_passes_stderr_through(funcs, capsys):
    filename = FIXTURES_GOOD / "chatty_dataset_definition.py"
    funcs.load_dataset_definition(filename)
    assert capsys.readouterr().err == "I am a bit chatty\n"


def test_load_dataset_definition_no_dataset(funcs):
    filename = FIXTURES_BAD / "no_dataset.py"
    with pytest.raises(
        DefinitionError, match="Did not find a variable called 'dataset'"
    ):
        funcs.load_dataset_definition(filename)


def test_load_dataset_definition_not_a_dataset(funcs):
    filename = FIXTURES_BAD / "not_a_dataset.py"
    with pytest.raises(
        DefinitionError, match=r"'dataset' must be an instance of .*\.Dataset"
    ):
        funcs.load_dataset_definition(filename)


def test_load_dataset_definition_no_population(funcs):
    filename = FIXTURES_BAD / "no_population.py"
    with pytest.raises(DefinitionError, match="A population has not been defined"):
        funcs.load_dataset_definition(filename)


def test_load_dataset_definition_bad_syntax(funcs):
    filename = FIXTURES_BAD / "bad_syntax.py"
    with pytest.raises(DefinitionError, match="what even is a Python"):
        funcs.load_dataset_definition(filename)


def test_load_dataset_definition_operator_error(funcs):
    filename = FIXTURES_BAD / "operator_error.py"
    with pytest.raises(
        DefinitionError,
        match=(
            "WARNING: The `|` operator has different precedence rules from the "
            "normal `or` operator"
        ),
    ):
        funcs.load_dataset_definition(filename)


def test_load_measure_definitions_no_measures(funcs):
    filename = FIXTURES_BAD / "no_measures.py"
    with pytest.raises(
        DefinitionError, match="Did not find a variable called 'measures'"
    ):
        funcs.load_measure_definitions(filename)


def test_load_measure_definitions_not_measures_instance(funcs):
    filename = FIXTURES_BAD / "not_measures_instance.py"
    with pytest.raises(
        DefinitionError, match=r"'measures' must be an instance of .*\.Measures"
    ):
        funcs.load_measure_definitions(filename)


def test_load_measure_definitions_empty_measures(funcs):
    filename = FIXTURES_BAD / "empty_measures.py"
    with pytest.raises(DefinitionError, match="No measures defined"):
        funcs.load_measure_definitions(filename)


@pytest.mark.parametrize(
    "environ,expected",
    [
        ({}, False),
        ({"DATABASE_URL": "foo://bar"}, True),
        ({"EHRQL_ISOLATE_USER_CODE": "always"}, True),
        ({"EHRQL_ISOLATE_USER_CODE": "never"}, False),
        ({"EHRQL_ISOLATE_USER_CODE": "never", "DATABASE_URL": "foo://bar"}, False),
    ],
)
def test_isolation_is_required(environ, expected):
    assert loaders.isolation_is_required(environ) == expected


def test_isolation_is_required_rejects_unknown_values():
    with pytest.raises(RuntimeError, match="Invalid value"):
        loaders.isolation_is_required({"EHRQL_ISOLATE_USER_CODE": "maybe"})


@patch.object(loaders, "isolation_is_supported", return_value=False)
def test_load_definition_raises_error_if_isolation_required_but_unavailable(_):
    filename = FIXTURES_GOOD / "dataset_definition.py"
    with pytest.raises(RuntimeError, match="current environment does not support"):
        loaders.load_dataset_definition(
            filename,
            user_args=(),
            environ={"EHRQL_ISOLATE_USER_CODE": "always"},
        )


def test_load_definition_unsafe_raises_error_if_isolation_required():
    filename = FIXTURES_GOOD / "dataset_definition.py"
    with pytest.raises(RuntimeError, match="call to unsafe loader function"):
        loaders.load_definition_unsafe(
            "dataset",
            filename,
            user_args=(),
            environ={"EHRQL_ISOLATE_USER_CODE": "always"},
        )


# Confirm that various things we can do in an ordinary subprocess are blocked in an
# isolated subprocess
@pytest.mark.skipif(
    not sys.platform.startswith("linux"),
    reason="Subprocess isolation only works on Linux",
)
def test_isolation_report(tmp_path):
    assert loaders.isolation_is_supported()
    assert loaders.isolation_report(tmp_path) == {
        "subprocess.run": {
            "touch": "ALLOWED",
            "open_socket": "ALLOWED",
            "exec": "ALLOWED",
            "read_env_vars": "ALLOWED",
        },
        "subprocess_run_isolated": {
            "touch": "BLOCKED",
            "open_socket": "BLOCKED",
            "exec": "BLOCKED",
            "read_env_vars": "BLOCKED",
        },
    }
