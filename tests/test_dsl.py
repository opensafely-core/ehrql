from cohortextractor.concepts import tables
from cohortextractor.definition import Cohort, pick_first_value, register
from cohortextractor.definition.base import registered_cohorts
from cohortextractor.query_language import table
from cohortextractor.query_utils import get_column_definitions


def test_minimal_cohort_definition():
    # Nothing in the registry yet
    assert not registered_cohorts

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

    assert cohort in registered_cohorts
    (registered_cohort,) = registered_cohorts
    assert get_column_definitions(registered_cohort) == get_column_definitions(
        OldCohort
    )
