from pathlib import Path

import pytest

from ehrql.loaders import (
    DefinitionError,
    load_dataset_definition,
    load_measure_definitions,
    load_test_definition,
)
from ehrql.query_language import DummyDataConfig


FIXTURES_GOOD = Path(__file__).parents[1] / "fixtures" / "good_definition_files"
FIXTURES_BAD = Path(__file__).parents[1] / "fixtures" / "bad_definition_files"


def test_load_dataset_definition():
    filename = FIXTURES_GOOD / "dataset_definition.py"
    variables, dummy_data_config = load_dataset_definition(filename, user_args=())
    assert isinstance(variables, dict)
    assert isinstance(dummy_data_config, DummyDataConfig)


def test_load_measure_definitions():
    filename = FIXTURES_GOOD / "measure_definitions.py"
    measures = load_measure_definitions(filename, user_args=())
    assert isinstance(measures, list)


def test_load_test_definition():
    filename = FIXTURES_GOOD / "assurance.py"
    variables, test_data = load_test_definition(filename, user_args=())
    assert isinstance(variables, dict)
    assert isinstance(test_data, dict)


def test_load_dataset_definition_no_dataset():
    filename = FIXTURES_BAD / "no_dataset.py"
    with pytest.raises(
        DefinitionError, match="Did not find a variable called 'dataset'"
    ):
        load_dataset_definition(filename, user_args=())


def test_load_dataset_definition_not_a_dataset():
    filename = FIXTURES_BAD / "not_a_dataset.py"
    with pytest.raises(
        DefinitionError, match=r"'dataset' must be an instance of .*\.Dataset"
    ):
        load_dataset_definition(filename, user_args=())


def test_load_dataset_definition_no_population():
    filename = FIXTURES_BAD / "no_population.py"
    with pytest.raises(DefinitionError, match="A population has not been defined"):
        load_dataset_definition(filename, user_args=())


def test_load_dataset_definition_bad_syntax():
    filename = FIXTURES_BAD / "bad_syntax.py"
    with pytest.raises(DefinitionError, match="what even is a Python"):
        load_dataset_definition(filename, user_args=())


def test_load_measure_definitions_no_measures():
    filename = FIXTURES_BAD / "no_measures.py"
    with pytest.raises(
        DefinitionError, match="Did not find a variable called 'measures'"
    ):
        load_measure_definitions(filename, user_args=())


def test_load_measure_definitions_not_measures_instance():
    filename = FIXTURES_BAD / "not_measures_instance.py"
    with pytest.raises(
        DefinitionError, match=r"'measures' must be an instance of .*\.Measures"
    ):
        load_measure_definitions(filename, user_args=())


def test_load_measure_definitions_empty_measures():
    filename = FIXTURES_BAD / "empty_measures.py"
    with pytest.raises(DefinitionError, match="No measures defined"):
        load_measure_definitions(filename, user_args=())
