from pathlib import Path

import docker
import pytest


class Study:
    def __init__(self, study_path):
        super().__init__()
        self._path = Path(__file__).parent.absolute() / "fixtures" / study_path

    def grab_tables(self):
        return self._path / "tables.sql"

    def grab_study_definition(self):
        return self._path / "study_definition.py"

    def grab_expected_results(self):
        return self._path / "results.csv"


@pytest.fixture
def study():
    def read_dir(path):
        return Study(path)

    return read_dir


def pytest_sessionfinish(session, exitstatus):
    # TODO: clean up after ourselves more carefully
    client = docker.from_env()
    client.containers.get("mssql").remove(force=True)
