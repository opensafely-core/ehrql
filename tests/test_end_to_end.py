import csv
import shutil
from pathlib import Path

import pytest
from lib.tpp_schema import Events, Patient, RegistrationHistory

from cohortextractor.main import main


class Study:
    def __init__(self, study_path):
        self._path = Path(__file__).parent.absolute() / "fixtures" / study_path

    def definition(self):
        return self._path / "my_cohort.py"

    def code(self):
        return self._path.glob("*.py")

    def expected_results(self):
        return self._path / "results.csv"


@pytest.fixture
def load_study():
    return Study


@pytest.fixture
def cohort_extractor_in_container(tmpdir, database, containers):
    workspace = Path(tmpdir.mkdir("workspace"))
    analysis_dir = workspace / "analysis"
    analysis_dir.mkdir()
    output_rel_path = Path("outputs") / "cohort.csv"
    output_host_path = workspace / output_rel_path

    def run(study):
        for file in study.code():
            shutil.copy(file, analysis_dir)
        definition_path = Path("analysis") / study.definition().name

        containers.run_fg(
            image="cohort-extractor-v2:latest",
            command=[
                "--cohort-definition",
                str(definition_path),
                "--output",
                str(output_rel_path),
            ],
            environment={
                "TPP_DATABASE_URL": database.container_url(),
                "BACKEND": "tpp",
            },
            volumes={workspace: {"bind": "/workspace", "mode": "rw"}},
            network=database.network,
        )

        return output_host_path

    return run


@pytest.fixture
def cohort_extractor_in_process(tmpdir, database, containers):
    workspace = Path(tmpdir.mkdir("workspace"))
    analysis_dir = workspace / "analysis"
    analysis_dir.mkdir()
    output_rel_path = Path("outputs") / "cohort.csv"
    output_host_path = workspace / output_rel_path

    def run(study):
        for file in study.code():
            shutil.copy(file, analysis_dir)
        definition_path = analysis_dir / study.definition().name

        main(
            definition_path=definition_path,
            output_file=output_host_path,
            backend_id="tpp",
            db_url=database.host_url(),
        )

        return output_host_path

    return run


def assert_results_equivalent(actual_results, expected_results):
    with open(actual_results) as actual_file:
        with open(expected_results) as expected_file:
            actual_data = list(csv.DictReader(actual_file))
            expected_data = list(csv.DictReader(expected_file))

        assert actual_data == expected_data


@pytest.mark.smoke
def test_extracts_data_from_sql_server_smoke_test(
    load_study, setup_tpp_database, cohort_extractor_in_container
):
    run_test(load_study, setup_tpp_database, cohort_extractor_in_container)


@pytest.mark.integration
def test_extracts_data_from_sql_server_integration_test(
    load_study, setup_tpp_database, cohort_extractor_in_process
):
    run_test(load_study, setup_tpp_database, cohort_extractor_in_process)


def run_test(load_study, setup_tpp_database, cohort_extractor):
    setup_tpp_database(
        Patient(Patient_ID=1),
        Events(Patient_ID=1, ConsultationDate="2021-01-01", CTV3Code="xyz"),
        RegistrationHistory(Patient_ID=1),
    )

    study = load_study("end_to_end_tests")
    actual_results = cohort_extractor(study)
    assert_results_equivalent(actual_results, study.expected_results())
