import pytest
from end_to_end.utils import assert_results_equivalent


@pytest.mark.smoke
def test_generate_measures_smoke_test(
    load_measures_study, cohort_extractor_generate_measures_in_container
):
    study = load_measures_study(
        "end_to_end_tests_measures", definition_file="measures_cohort.py"
    )
    expected_results_name = "measures_event_rate.csv"
    run_test(
        study,
        cohort_extractor_generate_measures_in_container,
        expected_results_name,
    )


@pytest.mark.integration
def test_generate_measures_integration_test(
    load_measures_study, cohort_extractor_generate_measures_in_process
):
    study = load_measures_study(
        "end_to_end_tests_measures", definition_file="measures_cohort.py"
    )
    expected_results_name = "measures_event_rate.csv"
    run_test(
        study,
        cohort_extractor_generate_measures_in_process,
        expected_results_name,
    )


@pytest.mark.integration
def test_generate_measures_with_index_date_range_test(
    load_measures_study, cohort_extractor_generate_measures_in_process
):
    study = load_measures_study(
        "end_to_end_tests_measures_with_index_date_range",
        definition_file="measures_date_range_cohort.py",
        input_pattern="cohort_*.csv",
    )
    expected_results_name = "measures_event_rate_2021-01-01.csv"
    run_test(
        study, cohort_extractor_generate_measures_in_process, expected_results_name
    )


def run_test(study, cohort_extractor, expected_results_name):
    actual_results = cohort_extractor(study)
    first_results_file = sorted(actual_results.parent.glob(actual_results.name))[0]
    assert first_results_file.name == expected_results_name
    assert_results_equivalent(
        actual_results, study.expected_results(), match_output_pattern=True
    )
