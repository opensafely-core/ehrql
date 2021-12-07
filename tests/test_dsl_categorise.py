"""
Categorisation in this file are tested against mock data in test_query_engine.py using the
old-style DSL.  These tests check that categorisation in the new-style DSL produce the same
query graph as the old DSL.
"""
import re

import pytest

from cohortextractor2 import codelist
from cohortextractor2.concepts import tables
from cohortextractor2.dsl import BoolColumn, EventFrame, IdColumn, IntColumn
from cohortextractor2.dsl import categorise as new_dsl_categorise
from cohortextractor2.query_language import Comparator, Table
from cohortextractor2.query_language import categorise as old_dsl_categorise
from cohortextractor2.query_language import table

from .lib.util import OldCohortWithPopulation, make_codelist
from .test_dsl import assert_cohorts_equivalent


class MockPatientsTable(EventFrame):
    patient_id = IdColumn("patient_id")
    height = IntColumn("height")

    def __init__(self):
        super().__init__(Table("patients"))


mock_patients = MockPatientsTable()


class MockPositiveTestsTable(EventFrame):
    patient_id = IdColumn("patient_id")
    result = BoolColumn("result")

    def __init__(self):
        super().__init__(Table("positive_tests"))


mock_positive_tests = MockPositiveTestsTable()


def test_categorise(cohort_with_population):
    class OldCohort(OldCohortWithPopulation):
        # Define tables of interest, filtered to relevant values
        _first_code_date = table("clinical_events").first_by("date").get("date")
        _date_categories = {
            "before_2021": _first_code_date < "2021-01-01",
            "after_2021": _first_code_date >= "2021-01-01",
        }
        date_group = old_dsl_categorise(_date_categories, default="unknown")

    cohort = cohort_with_population
    events = tables.clinical_events
    first_code_date = (
        events.sort_by(events.date).first_for_patient().select_column(events.date)
    )
    date_categories = {
        "before_2021": first_code_date < "2021-01-01",
        "after_2021": first_code_date >= "2021-01-01",
    }
    cohort.date_group = new_dsl_categorise(date_categories, default="unknown")

    assert_cohorts_equivalent(cohort, OldCohort)


@pytest.mark.parametrize(
    "categories,default",
    [
        (
            lambda height_value: {
                "tall": height_value > 190,
                "medium": (height_value <= 190) & (height_value > 150),
                "short": height_value < 150,
            },
            "missing",
        ),
        (
            lambda height_value: {
                "short_or_tall": (height_value < 150) | (height_value > 190)
            },
            "medium",
        ),
        (
            lambda height_value: {
                "short_or_tall": (height_value < 150) | (height_value > 190)
            },
            None,
        ),
        (
            lambda height_value: {
                "tallish": (height_value > 175) & (height_value != 180),
                "short": height_value <= 175,
            },
            "missing",
        ),
    ],
    ids=[
        "test simple and on two conditions",
        "test simple or on two conditions",
        "test simple or with None default",
        "test a not-equals condition",
    ],
)
def test_categorise_single_combined_conditions(
    cohort_with_population, categories, default
):
    default_kwarg = {"default": default} if default is not None else {}

    class OldCohort(OldCohortWithPopulation):
        _height = table("patients").first_by("patient_id").get("height")
        _height_categories = categories(_height)
        height_group = old_dsl_categorise(_height_categories, **default_kwarg)

    cohort = cohort_with_population
    height = (
        mock_patients.sort_by(mock_patients.patient_id)
        .first_for_patient()
        .select_column(mock_patients.height)
    )
    height_categories = categories(height)
    cohort.height_group = new_dsl_categorise(height_categories, **default_kwarg)
    assert_cohorts_equivalent(cohort, OldCohort)


def test_categorise_multiple_values(cohort_with_population):
    """Test that categories can combine conditions that use different source values"""

    class OldCohort(OldCohortWithPopulation):
        _height = table("patients").first_by("patient_id").get("height")
        _code = table("clinical_events").first_by("date").get("code")
        _height_with_codes_categories = {
            "short": (_height < 190) & (_code == "abc"),
            "tall": (_height > 190) & (_code == "abc"),
        }
        height_group = old_dsl_categorise(
            _height_with_codes_categories, default="missing"
        )

    cohort = cohort_with_population
    height = (
        mock_patients.sort_by(mock_patients.patient_id)
        .first_for_patient()
        .select_column(mock_patients.height)
    )
    code = (
        tables.clinical_events.sort_by(tables.clinical_events.date)
        .first_for_patient()
        .select_column(tables.clinical_events.code)
    )
    height_with_codes_categories = {
        "short": (height < 190) & (code == "abc"),
        "tall": (height > 190) & (code == "abc"),
    }
    cohort.height_group = new_dsl_categorise(
        height_with_codes_categories, default="missing"
    )
    assert_cohorts_equivalent(cohort, OldCohort)


