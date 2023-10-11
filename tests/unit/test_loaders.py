from functools import partial
from pathlib import Path
from types import SimpleNamespace

import pytest

from ehrql import loaders
from ehrql.loaders import DefinitionError
from ehrql.query_language import DummyDataConfig


FIXTURES_GOOD = Path(__file__).parents[1] / "fixtures" / "good_definition_files"
FIXTURES_BAD = Path(__file__).parents[1] / "fixtures" / "bad_definition_files"


# Parameterize all tests over both the subprocess-using and unsafe versions of the
# loader functions so we can check they all behave the same
@pytest.fixture(params=["subprocess", "unsafe"])
def funcs(request):
    if request.param == "subprocess":
        return SimpleNamespace(
            load_dataset_definition=loaders.load_dataset_definition,
            load_measure_definitions=loaders.load_measure_definitions,
            load_test_definition=loaders.load_test_definition,
        )
    elif request.param == "unsafe":
        return SimpleNamespace(
            load_dataset_definition=partial(loaders.load_definition_unsafe, "dataset"),
            load_measure_definitions=partial(
                loaders.load_definition_unsafe, "measures"
            ),
            load_test_definition=partial(loaders.load_definition_unsafe, "test"),
        )
    else:
        assert False


def test_load_dataset_definition(funcs, capsys):
    filename = FIXTURES_GOOD / "dataset_definition.py"
    variables, dummy_data_config = funcs.load_dataset_definition(filename, user_args=())
    assert isinstance(variables, dict)
    assert isinstance(dummy_data_config, DummyDataConfig)
    # Check the subprocess doesn't emit warnings
    assert capsys.readouterr().err == ""


def test_load_measure_definitions(funcs, capsys):
    filename = FIXTURES_GOOD / "measure_definitions.py"
    measures = funcs.load_measure_definitions(filename, user_args=())
    assert isinstance(measures, list)
    # Check the subprocess doesn't emit warnings
    assert capsys.readouterr().err == ""


def test_load_test_definition(funcs, capsys):
    filename = FIXTURES_GOOD / "assurance.py"
    variables, test_data = funcs.load_test_definition(filename, user_args=())
    assert isinstance(variables, dict)
    assert isinstance(test_data, dict)
    # Check the subprocess doesn't emit warnings
    assert capsys.readouterr().err == ""


def test_load_dataset_definition_passes_stderr_through(funcs, capsys):
    filename = FIXTURES_GOOD / "chatty_dataset_definition.py"
    funcs.load_dataset_definition(filename, user_args=())
    assert capsys.readouterr().err == "I am a bit chatty\n"


def test_load_dataset_definition_no_dataset(funcs):
    filename = FIXTURES_BAD / "no_dataset.py"
    with pytest.raises(
        DefinitionError, match="Did not find a variable called 'dataset'"
    ):
        funcs.load_dataset_definition(filename, user_args=())


def test_load_dataset_definition_not_a_dataset(funcs):
    filename = FIXTURES_BAD / "not_a_dataset.py"
    with pytest.raises(
        DefinitionError, match=r"'dataset' must be an instance of .*\.Dataset"
    ):
        funcs.load_dataset_definition(filename, user_args=())


def test_load_dataset_definition_no_population(funcs):
    filename = FIXTURES_BAD / "no_population.py"
    with pytest.raises(DefinitionError, match="A population has not been defined"):
        funcs.load_dataset_definition(filename, user_args=())


def test_load_dataset_definition_bad_syntax(funcs):
    filename = FIXTURES_BAD / "bad_syntax.py"
    with pytest.raises(DefinitionError, match="what even is a Python"):
        funcs.load_dataset_definition(filename, user_args=())


def test_load_measure_definitions_no_measures(funcs):
    filename = FIXTURES_BAD / "no_measures.py"
    with pytest.raises(
        DefinitionError, match="Did not find a variable called 'measures'"
    ):
        funcs.load_measure_definitions(filename, user_args=())


def test_load_measure_definitions_not_measures_instance(funcs):
    filename = FIXTURES_BAD / "not_measures_instance.py"
    with pytest.raises(
        DefinitionError, match=r"'measures' must be an instance of .*\.Measures"
    ):
        funcs.load_measure_definitions(filename, user_args=())


def test_load_measure_definitions_empty_measures(funcs):
    filename = FIXTURES_BAD / "empty_measures.py"
    with pytest.raises(DefinitionError, match="No measures defined"):
        funcs.load_measure_definitions(filename, user_args=())
