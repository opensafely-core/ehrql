import csv
import subprocess
from datetime import datetime
from pathlib import Path

from databuilder.__main__ import main
from tests.lib.tpp_schema import patient


def test_generate_dataset(database, tmpdir, monkeypatch):
    database.setup(
        patient(dob=datetime(1910, 5, 5)),
        patient(dob=datetime(2010, 5, 5)),
    )

    workspace = Path(tmpdir.mkdir("workspace"))

    subprocess.check_call(
        [
            "git",
            "clone",
            "https://github.com/opensafely/test-age-distribution.git",
            ".",
        ],
        cwd=workspace,
    )

    definition_path = workspace / "analysis" / "dataset_definition.py"
    dataset_path = workspace / "dataset.csv"

    monkeypatch.setenv("DATABASE_URL", database.host_url())
    monkeypatch.setenv("OPENSAFELY_BACKEND", "tpp")

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
        results = list(csv.DictReader(f))
        assert len(results) == 1
        assert results[0]["year_of_birth"] == "2010"
