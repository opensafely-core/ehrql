import csv
import shutil
from datetime import datetime
from pathlib import Path

from tests.lib.tpp_schema import patient


def test_generate_dataset_in_container(tmpdir, database, containers):
    database.setup(patient(dob=datetime(1943, 5, 5)))

    # create some relative paths
    analysis_dir = Path("analysis")
    definition = Path("dataset_definition.py")
    outputs_dir = Path("outputs")
    dataset = Path("dataset.csv")

    # create the local workspace directory
    workspace = Path(tmpdir.mkdir("workspace"))

    # create the local analysis dir and copy in our definition
    (workspace / analysis_dir).mkdir()
    shutil.copy(Path(__file__).parent / definition, workspace / analysis_dir)

    # create the local outputs dir
    (workspace / outputs_dir).mkdir()

    command = [
        "generate_dataset",
        "--dataset-definition",
        str(Path("/workspace") / analysis_dir / definition),
        "--dataset",
        str(Path("/workspace") / outputs_dir / dataset),
    ]

    containers.run_fg(
        image="databuilder:latest",
        command=command,
        environment={
            "DATABASE_URL": database.container_url(),
            "OPENSAFELY_BACKEND": "tpp",
        },
        volumes={workspace: {"bind": "/workspace", "mode": "rw"}},
    )

    with open(workspace / outputs_dir / dataset) as f:
        results = list(csv.DictReader(f))
        assert len(results) == 1
        assert results[0]["year"] == "1943"


def test_validate_dataset_definition_in_container(run_in_container):
    output = run_in_container(
        [
            "validate_dataset_definition",
            "--help",
        ]
    )

    assert output


def test_generate_measures_in_container(run_in_container):
    output = run_in_container(
        [
            "generate_measures",
            "--help",
        ]
    )

    assert output


def test_test_connection_in_container(run_in_container):
    output = run_in_container(
        [
            "test_connection",
            "--help",
        ]
    )

    assert output


def test_generate_docs_in_container(run_in_container):
    output = run_in_container(
        [
            "generate_docs",
            "--help",
        ]
    )

    assert output
