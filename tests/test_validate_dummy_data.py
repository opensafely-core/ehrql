from pathlib import Path

import pytest

from databuilder import categorise, codelist, table
from databuilder.dsl import categorise as new_dsl_categorise
from databuilder.validate_dummy_data import (
    SUPPORTED_FILE_FORMATS,
    DummyDataValidationError,
    validate_dummy_data,
)

from .lib.csv_utils import write_rows_to_csv
from .lib.frames import events

cl = codelist(["12345"], system="snomed")

fixtures_path = Path(__file__).parent / "fixtures" / "dummy_data"


class Cohort:
    population = table("practice_registations").exists()
    sex = table("patients").latest().get("sex")
    _code = table("clinical_events").filter("code", is_in=cl)
    has_event = _code.exists()
    event_date = _code.latest().get("date")
    event_count = _code.count("code")


@pytest.mark.parametrize("file_format", SUPPORTED_FILE_FORMATS)
def test_validate_dummy_data_valid(file_format, tmpdir):
    rows = zip(
        ["patient_id", "11", "22"],
        ["sex", "F", "M"],
        ["has_event", True, False],
        ["event_date", "2021-01-01", None],
        ["event_count", 1, None],
    )
    dummy_data_file = Path(tmpdir) / f"dummy-data.{file_format}"
    write_rows_to_csv(rows, dummy_data_file)
    validate_dummy_data(Cohort, dummy_data_file, Path(f"output.{file_format}"))


@pytest.mark.parametrize(
    "filename,error_fragment",
    [
        ("missing-column", "Missing columns in dummy data: event_date"),
        ("extra-column", "Unexpected columns in dummy data: extra_col"),
        ("invalid-bool", "Invalid value `'X'` for has_event"),
        ("invalid-date", "Invalid value `'2021-021-021'` for event_date"),
        ("invalid-patient-id", "Invalid value `'Eleven'` for patient_id"),
        ("zero-date", "Invalid value `'0'` for event_date in row 4"),
    ],
)
def test_validate_dummy_data_invalid_csv(filename, error_fragment):
    with pytest.raises(DummyDataValidationError, match=error_fragment):
        validate_dummy_data(
            Cohort, fixtures_path / f"{filename}.csv", Path("output.csv")
        )


def test_validate_dummy_data_unknown_file_extension():
    with pytest.raises(
        DummyDataValidationError,
        match="Expected dummy data file with extension .csv; got dummy-data.txt",
    ):
        validate_dummy_data(
            Cohort, fixtures_path / "dummy-data.txt", Path("output.csv")
        )


@pytest.mark.parametrize("file_format", SUPPORTED_FILE_FORMATS)
def test_validate_dummy_data_missing_data_file(file_format):
    with pytest.raises(
        DummyDataValidationError,
        match=f"Dummy data file not found: .+missing.{file_format}",
    ):
        validate_dummy_data(
            Cohort,
            fixtures_path / f"missing.{file_format}",
            Path(f"output.{file_format}"),
        )


@pytest.mark.parametrize(
    "default_value,first_invalid_value",
    [
        (999, "foo"),  # valid dummy data value
        (None, "foo"),
        ("missing", "missing"),  # invalid dummy data value
    ],
)
def test_validate_dummy_data_with_categories(
    tmpdir, default_value, first_invalid_value
):
    class CohortWithCategories:
        population = table("practice_registations").exists()
        _code = table("clinical_events").filter("code", is_in=cl)
        event_date = _code.latest().get("date")
        _categories = {
            1: event_date == "2021-01-01",
        }
        category = categorise(_categories, default=default_value)

    rows = zip(
        ["patient_id", "11", "22", "33", "44"],
        ["event_date", "2021-01-01", "2021-01-01", "2021-01-01", "2021-01-01"],
        ["category", None, 1, default_value, "foo"],
    )

    dummy_data_file = Path(tmpdir) / "dummy-data.csv"
    write_rows_to_csv(rows, dummy_data_file)
    with pytest.raises(
        DummyDataValidationError,
        match=f"Invalid value `'{first_invalid_value}'` for category",
    ):
        validate_dummy_data(CohortWithCategories, dummy_data_file, Path("output.csv"))


def test_valid_dummy_data_with_categories_dsl(tmpdir, cohort_with_population):
    data_definition = cohort_with_population
    event_date = (
        events.sort_by(events.date).last_for_patient().select_column(events.date)
    )
    categories = {1: event_date == "2021-01-01"}
    data_definition.event_date = event_date
    data_definition.category = new_dsl_categorise(categories, default=-9)

    rows = zip(
        ["patient_id", "11", "22", "33"],
        ["event_date", "2021-01-01", "2021-01-01", "2021-01-01"],
        ["category", None, 1, -9],
    )

    dummy_data_file = Path(tmpdir) / "dummy-data.csv"
    write_rows_to_csv(rows, dummy_data_file)
    assert (
        validate_dummy_data(data_definition, dummy_data_file, Path("output.csv"))
        is None
    )


def test_validate_categories_values_must_be_valid_category(
    tmpdir, cohort_with_population
):
    data_definition = cohort_with_population
    event_date = (
        events.sort_by(events.date).last_for_patient().select_column(events.date)
    )
    categories = {"has event": event_date == "2021-01-01"}
    data_definition.event_date = event_date
    data_definition.category = new_dsl_categorise(categories, default="missing")

    rows = zip(
        ["patient_id", "11", "22", "33", "44"],
        ["event_date", "2021-01-01", "2021-01-01", None, None],
        ["category", None, "has event", "missing", "no event"],
    )

    dummy_data_file = Path(tmpdir) / "dummy-data.csv"
    write_rows_to_csv(rows, dummy_data_file)

    # All category values are valid type; only defined categories or the default are allowed
    with pytest.raises(
        DummyDataValidationError,
        match="Invalid value `'no event'` for category",
    ):
        validate_dummy_data(data_definition, dummy_data_file, Path("output.csv"))
