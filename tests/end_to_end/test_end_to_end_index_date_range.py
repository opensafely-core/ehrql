import pytest
from end_to_end.utils import assert_results_equivalent
from lib.tpp_schema import event, patient, registration
from lib.util import mark_xfail_in_playback_mode


@pytest.mark.smoke
def test_extracts_data_with_index_date_range_smoke_test(
    load_study, setup_backend_database, cohort_extractor_in_container
):
    study = load_study("end_to_end_index_date_range")
    run_index_date_range_test(
        study,
        setup_backend_database,
        cohort_extractor_in_container,
        "2021-01-01 to 2021-03-01 by month",
    )


@mark_xfail_in_playback_mode
@pytest.mark.integration
def test_extracts_data_with_index_date_range_integration_test(
    load_study, setup_backend_database, cohort_extractor_in_process
):
    study = load_study("end_to_end_index_date_range")
    run_index_date_range_test(
        study,
        setup_backend_database,
        cohort_extractor_in_process,
        "2021-01-01 to 2021-03-01 by month",
    )


def run_index_date_range_test(
    study, setup_backend_database, cohort_extractor, index_date_range
):
    setup_backend_database(
        *patient(
            1,
            "F",
            "1990-8-10",
            registration(
                start_date="2020-01-01", end_date="2026-06-26"
            ),  # registered at all index dates
            event(code="abc", date="2020-01-01"),  # covid diagnosis
        ),
        *patient(
            2,
            "F",
            "1980-6-15",
            registration(
                start_date="2021-01-14", end_date="2021-06-26"
            ),  # registered at index dates 2 & 3
            # registered at all index dates
            event(code="def", date="2020-02-01"),  # covid diagnosis
        ),
        *patient(
            3,
            "M",
            "1990-8-10",
            registration(
                start_date="2021-03-01", end_date="2026-06-26"
            ),  # registered at index date 3 only
            # registered at all index dates
            event(code="ghi", date="2020-03-01"),  # covid diagnosis
        ),
        *patient(
            4,
            "M",
            "2000-8-18",
            registration(
                start_date="2021-01-15", end_date="2021-02-20"
            ),  # registered at index date 2 only
            # registered at all index dates
            event(code="jkl", date="2020-04-01"),  # covid diagnosis
        ),
    )
    actual_results = cohort_extractor(
        study,
        backend="tpp",
        use_dummy_data=False,
        index_date_range=index_date_range,
    )
    assert_results_equivalent(actual_results, study.expected_results())


def test_dummy_data_with_index_date_range(
    load_study, cohort_extractor_in_process_no_database
):
    study = load_study("end_to_end_index_date_range", dummy_data_file="dummy_data*.csv")
    actual_results = cohort_extractor_in_process_no_database(
        study, use_dummy_data=True, index_date_range="2021-01-01 to 2021-03-01 by month"
    )
    assert_results_equivalent(actual_results, study.expected_results())


@pytest.mark.parametrize(
    "definition_file,index_date_range,error,error_message",
    [
        (None, "2021-01-01 to 2021-02-31 by month", ValueError, "Invalid date range"),
        (None, "2021-01-01 to 2021-02-20 by year", ValueError, "Unknown time period"),
        (None, "2021-01-01 to 2020-02-20 by week", ValueError, "Invalid date range"),
        (
            "cohort_no_base_index_date.py",
            "2021-01-01 to 2021-02-20 by month",
            RuntimeError,
            "index-date-range requires BASE_INDEX_DATE to be defined in study definition",
        ),
    ],
    ids=[
        "test invalid date",
        "test unknown by",
        "test to date before from date",
        "test no BASE_INDEX_DATE defined in cohort definition",
    ],
)
def test_index_date_range_errors(
    load_study,
    cohort_extractor_in_process_no_database,
    definition_file,
    index_date_range,
    error,
    error_message,
):
    study = load_study("end_to_end_index_date_range", definition_file=definition_file)

    with pytest.raises(error, match=error_message):
        return cohort_extractor_in_process_no_database(
            study,
            backend="tpp",
            use_dummy_data=False,
            index_date_range=index_date_range,
        )
