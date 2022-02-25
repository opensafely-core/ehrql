import csv
import subprocess

import pytest

from databuilder.__main__ import main


class Study:
    def __init__(self, tmp_path, monkeypatch):
        self._workspace = tmp_path
        self._monkeypatch = monkeypatch

    def setup_from_repo(self, repo, definition_path):
        repo_url = f"https://github.com/{repo}.git"
        subprocess.check_call(
            ["git", "clone", repo_url, "."],
            cwd=self._workspace,
        )
        self._definition_path = self._workspace / definition_path

    def setup_from_string(self, definition):
        self._definition_path = self._workspace / "dataset.py"
        self._definition_path.write_text(definition)

    def run(self, database, backend):
        dataset_path = self._workspace / "dataset.csv"

        self._monkeypatch.setenv("DATABASE_URL", database.host_url())
        self._monkeypatch.setenv("OPENSAFELY_BACKEND", backend)

        main(
            [
                "generate_dataset",
                "--dataset-definition",
                str(self._definition_path),
                "--dataset",
                str(dataset_path),
            ]
        )

        with open(dataset_path) as f:
            return list(csv.DictReader(f))


@pytest.fixture
def study(tmp_path, monkeypatch):
    return Study(tmp_path, monkeypatch)
