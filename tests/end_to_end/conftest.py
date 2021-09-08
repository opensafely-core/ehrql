import shutil
from pathlib import Path

import pytest
from end_to_end.utils import Study

from cohortextractor.main import main


@pytest.fixture
def load_study():
    return Study


@pytest.fixture
def cohort_extractor_in_container(tmpdir, database, containers):
    workspace = Path(tmpdir.mkdir("workspace"))
    analysis_dir = workspace / "analysis"
    analysis_dir.mkdir()
    output_rel_path = Path("outputs") / "cohort.csv"
    output_host_path = workspace / output_rel_path

    def run(study, backend, use_dummy_data=False):
        for file in study.code():
            shutil.copy(file, analysis_dir)
        definition_path = Path("analysis") / study.definition().name

        command = [
            "--cohort-definition",
            str(definition_path),
            "--output",
            str(output_rel_path),
        ]
        if use_dummy_data:
            shutil.copy(study.dummy_data(), analysis_dir)
            dummy_data_file = Path("analysis") / study.dummy_data().name
            command += ["--dummy-data-file", str(dummy_data_file)]

        containers.run_fg(
            image="cohort-extractor-v2:latest",
            command=command,
            environment={
                "DATABASE_URL": database.container_url(),
                "OPENSAFELY_BACKEND": backend,
                "TEMP_DATABASE_NAME": "temp_tables",
            },
            volumes={workspace: {"bind": "/workspace", "mode": "rw"}},
            network=database.network,
        )

        return output_host_path

    return run


def _in_process_setup(tmpdir):
    workspace = Path(tmpdir.mkdir("workspace"))
    analysis_dir = workspace / "analysis"
    analysis_dir.mkdir()
    output_rel_path = Path("outputs") / "cohort.csv"
    output_host_path = workspace / output_rel_path
    return analysis_dir, output_host_path


def _in_process_run(
    study, analysis_dir, output_host_path, backend_id, db_url, use_dummy_data
):
    for file in study.code():
        shutil.copy(file, analysis_dir)
    definition_path = analysis_dir / study.definition().name

    if use_dummy_data:
        shutil.copy(study.dummy_data(), analysis_dir)
        dummy_data_file = analysis_dir / study.dummy_data().name
    else:
        dummy_data_file = None

    main(
        definition_path=definition_path,
        output_file=output_host_path,
        backend_id=backend_id,
        db_url=db_url,
        dummy_data_file=dummy_data_file,
        temporary_database="temp_tables",
    )


@pytest.fixture
def cohort_extractor_in_process(tmpdir, database, containers):
    analysis_dir, output_host_path = _in_process_setup(tmpdir)

    def run(study, backend, use_dummy_data=False):
        _in_process_run(
            study=study,
            analysis_dir=analysis_dir,
            output_host_path=output_host_path,
            backend_id=backend,
            db_url=database.host_url(),
            use_dummy_data=use_dummy_data,
        )

        return output_host_path

    return run


@pytest.fixture
def cohort_extractor_in_process_no_database(tmpdir, containers):
    analysis_dir, output_host_path = _in_process_setup(tmpdir)

    def run(study, backend=None, use_dummy_data=False):
        _in_process_run(
            study=study,
            analysis_dir=analysis_dir,
            output_host_path=output_host_path,
            backend_id=backend,
            db_url=None,
            use_dummy_data=use_dummy_data,
        )
        return output_host_path

    return run
