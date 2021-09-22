import pytest
from end_to_end.utils import assert_results_equivalent


@pytest.mark.smoke
def test_generate_measures_smoke_test(
    load_measures_study, cohort_extractor_generate_measures_in_container
):
    run_test(load_measures_study, cohort_extractor_generate_measures_in_container)


def test_generate_measures_integration_test(
    load_measures_study, cohort_extractor_generate_measures_in_process
):
    run_test(load_measures_study, cohort_extractor_generate_measures_in_process)


def run_test(load_measures_study, cohort_extractor):
    study = load_measures_study("end_to_end_tests_measures")
    actual_results = cohort_extractor(study)
    actual_results_file = list(actual_results.parent.glob(actual_results.name))[0]
    # measures results file is named with the Measure id
    assert actual_results_file.name == "measures_event_rate.csv"
    assert_results_equivalent(actual_results_file, study.expected_results())
