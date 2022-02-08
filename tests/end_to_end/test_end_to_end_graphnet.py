from .utils import assert_results_equivalent


def test_dummy_data(load_study, cohort_extractor_in_process_no_database):
    study = load_study(
        "end_to_end_tests_graphnet",
        definition_file="cohort_graphnet.py",
    )
    actual_results = cohort_extractor_in_process_no_database(study, use_dummy_data=True)
    assert_results_equivalent(actual_results, study.expected_results())
