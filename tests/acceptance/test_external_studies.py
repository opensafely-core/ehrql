import contextlib
import sys
import warnings
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
        dataset_definitions=[],
        measure_definitions=[
            "analysis/dataset_definition_dm017.py",
            "analysis/dataset_definition_dm020.py",
            "analysis/dataset_definition_dm021.py",
        ],
    ),
    "openprompt-long-covid-economics": dict(
        repo="opensafely/openprompt_health_utilisation",
        branch="main",
        file_globs=[
            "analysis/dataset_definition_*.py",
            "analysis/codelists.py",
            "analysis/covariates.py",
            "analysis/hx_covariates.py",
            "analysis/outcomes_health_use.py",
            "analysis/variables.py",
            "codelists/*.csv",
        ],
        dummy_files=[
            "output/dataset_lc_gp_list.csv",
        ],
        dataset_definitions=[
            "analysis/dataset_definition_lc_gp_list.py",
            "analysis/dataset_definition_unmatched_exp_lc.py",
            "analysis/dataset_definition_unmatched_comparator.py",
            "analysis/dataset_definition_hx_unmatched_com_no_lc.py",
            "analysis/dataset_definition_hx_unmatched_exp_lc.py",
        ],
    ),
}

STUDY_DIR = Path(__file__).parent / "external_studies"


@contextlib.contextmanager
def reset_module_namespace():
    """
    Studies often use the same names for modules (e.g. codelists.py, variables_lib.py)
    Ensure that we clean up the module namespace after each external study test.
    """
    original_modules = set(sys.modules.keys())
    try:
        yield
    finally:
        new_modules = set(sys.modules.keys()) - original_modules
        for key in new_modules:
            del sys.modules[key]


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
    study_path = STUDY_DIR / study_name
    definition_path = study_path / definition_file
    with contextlib.ExitStack() as stack:
        # Studies often use project-relative paths so ensure these resolve correctly
        stack.enter_context(contextlib.chdir(study_path))
        # Studies often use the same names for modules (e.g. codelists.py,
        # variables_lib.py) Ensure that we clean up the module namespace after each
        # external study test.
        stack.enter_context(reset_module_namespace())
        # Usually we treat warnings as errors, but we want to ignore them in user code
        stack.enter_context(warnings.catch_warnings())
        warnings.simplefilter("ignore")
        # Import the dataset or measure definition. This tests that we can construct a
        # valid query model graph from the definition. I think this is sufficient for
        # these tests which are intended to ensure we don't accidentally break the API.
        # If we're unable to execute a valid query, that's a separate class of problem
        # for which we need separate tests.
        assert load_function(definition_path, user_args=())
