import shutil
from pathlib import Path

import pytest
from end_to_end.utils import MeasuresStudy, Study

from cohortextractor.main import generate_cohort, generate_measures, run_cohort_action


@pytest.fixture
def load_study():
    return Study


@pytest.fixture
def load_measures_study():
    return MeasuresStudy


def _in_container_setup(tmpdir):
    workspace = Path(tmpdir.mkdir("workspace"))
    analysis_dir = workspace / "analysis"
    analysis_dir.mkdir()
    return workspace, analysis_dir


@pytest.fixture
def cohort_extractor_in_container(tmpdir, database, containers):
    workspace, analysis_dir = _in_container_setup(tmpdir)
    output_rel_dir = Path("outputs")
    output_host_dir = workspace / output_rel_dir

    def run(study, backend, use_dummy_data=False):
        for file in study.code():
            shutil.copy(file, analysis_dir)
        definition_path = Path("analysis") / study.definition().name

        command = [
            "generate_cohort",
            "--cohort-definition",
            str(definition_path),
            "--output",
            str(output_rel_dir / study.output_file_name),
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
        )
        return output_host_dir / study.output_file_name

    return run


@pytest.fixture
def cohort_extractor_generate_measures_in_container(tmpdir, database, containers):
    workspace, analysis_dir = _in_container_setup(tmpdir)
    output_rel_path = Path("outputs") / "measures_*.csv"
    output_host_path = workspace / output_rel_path
    input_dir = workspace / "inputs"
    input_dir.mkdir()

    def run(study):
        for file in study.code():
            shutil.copy(file, analysis_dir)
        for file in study.input_files():
            shutil.copy(file, input_dir)
        input_path = Path("inputs") / study.input_pattern
        definition_path = Path("analysis") / study.definition().name

        command = [
            "generate_measures",
            "--cohort-definition",
            str(definition_path),
            "--input",
            str(input_path),
            "--output",
            str(output_rel_path),
        ]

        containers.run_fg(
            image="cohort-extractor-v2:latest",
            command=command,
            volumes={workspace: {"bind": "/workspace", "mode": "rw"}},
        )

        return output_host_path

    return run


def _in_process_setup(tmpdir):
    workspace = Path(tmpdir.mkdir("workspace"))
    analysis_dir = workspace / "analysis"
    analysis_dir.mkdir()
    output_rel_dir = Path("outputs")
    output_host_dir = workspace / output_rel_dir
    return workspace, analysis_dir, output_host_dir


def _in_process_run(
    study,
    analysis_dir,
    output_host_path,
    backend_id,
    db_url,
    use_dummy_data,
    action=generate_cohort,
):
    for file in study.code():
        shutil.copy(file, analysis_dir)
    definition_path = analysis_dir / study.definition().name

    if use_dummy_data:
        # If we have an index date range, the dummy date file input should be a pattern
        dummy_data_files = study.dummy_data().parent.glob(study.dummy_data().name)
        for dummy_file in dummy_data_files:
            shutil.copy(dummy_file, analysis_dir)
        dummy_data_file = analysis_dir / study.dummy_data().name
    else:
        dummy_data_file = None

    action_kwargs = dict(
        output_file=output_host_path,
        definition_path=definition_path,
        backend_id=backend_id,
    )
    if action == generate_cohort:
        action_kwargs.update(
            db_url=db_url,
            dummy_data_file=dummy_data_file,
            temporary_database="temp_tables",
        )
    run_cohort_action(action, **action_kwargs)


@pytest.fixture
def cohort_extractor_in_process(tmpdir, database, containers):
    _, analysis_dir, output_host_dir = _in_process_setup(tmpdir)

    def run(study, backend, use_dummy_data=False, action=generate_cohort):
        _in_process_run(
            study=study,
            analysis_dir=analysis_dir,
            output_host_path=output_host_dir / study.output_file_name,
            backend_id=backend,
            db_url=database.host_url(),
            use_dummy_data=use_dummy_data,
            action=action,
        )

        return output_host_dir / study.output_file_name

    return run


@pytest.fixture
def cohort_extractor_in_process_no_database(tmpdir, containers):
    _, analysis_dir, output_host_dir = _in_process_setup(tmpdir)

    def run(study, backend=None, use_dummy_data=False, action=generate_cohort):

        _in_process_run(
            study=study,
            analysis_dir=analysis_dir,
            output_host_path=output_host_dir / study.output_file_name,
            backend_id=backend,
            db_url=None,
            use_dummy_data=use_dummy_data,
            action=action,
        )
        return output_host_dir / study.output_file_name

    return run


@pytest.fixture
def cohort_extractor_generate_measures_in_process(tmpdir, containers):
    workspace, analysis_dir, output_host_dir = _in_process_setup(tmpdir)
    inputs_dir = workspace / "inputs"
    inputs_dir.mkdir()
    output_host_path = output_host_dir / "measures_*.csv"

    def run(study):
        for file in study.code():
            shutil.copy(file, analysis_dir)
        for file in study.input_files():
            shutil.copy(file, inputs_dir)

        definition_path = analysis_dir / study.definition().name
        input_file_path_pattern = inputs_dir / study.input_pattern
        generate_measures(definition_path, input_file_path_pattern, output_host_path)
        return output_host_path

    return run
