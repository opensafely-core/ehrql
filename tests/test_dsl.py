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
    assert_cohorts_equivalent(OldCohort, cohort)


def assert_cohorts_equivalent(old_cohort, new_cohort):
    """Verify that a cohort defined via Query Model objects has the same columns as a
    cohort defined via the DSL.

    This requires the addition of a temporary `.equals` method on Query Model objects to
    support comparison for equality, since some SM objects override `.__eq__`, meaning
    we cannot compare two objects with `==`.
    """

    # Cohorts are equivalent if they have the same columns...
    old_col_defs = get_column_definitions(old_cohort)
    new_col_defs = get_column_definitions(new_cohort)
    assert old_col_defs.keys() == new_col_defs.keys()

    # ...and if the columns are the same.
    for k in old_col_defs:
        assert old_col_defs[k].equals(new_col_defs[k])
