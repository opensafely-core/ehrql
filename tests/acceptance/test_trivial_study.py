import csv
from datetime import datetime
from pathlib import Path

from databuilder.__main__ import main
from tests.lib.tpp_schema import patient

dataset_definition = """
from databuilder.query_language import Dataset
from databuilder.tables import patients
from databuilder.definition import register

dataset = Dataset()
year = patients.date_of_birth.year
dataset.set_population(year >= 1900)
dataset.year = year
register(dataset)
"""


def test_generate_dataset(database, tmpdir, monkeypatch):
    database.setup(patient(dob=datetime(1943, 5, 5)))

    workspace = Path(tmpdir.mkdir("workspace"))
    definition_path = workspace / "dataset.py"
    definition_path.write_text(dataset_definition)
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
        assert results[0]["year"] == "1943"
