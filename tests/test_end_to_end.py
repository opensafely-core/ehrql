import csv
import shutil

import pytest


@pytest.fixture
def cohort_extractor(tmpdir, database, containers):
    study_dir = tmpdir.mkdir("study")

    def run(study):
        shutil.copy(study, study_dir)

        containers.run_fg(
            image="cohort-extractor-v2:latest",
            environment={
                "TPP_DATABASE_URL": database.container_url(),
                "BACKEND": "mock",
            },
            volumes={study_dir: {"bind": "/workspace", "mode": "rw"}},
            network=database.network,
        )

        return study_dir / "outputs"

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

    actual_results = cohort_extractor(study.study_definition())
    assert_results_equivalent(actual_results, study.expected_results())
