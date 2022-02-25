import csv
import subprocess
from pathlib import Path

import pytest

from databuilder.__main__ import main


class Study:
    def __init__(self, tmpdir, monkeypatch):
        self.tmpdir = tmpdir
        self.monkeypatch = monkeypatch

    def setup(self, repo):
        self.workspace = Path(self.tmpdir.mkdir("workspace"))

        repo_url = f"https://github.com/{repo}.git"
        subprocess.check_call(
            ["git", "clone", repo_url, "."],
            cwd=self.workspace,
        )

    def run(self, definition_path, database, backend):
        definition_path = self.workspace / definition_path
        dataset_path = self.workspace / "dataset.csv"

        self.monkeypatch.setenv("DATABASE_URL", database.host_url())
        self.monkeypatch.setenv("OPENSAFELY_BACKEND", backend)

        main(
            [
                "generate_dataset",
                "--dataset-definition",
                str(definition_path),
                "--dataset",
                str(dataset_path),
            ]
        )

        with open(dataset_path) as f:
            return list(csv.DictReader(f))


@pytest.fixture
def study(tmpdir, monkeypatch):
    return Study(tmpdir, monkeypatch)
