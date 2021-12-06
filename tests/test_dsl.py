import re

import pytest

from cohortextractor2.concepts import tables
from cohortextractor2.definition import register
from cohortextractor2.definition.base import cohort_registry
from cohortextractor2.dsl import Cohort, codelist
from cohortextractor2.query_language import table
from cohortextractor2.query_utils import get_column_definitions

from .lib.util import OldCohortWithPopulation, make_codelist


def test_minimal_cohort_definition(cohort_with_population):
    # Nothing in the registry yet
    assert not cohort_registry.cohorts

    # old DSL
    class OldCohort(OldCohortWithPopulation):
        #  Define tables of interest, filtered to relevant values
        code = table("clinical_events").first_by("date").get("code")

    # new DSL
    cohort = cohort_with_population
    events = tables.clinical_events
    cohort.code = (
        events.sort_by(events.date).first_for_patient().select_column(events.code)
    )

    register(cohort)
    assert cohort in cohort_registry.cohorts
    assert_cohorts_equivalent(cohort, OldCohort)


def test_filter(cohort_with_population):
    class OldCohort(OldCohortWithPopulation):
        # Define tables of interest, filtered to relevant values
        code = (
            table("clinical_events")
            .filter("date", greater_than="2021-01-01")
            .first_by("date")
            .get("code")
        )

    cohort = cohort_with_population
    events = tables.clinical_events
    cohort.code = (
        events.filter(events.date, greater_than="2021-01-01")
        .sort_by(events.date)
        .first_for_patient()
        .select_column(events.code)
    )

    assert_cohorts_equivalent(cohort, OldCohort)


def test_filter_with_codelist(cohort_with_population):
    class OldCohort(OldCohortWithPopulation):
        code = (
            table("clinical_events")
            .filter("code", is_in=make_codelist("Code1"))
            .first_by("date")
            .get("code")
        )

    cohort = cohort_with_population
    events = tables.clinical_events
    cohort.code = (
        events.filter(codelist(["Code1"], "ctv3").contains(events.code))
        .sort_by(events.date)
        .first_for_patient()
        .select_column(events.code)
    )

    assert_cohorts_equivalent(cohort, OldCohort)


def test_multiple_filters(cohort_with_population):
    class OldCohort(OldCohortWithPopulation):
        # Define tables of interest, filtered to relevant values
        code = (
            table("clinical_events")
            .filter("date", greater_than="2021-01-01")
            .filter("date", less_than="2021-10-10")
            .first_by("date")
            .get("code")
        )

    cohort = cohort_with_population
    events = tables.clinical_events
    cohort.code = (
        events.filter(events.date, greater_than="2021-01-01")
        .filter(events.date, less_than="2021-10-10")
        .sort_by(events.date)
        .first_for_patient()
        .select_column(events.code)
    )

    assert_cohorts_equivalent(cohort, OldCohort)


def test_count_aggregation(cohort_with_population):
    class OldCohort(OldCohortWithPopulation):
        # Define tables of interest, filtered to relevant values
        num_events = table("clinical_events").count()

    cohort = cohort_with_population
    cohort.num_events = tables.clinical_events.count_for_patient()

    assert_cohorts_equivalent(cohort, OldCohort)


def test_exists_aggregation(cohort_with_population):
    class OldCohort(OldCohortWithPopulation):
        # Define tables of interest, filtered to relevant values
        has_events = table("clinical_events").filter("code", not_equals=None).exists()

    cohort = cohort_with_population
    events = tables.clinical_events
    cohort.has_events = events.filter(events.code, not_equals=None).exists_for_patient()

    assert_cohorts_equivalent(cohort, OldCohort)


def test_set_population():
    class OldCohort:
        population = table("practice_registrations").exists("patient_id")

    cohort = Cohort()
    cohort.set_population(tables.registrations.exists_for_patient())
    assert_cohorts_equivalent(cohort, OldCohort)


def test_set_population_variable_must_be_boolean():
    cohort = Cohort()

    with pytest.raises(
        ValueError,
        match=re.escape("Population variable must return a boolean."),
    ):
        cohort.set_population(tables.registrations.count_for_patient())


@pytest.mark.parametrize(
    "variable_def, invalid_type",
    [
        ("code", "str"),
        (tables.clinical_events, "ClinicalEvents"),
        (
            tables.clinical_events.filter(
                tables.clinical_events.date, greater_than="2021-01-01"
            ),
            "EventFrame",
        ),
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


def test_add_variable():
    events = tables.clinical_events

    cohort1 = Cohort()
    cohort1.set_population(tables.registrations.exists_for_patient())
    cohort1.add_variable("code", events.count_for_patient())

    cohort2 = Cohort()
    cohort2.set_population(tables.registrations.exists_for_patient())
    cohort2.add_variable("code", events.count_for_patient())

    assert_cohorts_equivalent(cohort1, cohort2)


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
    assert sorted(dsl_col_defs.keys()) == sorted(qm_col_defs.keys())

    # ...and if the columns are the same.
    for k in dsl_col_defs:
        assert repr(dsl_col_defs[k]) == repr(qm_col_defs[k])
