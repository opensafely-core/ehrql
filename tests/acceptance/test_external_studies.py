import sys
from pathlib import Path

import pytest

from databuilder.main import load_dataset_definition
from databuilder.query_language import compile

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
    "comparative-booster-ehrql-poc": dict(
        repo="opensafely/comparative-booster-ehrql-poc",
        branch="main",
        file_globs=[
            "analysis/codelists.py",
            "analysis/dataset_definition.py",
            "analysis/study-dates.json",
            "analysis/variables_lib.py",
            "codelists/*.csv",
        ],
        dataset_definitions=["analysis/dataset_definition.py"],
    ),
    "ons-cis-validation": dict(
        repo="opensafely/cis-pop-validation-ehrql",
        branch="main",
        file_globs=[
            "analysis/codelists_ehrql.py",
            "analysis/dataset_definition.py",
            "analysis/variable_lib.py",
            "codelists/*.csv",
        ],
        dataset_definitions=["analysis/dataset_definition.py"],
    ),
    "ons-mental-health": dict(
        repo="opensafely/MH_pandemic",
        branch="main",
        file_globs=[
            "analysis/dataset_definition_ons_cis_new.py",
        ],
        dataset_definitions=["analysis/dataset_definition_ons_cis_new.py"],
    ),
    "openprompt-long-covid-vaccines": dict(
        repo="opensafely/openprompt-vaccine-long-covid",
        branch="main",
        file_globs=[
            "analysis/dataset_definition*.py",
            "analysis/datasets.py",
            "analysis/codelists.py",
            "codelists/*.csv",
            "analysis/variable_lib.py",
        ],
        dataset_definitions=[
            "analysis/dataset_definition_cases.py",
            "analysis/dataset_definition_controls.py",
            "analysis/dataset_definition_longcovid_prevaccine.py",
        ],
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
        dataset_definitions=[
            "analysis/dataset_definition_dm017.py",
            "analysis/dataset_definition_dm020.py",
            "analysis/dataset_definition_dm021.py",
        ],
    ),
}

STUDY_DIR = Path(__file__).parent / "external_studies"


@pytest.fixture
def reset_module_namespace():
    """
    Studies often use the same names for modules (e.g. codelists.py, variables_lib.py)
    Ensure that we clean up the module namespace after each external study test.
    """
    original_modules = set(sys.modules.keys())
    yield
    new_modules = set(sys.modules.keys()) - original_modules
    for key in new_modules:
        del sys.modules[key]


@pytest.mark.parametrize("name", EXTERNAL_STUDIES.keys())
def test_external_study(name, monkeypatch, reset_module_namespace):
    # clear_module_namespace()
    study_path = STUDY_DIR / name
    for dataset_def in EXTERNAL_STUDIES[name]["dataset_definitions"]:
        dataset_def_path = study_path / dataset_def
        monkeypatch.chdir(study_path)
        # Test that we can compile the dataset definition to a valid query model graph. I
        # think this is sufficient for these tests which are intended to ensure we don't
        # accidentally break the API. If we're unable to execute a valid query, that's a
        # separate class of problem for which we need separate tests.
        dataset = load_dataset_definition(dataset_def_path, user_args=())
        variable_definitions = compile(dataset)
        assert variable_definitions
