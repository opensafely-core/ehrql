from .utils import assert_results_equivalent


def test_generate_measures_container_test(
    load_measures_study, cohort_extractor_generate_measures_in_container
):
    study = load_measures_study(
        "end_to_end_tests_measures", definition_file="measures_cohort.py"
    )
    expected_results_names = ["measures_event_rate.csv"]
    run_test(
        study,
        cohort_extractor_generate_measures_in_container,
        1,
        expected_results_names,
    )


def test_generate_measures_integration_test(
    load_measures_study, cohort_extractor_generate_measures_in_process
):
    study = load_measures_study(
        "end_to_end_tests_measures", definition_file="measures_cohort.py"
    )
    expected_results_names = ["measures_event_rate.csv"]
    run_test(
        study,
        cohort_extractor_generate_measures_in_process,
        1,
        expected_results_names,
    )


def test_generate_measures_integration_test_no_measures_specified(
    load_measures_study, cohort_extractor_generate_measures_in_process
):
    study = load_measures_study(
        "end_to_end_tests_measures", definition_file="measures_not_specified_cohort.py"
    )
    # No measures specified in definition file; runs without error but produces no measures
    # output files
    expected_results_names = []
    run_test(
        study,
        cohort_extractor_generate_measures_in_process,
        0,
        expected_results_names,
    )


def test_generate_measures_with_index_date_range_test(
    load_measures_study, cohort_extractor_generate_measures_in_process
):
    study = load_measures_study(
        "end_to_end_tests_measures_with_index_date_range",
        definition_file="measures_date_range_cohort.py",
        input_pattern="cohort_*.csv",
    )
    expected_results_names = [
        "measures_event_rate.csv",
        "measures_event_rate_2021-01-01.csv",
        "measures_event_rate_2021-02-01.csv",
        "measures_event_rate_2021-03-01.csv",
    ]
    run_test(
        study, cohort_extractor_generate_measures_in_process, 4, expected_results_names
    )


def run_test(
    study, cohort_extractor, expected_number_of_results, expected_results_names
):
    actual_results = cohort_extractor(study)
    results_filenames = sorted(actual_results.parent.glob(actual_results.name))
    assert [
        results_file.name for results_file in results_filenames
    ] == expected_results_names
    assert_results_equivalent(
        actual_results,
        study.expected_results(),
        expected_number_of_results=expected_number_of_results,
        match_output_pattern=True,
    )
