import pytest

from databuilder.main import validate_cohort

from ..lib.tpp_schema import CTV3Events, Patient, RegistrationHistory
from .utils import assert_results_equivalent


@pytest.mark.integration
def test_extracts_data_from_sql_server_container_test(
    load_study, database, cohort_extractor_in_container
):
    run_test(load_study, database, cohort_extractor_in_container)


@pytest.mark.integration
def test_extracts_data_from_sql_server_integration_test(
    load_study, database, cohort_extractor_in_process
):
    run_test(load_study, database, cohort_extractor_in_process)


@pytest.mark.integration
def test_extracts_data_from_sql_server_integration_test_new_dsl(
    load_study, database, cohort_extractor_in_process
):
    run_test(
        load_study,
        database,
        cohort_extractor_in_process,
        definition_file="tpp_cohort_new_dsl.py",
    )


def run_test(
    load_study,
    database,
    cohort_extractor,
    definition_file=None,
    dummy_data_file=None,
):
    definition_file = definition_file or "tpp_cohort.py"
    database.setup(
        Patient(Patient_ID=1),
        CTV3Events(Patient_ID=1, ConsultationDate="2021-01-01", CTV3Code="xyz"),
        RegistrationHistory(Patient_ID=1),
        Patient(Patient_ID=2),
        CTV3Events(Patient_ID=2, ConsultationDate="2021-02-02", CTV3Code="abc"),
        RegistrationHistory(Patient_ID=2),
    )
    study = load_study(
        "end_to_end_tests_tpp",
        definition_file=definition_file,
        dummy_data_file=dummy_data_file,
    )
    actual_results = cohort_extractor(
        study, backend="tpp", use_dummy_data=dummy_data_file is not None
    )
    assert_results_equivalent(actual_results, study.expected_results())


def test_dummy_data(load_study, cohort_extractor_in_process_no_database):
    study = load_study("end_to_end_tests_tpp", definition_file="tpp_cohort.py")
    actual_results = cohort_extractor_in_process_no_database(study, use_dummy_data=True)
    assert_results_equivalent(actual_results, study.expected_results())


@pytest.mark.integration
def test_dummy_data_container_test(load_study, cohort_extractor_in_container):
    study = load_study("end_to_end_tests_tpp", definition_file="tpp_cohort.py")
    actual_results = cohort_extractor_in_container(
        study, backend="tpp", use_dummy_data=True
    )
    assert_results_equivalent(actual_results, study.expected_results())


def test_validate_cohort(load_study, cohort_extractor_in_process_no_database):
    study = load_study("end_to_end_tests_tpp", definition_file="tpp_cohort.py")
    actual_results = cohort_extractor_in_process_no_database(
        study, backend="tpp", action=validate_cohort
    )
    # validate_cohort succeeds and outputs SQL
    with open(actual_results) as actual_file:
        actual_data = actual_file.readlines()
        assert actual_data[0].startswith("SELECT * INTO")


@pytest.mark.integration
def test_extracts_data_from_sql_server_ignores_dummy_data_file(
    load_study, database, cohort_extractor_in_process
):
    # A dummy data file is ignored if running in a real backend (i.e. DATABASE_URL is set)
    # This provides an invalid dummy data file, but it is ignored so no errors are raised
    run_test(
        load_study,
        database,
        cohort_extractor_in_process,
        dummy_data_file="invalid_dummy_data.csv",
    )
