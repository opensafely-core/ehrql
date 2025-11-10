import contextlib
from pathlib import Path

import pytest

from ehrql.main import load_dataset_definition, load_measure_definitions


# These tests specify dataset definitions in other repositories which we want to ensure
# we don't accidentally break. In order to keep tests hermetic and deterministic, we
# copy the study code into the repo and commit it (taking care to copy just the files
# needed to evalute the dataset definition). The `update_external_studies.py` script
# handles this. It can be invoked as:
#
#     python -m tests.acceptance.update_external_studies
#
# Or via just as:
#
#     just update-external-studies
#
# This is run automatically by a scheduled action which will create a PR if there are
# any changes to be made.
EXTERNAL_STUDIES = {
    "test-age-distribution": dict(
        repo="opensafely/test-age-distribution",
        branch="main",
        file_globs=[
            "analysis/dataset_definition.py",
        ],
        dataset_definitions=["analysis/dataset_definition.py"],
    ),
    "qof-diabetes": dict(
        repo="opensafely/qof-diabetes",
        branch="main",
        file_globs=[
            "analysis/dataset_definition_*.py",
            "analysis/dm_dataset.py",
            "analysis/codelists.py",
            "analysis/variable_lib_helper.py",
            "codelists/*.csv",
        ],
        dataset_definitions=[],
        measure_definitions=[
            "analysis/dataset_definition_dm017.py",
            ("analysis/dataset_definition_dm020.py", ["--ifcchba-cutoff-val", "58"]),
            ("analysis/dataset_definition_dm021.py", ["--ifcchba-cutoff-val", "75"]),
        ],
    ),
    "waiting-list": dict(
        repo="opensafely/waiting-list",
        branch="main",
        file_globs=[
            "analysis/codelists.py",
            "analysis/dataset_definition_full.py",
            "analysis/measures_checks.py",
            "analysis/measures_opioid.py",
            "codelists/*.csv",
        ],
        dataset_definitions=[
            "analysis/dataset_definition_full.py",
        ],
        measure_definitions=[
            "analysis/measures_checks.py",
            ("analysis/measures_opioid.py", ["--codelist", "opioid_codes"]),
        ],
    ),
    "mainroute_cancer": dict(
        repo="opensafely/mainroute_cancer",
        branch="main",
        file_globs=[
            "analysis/codelists.py",
            "analysis/dataset_definition.py",
            "analysis/define_static_dataset.py",
            "analysis/measures_demo.py",
            "codelists/*.csv",
            "local_codelists/*.csv",
        ],
        dataset_definitions=[
            "analysis/define_static_dataset.py",
        ],
        measure_definitions=[
            (
                "analysis/measures_demo.py",
                ["--start-date", "2018-03-23", "--intervals", "67"],
            ),
        ],
    ),
}

STUDY_DIR = Path(__file__).parent / "external_studies"


@pytest.mark.parametrize(
    "study_name,definition_file,load_function",
    [
        (study_name, dataset_def, load_dataset_definition)
        for (study_name, config) in EXTERNAL_STUDIES.items()
        for dataset_def in config["dataset_definitions"]
    ]
    + [
        (study_name, measure_def, load_measure_definitions)
        for (study_name, config) in EXTERNAL_STUDIES.items()
        for measure_def in config.get("measure_definitions", ())
    ],
)
def test_external_study(study_name, definition_file, load_function):
    if isinstance(definition_file, tuple):
        definition_file, user_args = definition_file
    else:
        user_args = []
    study_path = STUDY_DIR / study_name
    definition_path = study_path / definition_file
    # Studies often use project-relative paths so ensure these resolve correctly
    with contextlib.chdir(study_path):
        # Load the dataset or measure definition. This tests that we can construct a
        # valid query model graph from the definition. I think this is sufficient for
        # these tests which are intended to ensure we don't accidentally break the API.
        # If we're unable to execute a valid query, that's a separate class of problem
        # for which we need separate tests.
        assert load_function(definition_path, user_args=user_args, environ={})
