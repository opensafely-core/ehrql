import pytest

from databuilder.dsl import categorise

from .lib.mock_backend import MockPatients, patient

# Mark the whole module as containing integration tests
pytestmark = pytest.mark.integration


def test_categorise_simple_comparisons(engine, cohort_with_population):
    input_data = [patient(1, height=180), patient(2, height=200.5), patient(3)]
    engine.setup(input_data)

    patients = MockPatients()
    height = patients.select_column(patients.height)
    height_categories = {
        "tall": height > 190,
        "short": height <= 190,
    }
    height_group = categorise(height_categories, default="missing")
    cohort = cohort_with_population
    cohort.height_group = height_group

    result = engine.extract(cohort)
    assert result == [
        dict(patient_id=1, height_group="short"),
        dict(patient_id=2, height_group="tall"),
        dict(patient_id=3, height_group="missing"),
    ]


def test_comparator_order(engine, cohort_with_population):
    """Test that comparison operators work on both sides of the comparator"""
    input_data = [patient(1, height=180), patient(2, height=200.5), patient(3)]
    engine.setup(input_data)

    patients = MockPatients()
    height = patients.select_column(patients.height)
    height_categories = {
        "tall": 190 < height,
        "short": 190 >= height,
    }
    height_group = categorise(height_categories, default="missing")
    cohort = cohort_with_population
    cohort.height_group = height_group

    result = engine.extract(cohort)
    assert result == [
        dict(patient_id=1, height_group="short"),
        dict(patient_id=2, height_group="tall"),
        dict(patient_id=3, height_group="missing"),
    ]
