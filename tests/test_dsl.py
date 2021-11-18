import re

import pytest

from cohortextractor.concepts import tables
from cohortextractor.definition import Cohort, count, exists, pick_first_value, register
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

    assert_cohorts_equivalent(cohort, OldCohort)


def test_filter():
    class OldCohort:
        # Define tables of interest, filtered to relevant values
        code = (
            table("clinical_events")
            .filter("date", greater_than="2021-01-01")
            .first_by("date")
            .get("code")
        )

    cohort = Cohort()
    events = tables.clinical_events
    cohort.code = (
        events.filter(events.date, greater_than="2021-01-01")
        .select_column(events.code)
        .make_one_row_per_patient(pick_first_value)
    )

    assert_cohorts_equivalent(cohort, OldCohort)


def test_multiple_filters():
    class OldCohort:
        # Define tables of interest, filtered to relevant values
        code = (
            table("clinical_events")
            .filter("date", greater_than="2021-01-01")
            .filter("date", less_than="2021-10-10")
            .first_by("date")
            .get("code")
        )

    cohort = Cohort()
    events = tables.clinical_events
    cohort.code = (
        events.filter(events.date, greater_than="2021-01-01")
        .filter(events.date, less_than="2021-10-10")
        .select_column(events.code)
        .make_one_row_per_patient(pick_first_value)
    )

    assert_cohorts_equivalent(cohort, OldCohort)


def test_count_aggregation():
    class OldCohort:
        # Define tables of interest, filtered to relevant values
        num_events = table("clinical_events").count("code")

    cohort = Cohort()
    events = tables.clinical_events
    cohort.num_events = events.select_column(events.code).make_one_row_per_patient(
        count
    )

    assert_cohorts_equivalent(cohort, OldCohort)


def test_exists_aggregation():
    class OldCohort:
        # Define tables of interest, filtered to relevant values
        has_events = table("clinical_events").exists("code")

    cohort = Cohort()
    events = tables.clinical_events
    cohort.has_events = events.select_column(events.code).make_one_row_per_patient(
        exists
    )

    assert_cohorts_equivalent(cohort, OldCohort)


def test_set_population():
    index_date = "2021-01-01"

    class OldCohort:
        population = (
            table("practice_registrations").date_in_range(index_date).exists("date_end")
        )

    registations_table = tables.registrations
    registered = (
        registations_table.filter(
            registations_table.date_start, less_than_or_equals=index_date
        )
        .filter(
            registations_table.date_end,
            greater_than_or_equals=index_date,
            include_null=True,
        )
        .select_column(registations_table.date_end)
        .make_one_row_per_patient(exists)
    )

    cohort = Cohort()
    cohort.set_population(registered)
    assert_cohorts_equivalent(cohort, OldCohort)


def test_set_population_variable_must_be_boolean():
    registations_table = tables.registrations
    registered = registations_table.select_column(
        registations_table.date_end
    ).make_one_row_per_patient(pick_first_value)
    cohort = Cohort()

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Population variable must return a boolean. Did you mean to use `make_one_row_per_patient(exists)`?"
        ),
    ):
        cohort.set_population(registered)


@pytest.mark.parametrize(
    "variable_def, invalid_type",
    [
        (tables.clinical_events.select_column("code"), "Column"),
        ("code", "str"),
        (tables.clinical_events, "ClinicalEvents"),
    ],
)
def test_set_variable_errors(variable_def, invalid_type):
    cohort = Cohort()
    with pytest.raises(
        TypeError,
        match=re.escape(
            f"code must be a single value per patient (got '{invalid_type}')"
        ),
    ):
        cohort.code = variable_def


def assert_cohorts_equivalent(dsl_cohort, qm_cohort):
    """Verify that a cohort defined via Query Model objects has the same columns as a
    cohort defined via the DSL.

    Since some Query Model objects override `.__eq__`, we cannot compare two objects
    with `==`.  Instead, we compare their representations, which, thanks to dataclasses,
    contain all the information we need to compare for equality.
    """

    # Cohorts are equivalent if they have the same columns...
    dsl_col_defs = get_column_definitions(dsl_cohort)
    qm_col_defs = get_column_definitions(qm_cohort)
    assert dsl_col_defs.keys() == qm_col_defs.keys()

    # ...and if the columns are the same.
    for k in dsl_col_defs:
        assert repr(dsl_col_defs[k]) == repr(qm_col_defs[k])
