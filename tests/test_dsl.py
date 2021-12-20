import re

import pytest

from databuilder import codelist
from databuilder.concepts import tables
from databuilder.definition import register
from databuilder.definition.base import cohort_registry
from databuilder.dsl import Cohort
from databuilder.query_language import table
from databuilder.query_utils import get_column_definitions

from .lib.util import OldCohortWithPopulation, make_codelist, mock_positive_tests


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
        events.filter(events.date > "2021-01-01")
        .sort_by(events.date)
        .first_for_patient()
        .select_column(events.code)
    )

    assert_cohorts_equivalent(cohort, OldCohort)


@pytest.mark.parametrize(
    "kwarg, method",
    [
        ("equals", "__eq__"),
        ("not_equals", "__ne__"),
        ("less_than", "__lt__"),
        ("less_than_or_equals", "__le__"),
        ("greater_than", "__gt__"),
        ("greater_than_or_equals", "__ge__"),
    ],
)
def test_date_predicates(cohort_with_population, kwarg, method):
    events = tables.clinical_events

    class OldCohort(OldCohortWithPopulation):
        has_code = (
            table("clinical_events").filter("date", **{kwarg: "2021-01-01"}).exists()
        )

    cohort = cohort_with_population
    predicate = getattr(events.date, method)(
        "2021-01-01"
    )  # e.g. events.date >= "2021-01-01"
    cohort.has_code = events.filter(predicate).exists_for_patient()

    assert_cohorts_equivalent(cohort, OldCohort)


@pytest.mark.parametrize(
    "kwarg, method",
    [
        ("equals", "__eq__"),
        ("not_equals", "__ne__"),
        ("less_than", "__lt__"),
        ("less_than_or_equals", "__le__"),
        ("greater_than", "__gt__"),
        ("greater_than_or_equals", "__ge__"),
    ],
)
def test_int_predicates(cohort_with_population, kwarg, method):
    events = tables.clinical_events

    class OldCohort(OldCohortWithPopulation):
        has_code = table("clinical_events").filter("value", **{kwarg: 42}).exists()

    cohort = cohort_with_population
    predicate = getattr(events.value, method)(42)  # e.g. events.value < 42
    cohort.has_code = events.filter(predicate).exists_for_patient()

    assert_cohorts_equivalent(cohort, OldCohort)


def test_comparison_inversion_works(cohort_with_population):
    # Check that authors can write `42 > events.value` as well as `events.value > 42`.
    events = tables.clinical_events

    class OldCohort(OldCohortWithPopulation):
        fish = table("clinical_events").filter("value", less_than=42).exists()

    cohort = cohort_with_population
    cohort.fish = events.filter(42 > events.value).exists_for_patient()

    assert_cohorts_equivalent(cohort, OldCohort)


@pytest.mark.parametrize(
    "kwarg, method",
    [
        ("equals", "__eq__"),
        ("not_equals", "__ne__"),
    ],
)
def test_code_predicates(cohort_with_population, kwarg, method):
    events = tables.clinical_events

    class OldCohort(OldCohortWithPopulation):
        has_code = table("clinical_events").filter("code", **{kwarg: "abc"}).exists()

    cohort = cohort_with_population
    predicate = getattr(events.code, method)("abc")  # e.g. events.code == "abc"
    cohort.has_code = events.filter(predicate).exists_for_patient()

    assert_cohorts_equivalent(cohort, OldCohort)


@pytest.mark.parametrize(
    "kwarg, old_value, method, new_value",
    [
        ("equals", True, "__eq__", True),
        ("equals", False, "__eq__", False),
        ("equals", False, "__ne__", True),
        ("equals", True, "__ne__", False),
    ],
)
def test_bool_predicates(cohort_with_population, kwarg, old_value, method, new_value):
    # Standard Python style frowns on direct equality comparison against True/False, but we want to allow authors to
    # write it this way if they like.
    tests = mock_positive_tests

    class OldCohort(OldCohortWithPopulation):
        result = table("positive_tests").filter("result", **{kwarg: old_value}).exists()

    cohort = cohort_with_population
    predicate = getattr(tests.result, method)(new_value)  # e.g. events.result == True
    cohort.result = tests.filter(predicate).exists_for_patient()

    assert_cohorts_equivalent(cohort, OldCohort)


def test_alternative_bool_predicates(cohort_with_population):
    # We provide these because standard Python style frowns on direct equality comparison against True/False.
    tests = mock_positive_tests

    class OldCohort(OldCohortWithPopulation):
        success = table("positive_tests").filter("result", equals=True).exists()
        failure = table("positive_tests").filter("result", equals=False).exists()

    cohort = cohort_with_population
    cohort.success = tests.filter(tests.result.is_true()).exists_for_patient()
    cohort.failure = tests.filter(tests.result.is_false()).exists_for_patient()

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
        events.filter(events.code.is_in(codelist(["Code1"], "ctv3")))
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
        events.filter(events.date > "2021-01-01")
        .filter(events.date < "2021-10-10")
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
    cohort.has_events = events.filter(events.code.is_not_null()).exists_for_patient()

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
            tables.clinical_events.filter(tables.clinical_events.date > "2021-01-01"),
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


def test_population_required():
    data_definition = Cohort()

    with pytest.raises(ValueError, match="must define a 'population' variable"):
        get_column_definitions(data_definition)

    data_definition.set_population(tables.registrations.exists_for_patient())
    get_column_definitions(data_definition)


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
