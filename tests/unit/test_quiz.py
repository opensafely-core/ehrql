from pathlib import Path
from unittest.mock import patch

import pytest

from ehrql import quiz, weeks
from ehrql.query_engines.sandbox import SandboxQueryEngine
from ehrql.query_language import Dataset
from ehrql.tables.core import (
    clinical_events,
    medications,
    patients,
    practice_registrations,
)


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


def filtered_medications(
    index_year: int = 2023,
    codelist: list[str] = ["39113611000001102"],
    filter_dates: bool = True,
):
    index_date = f"{index_year}-01-01"
    f = medications.dmd_code.is_in(codelist)
    if filter_dates:
        f = f & medications.date.is_on_or_between(index_date - weeks(52), index_date)
    filtered = medications.where(f)
    return filtered


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
        (clinical_events, clinical_events),
        (medications.dmd_code, medications.dmd_code),
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
def test_dataset_has_missing_or_extra_column(engine, order, message):
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
def test_dataset_has_missing_or_extra_patients(engine, order, message):
    datasets = [dataset_smoketest(), dataset_smoketest(min_age=0, max_age=100)]
    answer, expected = (datasets[i] for i in order)
    msg = quiz.check_answer(engine=engine, answer=answer, expected=expected)
    assert msg == message


def test_dataset_column_has_missing_patients(engine):
    answer = dataset_smoketest()
    expected = dataset_smoketest()
    answer.num_medications = filtered_medications().count_for_patient()
    expected.num_medications = filtered_medications(index_year=2015).count_for_patient()
    msg = quiz.check_answer(engine=engine, answer=answer, expected=expected)
    assert msg == "Column num_medications:\nMissing patient(s): 1."


def test_dataset_has_incorrect_value(engine):
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


@pytest.mark.parametrize(
    "order, message",
    [
        ([1, 0], "Missing row(s): 1, 3, 6, 9, 10, 13, 15, 17, 19, 20."),
        ([0, 1], "Found extra row(s): 1, 3, 6, 9, 10, 13, 15, 17, 19, 20."),
    ],
)
def test_event_table_has_missing_or_extra_rows(engine, order, message):
    tables = [
        clinical_events,
        clinical_events.where(clinical_events.snomedct_code.is_in(["60621009"])),
    ]
    answer, expected = (tables[i] for i in order)
    msg = quiz.check_answer(engine=engine, answer=answer, expected=expected)
    assert msg == message


@pytest.mark.parametrize(
    "order, message",
    [
        ([1, 0], "Missing row(s): 5, 9."),
        ([0, 1], "Found extra row(s): 5, 9."),
    ],
)
def test_event_series_has_missing_or_extra_rows(engine, order, message):
    series = [
        medications.dmd_code,
        medications.where(medications.date.is_on_or_before("2020-12-01")).dmd_code,
    ]
    answer, expected = (series[i] for i in order)
    msg = quiz.check_answer(engine=engine, answer=answer, expected=expected)
    assert msg == message


def test_event_series_has_incorrect_value(engine):
    answer = medications.date
    expected = medications.dmd_code
    msg = quiz.check_answer(engine=engine, answer=answer, expected=expected)
    assert (
        msg
        == "Incorrect value for patient 1, row 1: expected 39113611000001102, got 2014-01-11 instead."
    )


def test_incorrect_event_selection_for_patient(engine):
    events = clinical_events.where(
        clinical_events.snomedct_code.is_in(["60621009"])
    ).sort_by(clinical_events.date)
    answer = events.first_for_patient()
    expected = events.last_for_patient()
    msg = quiz.check_answer(engine=engine, answer=answer, expected=expected)
    # TODO: This might not be the most helpful error message.
    assert (
        msg
        == "Incorrect `numeric_value` value for patient 2: expected 23.1, got 18.4 instead."
    )


def test_unidentified_error_shows_fallback_message(engine):
    with patch("ehrql.quiz.check_patient_table_values", return_value=None):
        msg = quiz.check_answer(
            engine, dataset_smoketest(index_year=2024), dataset_smoketest()
        )
        assert msg.startswith("Incorrect answer.\nExpected:")
