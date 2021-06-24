import csv
import shutil
from pathlib import Path

import docker

client = docker.from_env()


def run_cohort_extractor(study, tmpdir):
    study_dir = tmpdir.mkdir("study")
    shutil.copy(study, study_dir)

    client.containers.run("cohort-extractor-v2:latest", remove=True, links={"mssql": "mssql"},
                          environment={"TPP_DATABASE_URL": 'mssql://SA:Your_password123!@mssql/Test_OpenCorona'},
                          volumes={study_dir: {'bind': '/workspace', 'mode': 'rw'}})

    return study_dir / "outputs"


def start_sql_server(tables, tmpdir):
    mssql_dir = tmpdir.mkdir("mssql")
    shutil.copy(tables, mssql_dir)
    shutil.copy(Path(__file__).parent.absolute() / "support/mssql/entrypoint.sh", mssql_dir)

    client.containers.run("mcr.microsoft.com/mssql/server:2017-latest", remove=True, name="mssql",
                          volumes={mssql_dir: {'bind': '/mssql', 'mode': 'ro'}},
                          environment={"SA_PASSWORD": "Your_password123!", "ACCEPT_EULA": "Y"},
                          entrypoint="/mssql/entrypoint.sh",
                          command="/opt/mssql/bin/sqlservr",
                          detach=True)


def assert_results_equivalent(actual_results, expected_results):
    with open(actual_results / "some_file.csv") as actual_file, open(expected_results) as expected_file:
        actual_data = list(csv.DictReader(actual_file))
        expected_data = list(csv.DictReader(expected_file))

        assert actual_data == expected_data


def test_extracts_data_from_sql_server(study, tmpdir):
    our_study = study("end_to_end_tests")

    tables = our_study.grab_tables()
    start_sql_server(tables, tmpdir)

    study = our_study.grab_study_definition()

    actual_results = run_cohort_extractor(study, tmpdir)

    expected_results = our_study.grab_expected_results()

    assert_results_equivalent(actual_results, expected_results)
