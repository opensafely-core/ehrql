import pytest

from databuilder.concepts import tables
from databuilder.dsl import categorise
from databuilder.dsl import categorise as dsl_categorise

from .lib.mock_backend import MockPatients, ctv3_event, patient

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


def test_dsl_code_comparisons(cohort_with_population, engine):
    input_data = [
        patient(1, ctv3_event("abc")),
        patient(2, ctv3_event("abc")),
        patient(3, ctv3_event("def")),
    ]
    engine.setup(input_data)

    events = tables.clinical_events
    first_code = (
        events.sort_by(events.code).first_for_patient().select_column(events.code)
    )

    date_categories = {
        "abc": first_code == "abc",
        "not_abc": first_code != "abc",
    }

    data_definition = cohort_with_population
    data_definition.code_group = dsl_categorise(date_categories, default="unknown")

    result = engine.extract(data_definition)

    assert result == [
        {"patient_id": 1, "code_group": "abc"},
        {"patient_id": 2, "code_group": "abc"},
        {"patient_id": 3, "code_group": "not_abc"},
    ]


def test_dsl_date_comparisons(cohort_with_population, engine):
    """
    Exercise comparison (and some boolean) operators in the DSL

    We want to ensure the PatientSeries comparison and boolean operators work
    as expected for date values.  We're using the DSL's categorise function
    here to let us make boolean values against which to match the PatientSeries
    values.
    """
    input_data = [
        patient(1, ctv3_event("abc", "2019-12-31")),
        patient(2, ctv3_event("abc", "2020-02-29")),
        patient(3, ctv3_event("abc", "2020-10-01")),
        patient(4, ctv3_event("abc", "2021-04-07")),
    ]
    engine.setup(input_data)

    events = tables.clinical_events
    first_code_date = (
        events.sort_by(events.date).first_for_patient().select_column(events.date)
    )

    first_half_2020 = (first_code_date >= "2020-01-01") & (
        first_code_date <= "2020-06-30"
    )
    second_half_2020 = (first_code_date >= "2020-07-01") & (
        first_code_date <= "2020-12-31"
    )
    in_2020 = first_half_2020 | second_half_2020
    date_categories = {
        "before_2020": first_code_date < "2020-01-01",
        "in_2020": in_2020,
        "after_2020": first_code_date > "2020-12-31",
    }

    data_definition = cohort_with_population
    data_definition.date_group = dsl_categorise(date_categories, default="unknown")

    result = engine.extract(data_definition)

    assert result == [
        {"patient_id": 1, "date_group": "before_2020"},
        {"patient_id": 2, "date_group": "in_2020"},
        {"patient_id": 3, "date_group": "in_2020"},
        {"patient_id": 4, "date_group": "after_2020"},
    ]
