import importlib.util

from cohortextractor.__main__ import get_column_definitions
from cohortextractor.query_language import ValueFromRow


def test_cohort_column_definitions(study):
    study_definition_path = study("end_to_end_tests_filtering").grab_study_definition()
    spec = importlib.util.spec_from_file_location("module.name", study_definition_path)
    study_definition = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(study_definition)
    Cohort = getattr(study_definition, "Cohort")
    column_definitions = get_column_definitions(Cohort)
    assert list(column_definitions.keys()) == ["abc_value", "date"]
    for value in column_definitions.values():
        assert isinstance(value, ValueFromRow)