def test_categorise_nested_comparisons(cohort_with_population):
    class OldCohort(OldCohortWithPopulation):
        _height = table("patients").first_by("patient_id").get("height")
        _code = table("clinical_events").first_by("date").get("code")

        # make sure the parentheses precedence is followed; these two expressions are equivalent
        _height_with_codes_categories = {
            "tall_or_code": (_height > 190) | ((_height < 150) & (_code == "abc")),
        }
        _codes_with_height_categories = {
            "code_or_tall": ((_height < 150) & (_code == "abc")) | (_height > 190),
        }
        height_group = old_dsl_categorise(_height_with_codes_categories, default="na")
        height_group1 = old_dsl_categorise(_codes_with_height_categories, default="na")

    cohort = cohort_with_population
    height = (
        mock_patients.sort_by(mock_patients.patient_id)
        .first_for_patient()
        .select_column(mock_patients.height)
    )
    code = (
        tables.clinical_events.sort_by(tables.clinical_events.date)
        .first_for_patient()
        .select_column(tables.clinical_events.code)
    )
    height_with_codes_categories = {
        "tall_or_code": (height > 190) | ((height < 150) & (code == "abc")),
    }
    codes_with_height_categories = {
        "code_or_tall": ((height < 150) & (code == "abc")) | (height > 190),
    }

    cohort.height_group = new_dsl_categorise(height_with_codes_categories, default="na")
    cohort.height_group1 = new_dsl_categorise(
        codes_with_height_categories, default="na"
    )
    assert_cohorts_equivalent(cohort, OldCohort)


def test_categorise_on_truthiness(cohort_with_population):
    """Test truthiness of a Value from an exists aggregation"""

    class OldCohort(OldCohortWithPopulation):
        _code = (
            table("clinical_events").filter("code", is_in=make_codelist("abc")).exists()
        )
        _codes_categories = {"yes": _code}
        abc = old_dsl_categorise(_codes_categories, default="na")

    cohort = cohort_with_population
    events = tables.clinical_events
    code = events.filter(
        events.code.is_in(codelist(["abc"], "ctv3"))
    ).exists_for_patient()
    codes_categories = {"yes": code}
    cohort.abc = new_dsl_categorise(codes_categories, default="na")
    assert_cohorts_equivalent(cohort, OldCohort)


def test_categorise_on_truthiness_from_filter(cohort_with_population):
    """Test truthiness of a Value from a filtered value"""

    class OldCohort(OldCohortWithPopulation):
        _code = (
            table("clinical_events")
            .filter("code", is_in=make_codelist("abc", "def"))
            .latest()
            .get("code")
        )
        _codes_categories = {"yes": _code}
        has_code = old_dsl_categorise(_codes_categories, default="na")

    cohort = cohort_with_population
    events = tables.clinical_events
    code = (
        events.filter(events.code.is_in(codelist(["abc", "def"], "ctv3")))
        .sort_by(events.date)
        .last_for_patient()
        .select_column(events.code)
    )
    codes_categories = {"yes": code}
    cohort.has_code = new_dsl_categorise(codes_categories, default="na")
    assert_cohorts_equivalent(cohort, OldCohort)


def test_categorise_multiple_truthiness_values(cohort_with_population):
    class OldCohort(OldCohortWithPopulation):
        _code = (
            table("clinical_events")
            .filter("code", is_in=make_codelist("abc", "def"))
            .latest()
            .get("code")
        )
        _has_positive_test = table("positive_tests").filter(result=True).exists()
        _codes_categories = {"yes": _code & _has_positive_test}
        has_positive_code = old_dsl_categorise(_codes_categories, default="na")

    cohort = cohort_with_population
    events = tables.clinical_events
    code = (
        events.filter(events.code.is_in(codelist(["abc", "def"], "ctv3")))
        .sort_by(events.date)
        .last_for_patient()
        .select_column(events.code)
    )
    has_positive_test = mock_positive_tests.filter(
        mock_positive_tests.result
    ).exists_for_patient()
    codes_categories = {"yes": code & has_positive_test}
    cohort.has_positive_code = new_dsl_categorise(codes_categories, default="na")
    assert_cohorts_equivalent(cohort, OldCohort)


def test_categorise_invert(cohort_with_population):
    class OldCohort(OldCohortWithPopulation):
        _height = table("patients").first_by("patient_id").get("height")
        _code = table("clinical_events").first_by("patient_id").get("code")

        # make sure the parentheses precedence is followed; these two expressions are equivalent
        _height_inverted = {
            "tall": _height > 190,
            "not_tall": ~(_height > 190),
        }
        height_group = old_dsl_categorise(_height_inverted, default="na")

    cohort = cohort_with_population
    height = (
        mock_patients.sort_by(mock_patients.patient_id)
        .first_for_patient()
        .select_column(mock_patients.height)
    )
    height_inverted = {
        "tall": height > 190,
        "not_tall": ~(height > 190),
    }
    cohort.height_group = new_dsl_categorise(height_inverted, default="na")
    assert_cohorts_equivalent(cohort, OldCohort)


