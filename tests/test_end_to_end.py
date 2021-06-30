import csv
import shutil

import pytest
from conftest import is_fast_mode


def container_cohort_extractor(study, database, containers, study_dir):
    shutil.copy(study, study_dir)

    containers.run_fg(
        image="cohort-extractor-v2:latest",
        environment={
            "TPP_DATABASE_URL": f"mssql://SA:{database.password}@{database.host_from_container}:{database.port_from_container}/test"
        },
        volumes={study_dir: {"bind": "/workspace", "mode": "rw"}},
        network=database.network,
    )

    return study_dir / "outputs"


def in_process_cohort_extractor(study, database, study_dir):
    shutil.copy(study, study_dir)
    from cohortextractor.main import main

    main(
        workspace=str(study_dir),
        db_url=f"mssql://SA:{database.password}@{database.host_from_host}:{database.port_from_host}/test",
    )
    return study_dir / "outputs"


@pytest.fixture
def run_cohort_extractor(tmpdir, database, containers):
    study_dir = tmpdir.mkdir("study")
    if is_fast_mode():
        return lambda study: in_process_cohort_extractor(study, database, study_dir)
    else:
        return lambda study: container_cohort_extractor(
            study, database, containers, study_dir
        )


def assert_results_equivalent(actual_results, expected_results):
    with open(actual_results / "cohort.csv") as actual_file:
        with open(expected_results) as expected_file:
            actual_data = list(csv.DictReader(actual_file))
            expected_data = list(csv.DictReader(expected_file))

        assert actual_data == expected_data


def test_extracts_data_from_sql_server(load_study, load_data, run_cohort_extractor):
    study = load_study("end_to_end_tests")
    load_data(study.tables())

    actual_results = run_cohort_extractor(study.study_definition())
    assert_results_equivalent(actual_results, study.expected_results())
