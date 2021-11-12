from cohortextractor.main import validate_cohort


def test_validate_cohort(load_study, cohort_extractor_in_process_no_database):
    study = load_study("end_to_end_tests_databricks", definition_file="db_cohort.py")
    actual_results = cohort_extractor_in_process_no_database(
        study, backend="databricks", action=validate_cohort
    )
    # validate_cohort succeeds and outputs SQL
    with open(actual_results) as actual_file:
        actual_data = actual_file.readlines()
        assert actual_data[0].startswith("SELECT")