def test_categorise_invert_truthiness_values(cohort_with_population):
    class OldCohort(OldCohortWithPopulation):
        _code = (
            table("clinical_events")
            .filter("code", is_in=make_codelist("abc", "def"))
            .latest()
            .get("code")
        )
        _codes_categories = {"yes": _code, "no": ~_code}
        has_code = old_dsl_categorise(_codes_categories, default="na")

    cohort = cohort_with_population
    events = tables.clinical_events
    code = (
        events.filter(events.code.is_in(codelist(["abc", "def"], "ctv3")))
        .sort_by(events.date)
        .last_for_patient()
        .select_column(events.code)
    )
    codes_categories = {"yes": code, "no": ~code}
    cohort.has_code = new_dsl_categorise(codes_categories, default="na")
    assert_cohorts_equivalent(cohort, OldCohort)


def test_categorise_invert_combined_values(cohort_with_population):
    class OldCohort(OldCohortWithPopulation):
        _code = (
            table("clinical_events")
            .filter("code", is_in=make_codelist("abc", "def"))
            .latest()
            .get("code")
        )
        _has_positive_test = table("positive_tests").filter(result=True).exists()
        _codes_categories = {"neg_or_no_code": ~(_code & _has_positive_test)}
        result_group = old_dsl_categorise(_codes_categories, default="pos")

    cohort = cohort_with_population
    events = tables.clinical_events
    code = (
        events.filter(events.code.is_in(codelist(["abc", "def"], "ctv3")))
        .sort_by(events.date)
        .last_for_patient()
        .select_column(events.code)
    )
    has_positive_test = mock_positive_tests.filter(
        mock_positive_tests.result
    ).exists_for_patient()
    codes_categories = {"neg_or_no_code": ~(code & has_positive_test)}
    cohort.result_group = new_dsl_categorise(codes_categories, default="pos")
    assert_cohorts_equivalent(cohort, OldCohort)


def test_categorise_double_invert(cohort_with_population):
    class OldCohort(OldCohortWithPopulation):
        _code = (
            table("clinical_events")
            .filter("code", is_in=make_codelist("abc", "def"))
            .latest()
            .get("code")
        )
        _codes_categories = {"yes": ~~_code}
        has_code = old_dsl_categorise(_codes_categories, default="na")

    cohort = cohort_with_population
    events = tables.clinical_events
    code = (
        events.filter(events.code.is_in(codelist(["abc", "def"], "ctv3")))
        .sort_by(events.date)
        .last_for_patient()
        .select_column(events.code)
    )
    codes_categories = {"yes": ~~code}
    cohort.has_code = new_dsl_categorise(codes_categories, default="na")
    assert_cohorts_equivalent(cohort, OldCohort)


@pytest.mark.parametrize(
    "category_mapping,error,error_match",
    [
        (
            {"yes": 1, "no": 2},
            TypeError,
            re.escape("Got '1' (<class 'int'>) for category key 'yes'"),
        ),
        (
            {"yes": mock_positive_tests.exists_for_patient(), "no": 2},
            TypeError,
            re.escape("Got '2' (<class 'int'>) for category key 'no'"),
        ),
        (
            {"positive": mock_positive_tests},
            TypeError,
            r"Got .*MockPositiveTestsTable.* for category key 'positive'",
        ),
        (
            {
                "yes": mock_positive_tests.exists_for_patient(),
                "no": mock_positive_tests.exists_for_patient(),
            },
            ValueError,
            re.escape("Duplicate category values found for key: 'no'"),
        ),
        (
            {
                "yes": mock_positive_tests.count_for_patient() >= 1,
                0: mock_positive_tests.count_for_patient() < 1,
            },
            TypeError,
            re.escape(
                "Multiple category key types found: yes (<class 'str'>), 0 (<class 'int'>)"
            ),
        ),
        (
            {"no": mock_positive_tests.exists_for_patient(), 1: "yes", 2: "yes"},
            # multiple errors are chained and then raised recursively, the most recent call in the
            # traceback is the first error encountered (the first invalid value type)
            TypeError,
            re.escape("Got 'yes' (<class 'str'>) for category key '1'"),
        ),
    ],
)
def test_categorise_validation(category_mapping, error, error_match):
    with pytest.raises(error, match=error_match):
        new_dsl_categorise(category_mapping, default="na")


def test_categorise_invalid_default():
    category_mapping = {
        "yes": mock_positive_tests.count_for_patient() >= 1,
        "no": mock_positive_tests.count_for_patient() == 0,
    }
    with pytest.raises(
        TypeError,
        match=r"Default category.*(expected <class 'str'>, got <class 'int'>)",
    ):
        new_dsl_categorise(category_mapping, default=999)


def test_cannot_compare_comparators():
    codes = tables.clinical_events.count_for_patient()
    count_3 = codes == 3
    assert isinstance(count_3.value, Comparator)
    with pytest.raises(RuntimeError, match="Invalid operation"):
        (codes == 3) > 2
