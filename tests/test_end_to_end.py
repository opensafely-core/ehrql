import csv
import shutil
from pathlib import Path

import pytest
from lib.tpp_schema import Events, Patient, RegistrationHistory

from cohortextractor.main import main


class Study:
    def __init__(self, study_path, dummy_data_file=None):
        self._path = Path(__file__).parent.absolute() / "fixtures" / study_path
        self.dummy_data_file = dummy_data_file or "dummy_data.csv"

    def definition(self):
        return self._path / "my_cohort.py"

    def code(self):
        return self._path.glob("*.py")

    def expected_results(self):
        return self._path / "results.csv"

    def dummy_data(self):
        return self._path / self.dummy_data_file


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

    def run(study, use_dummy_data=False):
        for file in study.code():
            shutil.copy(file, analysis_dir)
        definition_path = Path("analysis") / study.definition().name

        command = [
            "--cohort-definition",
            str(definition_path),
            "--output",
            str(output_rel_path),
        ]
        if use_dummy_data:
            shutil.copy(study.dummy_data(), analysis_dir)
            dummy_data_file = Path("analysis") / study.dummy_data().name
            command += ["--dummy-data-file", str(dummy_data_file)]

        containers.run_fg(
            image="cohort-extractor-v2:latest",
            command=command,
            environment={
                "DATABASE_URL": database.container_url(),
                "BACKEND": "tpp",
            },
            volumes={workspace: {"bind": "/workspace", "mode": "rw"}},
            network=database.network,
        )

        return output_host_path

    return run


def _in_process_setup(tmpdir):
    workspace = Path(tmpdir.mkdir("workspace"))
    analysis_dir = workspace / "analysis"
    analysis_dir.mkdir()
    output_rel_path = Path("outputs") / "cohort.csv"
    output_host_path = workspace / output_rel_path
    return analysis_dir, output_host_path


def _in_process_run(
    study, analysis_dir, output_host_path, backend_id, db_url, use_dummy_data
):
    for file in study.code():
        shutil.copy(file, analysis_dir)
    definition_path = analysis_dir / study.definition().name
    if use_dummy_data:
        shutil.copy(study.dummy_data(), analysis_dir)
        dummy_data_file = analysis_dir / study.dummy_data().name
    else:
        dummy_data_file = None

    main(
        definition_path=definition_path,
        output_file=output_host_path,
        backend_id=backend_id,
        db_url=db_url,
        dummy_data_file=dummy_data_file,
    )


@pytest.fixture
def cohort_extractor_in_process(tmpdir, database, containers):
    analysis_dir, output_host_path = _in_process_setup(tmpdir)

    def run(study, use_dummy_data=False):

        _in_process_run(
            study=study,
            analysis_dir=analysis_dir,
            output_host_path=output_host_path,
            backend_id="tpp",
            db_url=database.host_url(),
            use_dummy_data=use_dummy_data,
        )

        return output_host_path

    return run


@pytest.fixture
def cohort_extractor_in_process_no_database(tmpdir, containers):
    analysis_dir, output_host_path = _in_process_setup(tmpdir)

    def run(study, use_dummy_data=False):
        _in_process_run(
            study=study,
            analysis_dir=analysis_dir,
            output_host_path=output_host_path,
            backend_id=None,
            db_url=None,
            use_dummy_data=use_dummy_data,
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


def run_test(load_study, setup_tpp_database, cohort_extractor, dummy_data_file=None):
    setup_tpp_database(
        Patient(Patient_ID=1),
        Events(Patient_ID=1, ConsultationDate="2021-01-01", CTV3Code="xyz"),
        RegistrationHistory(Patient_ID=1),
    )

    study = load_study("end_to_end_tests", dummy_data_file)
    actual_results = cohort_extractor(study, use_dummy_data=dummy_data_file is not None)
    assert_results_equivalent(actual_results, study.expected_results())


def test_dummy_data(load_study, cohort_extractor_in_process_no_database):
    study = load_study("end_to_end_tests")
    actual_results = cohort_extractor_in_process_no_database(study, use_dummy_data=True)
    assert_results_equivalent(actual_results, study.expected_results())


@pytest.mark.integration
def test_extracts_data_from_sql_server_ignores_dummy_data_file(
    load_study, setup_tpp_database, cohort_extractor_in_process
):
    # A dummy data file is ignored if running in a real backend (i.e. DATABASE_URL is set)
    # THis provides an invalid dummy data file, but it is ignored so no errors are raised
    run_test(
        load_study,
        setup_tpp_database,
        cohort_extractor_in_process,
        "invalid_dummy_data.csv",
    )
