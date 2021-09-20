import pytest
from end_to_end.utils import assert_results_equivalent
from lib.tpp_schema import (
    Events,
    Patient,
    RegistrationHistory,
    event,
    patient,
    registration,
)
from lib.util import mark_xfail_in_playback_mode


@pytest.mark.smoke
def test_extracts_data_from_sql_server_smoke_test(
    load_study, setup_backend_database, cohort_extractor_in_container
):
    run_test(load_study, setup_backend_database, cohort_extractor_in_container)


@mark_xfail_in_playback_mode
@pytest.mark.integration
def test_extracts_data_from_sql_server_integration_test(
    load_study, setup_backend_database, cohort_extractor_in_process
):
    run_test(load_study, setup_backend_database, cohort_extractor_in_process)


def run_test(
    load_study, setup_backend_database, cohort_extractor, dummy_data_file=None
):
    setup_backend_database(
        Patient(Patient_ID=1),
        Events(Patient_ID=1, ConsultationDate="2021-01-01", CTV3Code="xyz"),
        RegistrationHistory(Patient_ID=1),
        Patient(Patient_ID=2),
        Events(Patient_ID=2, ConsultationDate="2021-02-02", CTV3Code="abc"),
        RegistrationHistory(Patient_ID=2),
    )
    study = load_study("end_to_end_tests_tpp", dummy_data_file)
    actual_results = cohort_extractor(
        study, backend="tpp", use_dummy_data=dummy_data_file is not None
    )
    assert_results_equivalent(actual_results, study.expected_results())


def test_dummy_data(load_study, cohort_extractor_in_process_no_database):
    study = load_study("end_to_end_tests_tpp")
    actual_results = cohort_extractor_in_process_no_database(study, use_dummy_data=True)
    assert_results_equivalent(actual_results, study.expected_results())


@mark_xfail_in_playback_mode
@pytest.mark.integration
def test_extracts_data_from_sql_server_ignores_dummy_data_file(
    load_study, setup_backend_database, cohort_extractor_in_process
):
    # A dummy data file is ignored if running in a real backend (i.e. DATABASE_URL is set)
    # This provides an invalid dummy data file, but it is ignored so no errors are raised
    run_test(
        load_study,
        setup_backend_database,
        cohort_extractor_in_process,
        "invalid_dummy_data.csv",
    )


@pytest.mark.smoke
def test_extracts_data_with_index_date_range_smoke_test(
    load_study, setup_backend_database, cohort_extractor_in_container
):
    run_index_date_range_test(
        load_study, setup_backend_database, cohort_extractor_in_container
    )


@mark_xfail_in_playback_mode
@pytest.mark.integration
def test_extracts_data_with_index_date_range_integration_test(
    load_study, setup_backend_database, cohort_extractor_in_process
):
    run_index_date_range_test(
        load_study, setup_backend_database, cohort_extractor_in_process
    )


def run_index_date_range_test(
    load_study, setup_backend_database, cohort_extractor, dummy_data_file=None
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
    study = load_study("end_to_end_index_date_range_tpp", dummy_data_file)
    actual_results = cohort_extractor(
        study,
        backend="tpp",
        use_dummy_data=dummy_data_file is not None,
        index_date_range="2021-01-01 to 2021-03-01 by month",
    )
    assert_results_equivalent(actual_results, study.expected_results())


def test_dummy_data_with_index_date_range(
    load_study, cohort_extractor_in_process_no_database
):
    study = load_study(
        "end_to_end_index_date_range_tpp", dummy_data_file="dummy_data*.csv"
    )
    actual_results = cohort_extractor_in_process_no_database(
        study, use_dummy_data=True, index_date_range="2021-01-01 to 2021-03-01 by month"
    )
    assert_results_equivalent(actual_results, study.expected_results())
