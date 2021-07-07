import csv
import shutil
from pathlib import Path

import pytest

from cohortextractor.main import main


class Study:
    def __init__(self, study_path):
        self._path = Path(__file__).parent.absolute() / "fixtures" / study_path

    def tables(self):
        return self._path / "tables.sql"

    def definition(self):
        return self._path / "my_cohort.py"

    def expected_results(self):
        return self._path / "results.csv"


@pytest.fixture
def load_study():
    return Study


@pytest.fixture
def cohort_extractor(tmpdir, database, containers):
    workspace = tmpdir.mkdir("workspace")
    analysis_dir = workspace / "analysis"
    analysis_dir.mkdir()

    def run(study):
        shutil.copy(study.definition(), analysis_dir)
        definition_path = Path("analysis") / study.definition().name

        containers.run_fg(
            image="cohort-extractor-v2:latest",
            command=["--cohort-definition", str(definition_path)],
            environment={
                "TPP_DATABASE_URL": database.container_url(),
                "BACKEND": "mock",
            },
            volumes={workspace: {"bind": "/workspace", "mode": "rw"}},
            network=database.network,
        )

        return workspace / "outputs"

    return run


def assert_results_equivalent(actual_results, expected_results):
    with open(actual_results / "cohort.csv") as actual_file:
        with open(expected_results) as expected_file:
            actual_data = list(csv.DictReader(actual_file))
            expected_data = list(csv.DictReader(expected_file))

        assert actual_data == expected_data


@pytest.mark.smoke
def test_extracts_data_from_sql_server(load_study, load_data, cohort_extractor):
    study = load_study("end_to_end_tests")
    load_data(study.tables())

    actual_results = cohort_extractor(study)
    assert_results_equivalent(actual_results, study.expected_results())


@pytest.mark.integration
def test_main(load_study, load_data, database):
    study = load_study("end_to_end_tests")
    load_data(study.tables())
    main(workspace=str(study.path), backend_id="mock", db_url=database.host_url())
    output_file_path = study.path / "outputs" / "cohort.csv"
    assert output_file_path.read_text() == study.expected_results().read_text()
