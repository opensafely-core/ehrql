from pathlib import Path

import pytest

from ehrql.loaders import (
    DefinitionError,
    load_dataset_definition,
    load_measure_definitions,
)


FIXTURES = Path(__file__).parents[1] / "fixtures" / "bad_definition_files"


def test_load_dataset_definition_no_dataset():
    filename = FIXTURES / "no_dataset.py"
    with pytest.raises(
        DefinitionError, match="Did not find a variable called 'dataset'"
    ):
        load_dataset_definition(filename, user_args=())


def test_load_dataset_definition_not_a_dataset():
    filename = FIXTURES / "not_a_dataset.py"
    with pytest.raises(
        DefinitionError, match=r"'dataset' must be an instance of .*\.Dataset"
    ):
        load_dataset_definition(filename, user_args=())


def test_load_dataset_definition_no_population():
    filename = FIXTURES / "no_population.py"
    with pytest.raises(DefinitionError, match="A population has not been defined"):
        load_dataset_definition(filename, user_args=())


def test_load_measure_definitions_no_measures():
    filename = FIXTURES / "no_measures.py"
    with pytest.raises(
        DefinitionError, match="Did not find a variable called 'measures'"
    ):
        load_measure_definitions(filename, user_args=())


def test_load_measure_definitions_not_measures_instance():
    filename = FIXTURES / "not_measures_instance.py"
    with pytest.raises(
        DefinitionError, match=r"'measures' must be an instance of .*\.Measures"
    ):
        load_measure_definitions(filename, user_args=())


def test_load_measure_definitions_empty_measures():
    filename = FIXTURES / "empty_measures.py"
    with pytest.raises(DefinitionError, match="No measures defined"):
        load_measure_definitions(filename, user_args=())
