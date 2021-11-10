from cohortextractor.concepts import tables
from cohortextractor.definition import Cohort, pick_first_value, register
from cohortextractor.definition.base import cohort_registry
from cohortextractor.query_language import table
from cohortextractor.query_utils import get_column_definitions


def test_minimal_cohort_definition():
    # Nothing in the registry yet
    assert not cohort_registry.cohorts

    # old DSL
    class OldCohort:
        #  Define tables of interest, filtered to relevant values
        code = table("clinical_events").first_by("date").get("code")

    # new DSL
    cohort = Cohort()
    events = tables.clinical_events
    cohort.code = events.select_column(events.code).make_one_row_per_patient(
        pick_first_value
    )
    register(cohort)

    assert cohort in cohort_registry.cohorts
    (registered_cohort,) = cohort_registry.cohorts
    assert get_column_definitions(registered_cohort) == get_column_definitions(
        OldCohort
    )
