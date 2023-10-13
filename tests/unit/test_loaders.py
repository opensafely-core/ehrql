import subprocess
import sys
import textwrap
from functools import partial
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from ehrql import loaders
from ehrql.loaders import DefinitionError
from ehrql.query_language import DummyDataConfig


FIXTURES_GOOD = Path(__file__).parents[1] / "fixtures" / "good_definition_files"
FIXTURES_BAD = Path(__file__).parents[1] / "fixtures" / "bad_definition_files"


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


def test_load_measure_definitions(funcs, capsys):
    filename = FIXTURES_GOOD / "measure_definitions.py"
    measures = funcs.load_measure_definitions(filename)
    assert isinstance(measures, list)
    # Check the subprocess doesn't emit warnings
    assert capsys.readouterr().err == ""


def test_load_test_definition(funcs, capsys):
    filename = FIXTURES_GOOD / "assurance.py"
    variables, test_data = funcs.load_test_definition(filename)
    assert isinstance(variables, dict)
    assert isinstance(test_data, dict)
    # Check the subprocess doesn't emit warnings
    assert capsys.readouterr().err == ""


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
@pytest.mark.parametrize(
    "function,status",
    [
        (subprocess.run, "ALLOWED"),
        (loaders.subprocess_run_isolated, "BLOCKED"),
    ],
)
@pytest.mark.skipif(
    not sys.platform.startswith("linux"),
    reason="Subprocess isolation only works on Linux",
)
def test_subprocess_run_isolated(tmp_path, function, status):
    assert loaders.isolation_is_supported()
    # Attempt various sorts of action and print whether or not we were blocked
    code = textwrap.dedent(
        """\
        import os, pathlib, socket, subprocess


        print("Touch: ", end="")
        try:
            pathlib.Path(".").touch()
            print("ALLOWED")
        except PermissionError:
            print("BLOCKED")

        print("Open socket: ", end="")
        try:
            socket.create_connection(("192.0.2.0", 53), timeout=0.001)
        except TimeoutError:
            print("ALLOWED")
        except PermissionError:
            print("BLOCKED")

        print("Exec: ", end="")
        try:
            subprocess.run(["/bin/true"])
            print("ALLOWED")
        except PermissionError:
            print("BLOCKED")

        print("Read env vars: ", end="")
        try:
            pathlib.Path(f"/proc/{os.getppid()}/environ").read_bytes()
            print("ALLOWED")
        except PermissionError:
            print("BLOCKED")
        """
    )
    result = function(
        [sys.executable, "-c", code],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        cwd=tmp_path,
    )
    assert result.stdout == (
        f"Touch: {status}\n"
        f"Open socket: {status}\n"
        f"Exec: {status}\n"
        # Until we can assume "unveil" support we can't block the subprocess reading its
        # parent's environment variables out of /proc; but we leave this test code in
        # place in preparation.
        f"Read env vars: ALLOWED\n"
    )
