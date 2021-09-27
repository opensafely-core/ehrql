import pytest
from end_to_end.utils import assert_results_equivalent
from lib.tpp_schema import event, patient, registration
from lib.util import mark_xfail_in_playback_mode


@pytest.mark.smoke
def test_extracts_data_with_index_date_range_smoke_test(
    load_study, setup_backend_database, cohort_extractor_in_container
):
    study = load_study("end_to_end_index_date_range", output_file_name="cohort_*.csv")
    run_index_date_range_test(
        study,
        setup_backend_database,
        cohort_extractor_in_container,
        expected_number_of_results=3,
    )


@mark_xfail_in_playback_mode
@pytest.mark.integration
def test_extracts_data_with_index_date_range_integration_test(
    load_study,
    setup_backend_database,
    cohort_extractor_in_process,
):
    study = load_study(
        "end_to_end_index_date_range",
        output_file_name="cohort_*.csv",
    )
    run_index_date_range_test(
        study,
        setup_backend_database,
        cohort_extractor_in_process,
        expected_number_of_results=3,
    )


@mark_xfail_in_playback_mode
@pytest.mark.integration
@pytest.mark.parametrize(
    "definition_file,output_file,error",
    [
        (
            "cohort_no_valid_class_or_function.py",
            "cohort_*.csv",
            "A study definition must contain one and only one 'cohort' function or 'Cohort' class",
        ),
        (
            "cohort_invalid_function_args.py",
            "cohort_*.csv",
            "A study definition with index_date_range must pass a single index_date argument to the 'cohort' function",
        ),
        (
            "my_cohort.py",
            "cohort.csv",
            "No output pattern found in output file",
        ),
    ],
)
def test_index_date_range_cohort_definition_errors(
    load_study,
    cohort_extractor_in_process_no_database,
    definition_file,
    output_file,
    error,
):
    study = load_study(
        "end_to_end_index_date_range",
        definition_file=definition_file,
        output_file_name=output_file,
    )
    with pytest.raises(ValueError, match=error):
        cohort_extractor_in_process_no_database(
            study,
            backend="tpp",
            use_dummy_data=False,
        )


def run_index_date_range_test(
    study,
    setup_backend_database,
    cohort_extractor,
    expected_number_of_results,
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
            ),  # registered at index dates 2021-01-15, 21, 28, 31, 2021-02-01, 28, 2021-03-01
            event(code="def", date="2020-02-01"),  # covid diagnosis
        ),
        *patient(
            3,
            "M",
            "1990-8-10",
            registration(
                start_date="2021-03-01", end_date="2026-06-26"
            ),  # registered at index date 2021-03-01 only
            event(code="ghi", date="2020-03-01"),  # covid diagnosis
        ),
        *patient(
            4,
            "M",
            "2000-8-18",
            registration(
                start_date="2021-01-15", end_date="2021-02-20"
            ),  # registered at all index dates 2021-01-15, 21, 28, 31, 2021-02-01
            event(code="jkl", date="2020-04-01"),  # covid diagnosis
        ),
    )
    actual_results = cohort_extractor(
        study,
        backend="tpp",
        use_dummy_data=False,
    )
    assert_results_equivalent(
        actual_results,
        study.expected_results(),
        expected_number_of_results,
        match_output_pattern=True,
    )


def test_dummy_data_with_index_date_range(
    load_study, cohort_extractor_in_process_no_database
):
    study = load_study(
        "end_to_end_index_date_range",
        dummy_data_file="dummy_data_*.csv",
        output_file_name="cohort_*.csv",
    )
    actual_results = cohort_extractor_in_process_no_database(study, use_dummy_data=True)
    assert_results_equivalent(
        actual_results,
        study.expected_results(),
        expected_number_of_results=3,
        match_output_pattern=True,
    )
