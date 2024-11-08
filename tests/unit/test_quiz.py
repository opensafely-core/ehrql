from pathlib import Path

import pytest

from ehrql import quiz
from ehrql.query_engines.sandbox import SandboxQueryEngine
from ehrql.query_language import Dataset
from ehrql.tables.core import clinical_events, patients, practice_registrations


@pytest.fixture
def engine():
    path = Path(__file__).parents[2] / "ehrql" / "example-data"
    return SandboxQueryEngine(str(path))


def dataset_smoketest(
    index_year=2022, min_age=18, max_age=80, year_of_birth_column: bool = False
) -> Dataset:
    year_of_birth = patients.date_of_birth.year
    age = index_year - year_of_birth

    dataset = Dataset()
    dataset.define_population((age >= min_age) & (age <= max_age))
    dataset.age = age
    if year_of_birth_column:
        dataset.year_of_birth = patients.date_of_birth.year
    return dataset


@pytest.mark.parametrize(
    "answer, expected, message",
    [
        (1, Dataset(), "Expected Dataset, got int instead."),
        (patients, Dataset(), "Expected Dataset, got Table instead."),
        (patients.date_of_birth, Dataset(), "Expected Dataset, got Series instead."),
        (Dataset(), patients, "Expected Table, got Dataset instead."),
        (patients, patients.date_of_birth, "Expected Series, got Table instead."),
    ],
)
def test_wrong_type_before_evaluation(answer, expected, message):
    msg = quiz.check_answer(engine=None, answer=answer, expected=expected)
    assert msg == message


def test_event_frame_not_converted_to_patient_frame(engine):
    # Wrong type after evaluation
    msg = quiz.check_answer(
        engine=engine,
        answer=clinical_events,
        expected=clinical_events.sort_by(clinical_events.date).last_for_patient(),
    )
    assert msg == "Expected PatientTable, got EventTable instead."


@pytest.mark.parametrize(
    "answer, expected",
    [
        (Dataset(), Dataset()),  # Same syntax but different objects
        (dataset_smoketest(), dataset_smoketest()),
        (patients, patients),
        (patients.date_of_birth, patients.date_of_birth),
    ],
)
def test_same_syntax_correct(engine, answer, expected):
    msg = quiz.check_answer(engine=engine, answer=answer, expected=expected)
    assert msg == "Correct!"


def test_empty_dataset(engine):
    msg = quiz.check_answer(
        engine=engine, answer=Dataset(), expected=dataset_smoketest()
    )
    assert msg == "The dataset is empty."


@pytest.mark.parametrize(
    "order, message",
    [
        ([0, 1], "Missing column(s): year_of_birth."),
        ([1, 0], "Found extra column(s): year_of_birth."),
    ],
)
def test_dataset_missing_or_extra_column(engine, order, message):
    datasets = [dataset_smoketest(), dataset_smoketest(year_of_birth_column=True)]
    answer, expected = (datasets[i] for i in order)
    msg = quiz.check_answer(engine=engine, answer=answer, expected=expected)
    assert msg == message


def test_dataset_typo_in_column_name(engine):
    answer = dataset_smoketest(year_of_birth_column=False)
    answer.yeah_of_birth = patients.date_of_birth.year
    expected = dataset_smoketest(year_of_birth_column=True)
    msg = quiz.check_answer(engine=engine, answer=answer, expected=expected)
    assert (
        msg
        == "Missing column(s): year_of_birth.\nFound extra column(s): yeah_of_birth."
    )


@pytest.mark.parametrize(
    "order, message",
    [
        ([0, 1], "Missing patient(s): 4, 5, 9."),
        ([1, 0], "Found extra patient(s): 4, 5, 9."),
    ],
)
def test_dataset_missing_or_extra_patients(engine, order, message):
    datasets = [dataset_smoketest(), dataset_smoketest(min_age=0, max_age=100)]
    answer, expected = (datasets[i] for i in order)
    msg = quiz.check_answer(engine=engine, answer=answer, expected=expected)
    assert msg == message


def test_dataset_value_incorrect(engine):
    msg = quiz.check_answer(
        engine=engine,
        answer=dataset_smoketest(index_year=2023),
        expected=dataset_smoketest(),
    )
    assert msg == "Incorrect `age` value for patient 1: expected 49, got 50 instead."


@pytest.mark.parametrize(
    "order, message",
    [
        ([0, 1], "Missing patient(s): 7."),
        ([1, 0], "Found extra patient(s): 7."),
    ],
)
def test_patient_series_has_missing_or_extra_patients(engine, order, message):
    series = [
        practice_registrations.for_patient_on("2013-12-01").practice_pseudo_id,
        practice_registrations.for_patient_on("2014-01-01").practice_pseudo_id,
    ]
    answer, expected = (series[i] for i in order)
    msg = quiz.check_answer(engine=engine, answer=answer, expected=expected)
    assert msg == message


def test_patient_series_has_incorrect_value(engine):
    msg = quiz.check_answer(
        engine=engine,
        answer=patients.age_on("2023-12-31"),
        expected=patients.age_on("2022-12-31"),
    )
    assert msg == "Incorrect value for patient 1: expected 49, got 50 instead."
