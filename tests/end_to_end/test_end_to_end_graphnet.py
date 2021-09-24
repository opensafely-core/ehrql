import pytest
from end_to_end.utils import assert_results_equivalent
from lib.graphnet_schema import Patients
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
        Patients(patient_id=1, date_of_birth="1980-01-01"),
        Patients(patient_id=2, date_of_birth="1948-02-02"),
        backend="graphnet",
    )
    study = load_study(
        "end_to_end_tests_graphnet",
        dummy_data_file=dummy_data_file,
        definition_file="cohort_graphnet.py",
    )
    actual_results = cohort_extractor(
        study, backend="graphnet", use_dummy_data=dummy_data_file is not None
    )
    assert_results_equivalent(actual_results, study.expected_results())
