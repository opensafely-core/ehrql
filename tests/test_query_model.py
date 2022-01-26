import re

import pytest

from databuilder.codelistlib import Codelist
from databuilder.query_model_old import (
    Comparator,
    FilteredTable,
    Row,
    Table,
    ValueFromRow,
    table,
)
from databuilder.query_utils import get_column_definitions

from .lib.util import OldCohortWithPopulation, make_codelist


def test_cannot_use_equals_with_codelist_or_columns():
    test_codelist = make_codelist("abc")
    all_codes = table("clinical_events").get("codes")

    msg_eq = "You can only use 'equals' to filter a column by a single value"
    with pytest.raises(TypeError, match=msg_eq):
        table("clinical_events").filter(code=test_codelist)
    with pytest.raises(TypeError, match=msg_eq):
        table("clinical_events").filter(code=all_codes)

    msg_ne = "You can only use 'not_equals' to filter a column by a single value"
    with pytest.raises(TypeError, match=msg_ne):
        table("clinical_events").filter("code", not_equals=test_codelist)
    with pytest.raises(TypeError, match=msg_ne):
        table("clinical_events").filter("code", not_equals=all_codes)


def test_comparator_logical_comparisons_not_handled_directly():
    msg = "Invalid operation; cannot perform logical operations on a Comparator"

    with pytest.raises(RuntimeError, match=msg):
        Comparator() > Comparator()

    with pytest.raises(RuntimeError, match=msg):
        Comparator() >= Comparator()

    with pytest.raises(RuntimeError, match=msg):
        Comparator() < Comparator()

    with pytest.raises(RuntimeError, match=msg):
        Comparator() <= Comparator()


def test_comparator_eq():
    output = Comparator() == Comparator()

    expected = Comparator(
        operator="__eq__",
        lhs=Comparator(),
        rhs=Comparator(),
    )

    assert repr(output) == repr(expected)


def test_comparator_ne():
    output = Comparator() != Comparator()

    expected = Comparator(
        operator="__ne__",
        lhs=Comparator(),
        rhs=Comparator(),
    )

    assert repr(output) == repr(expected)


def test_cohort_column_definitions_simple_query():
    class Cohort(OldCohortWithPopulation):
        #  Define tables of interest, filtered to relevant values
        _abc_table = table("clinical_events").filter("code", is_in=make_codelist("abc"))
        # Get a single row per patient by selecting the latest event
        _abc_values = _abc_table.latest()
        # define columns in output
        abc_value = _abc_values.get("test_value")
        date = _abc_values.get("date")

    column_definitions = get_column_definitions(Cohort)

    assert sorted(column_definitions.keys()) == ["abc_value", "date", "population"]
    output_values = [
        value for key, value in column_definitions.items() if key != "population"
    ]
    for output_value in output_values:
        # There are 2 outputs, each a simple get on a Row from the same FilteredTable
        assert isinstance(output_value, ValueFromRow)
        assert isinstance(output_value.source, Row)
        assert isinstance(output_value.source.source, FilteredTable)
        assert output_value.source.source.operator == "in_"


def test_cohort_column_definitions_invalid_output_value():
    class Cohort(OldCohortWithPopulation):
        #  Define tables of interest, filtered to relevant values
        _abc_table = table("clinical_events").filter("code", is_in=make_codelist("abc"))
        # Try to return the test_value column, which should raise an exception
        value = _abc_table.get("test_value")

    with pytest.raises(
        TypeError,
        match=re.escape("Cohort variable 'value' is not a Value (type='Column')"),
    ):
        get_column_definitions(Cohort)


def test_cohort_column_definitions_chained_query():
    class Cohort(OldCohortWithPopulation):
        _abc = (
            table("clinical_events")
            .filter("code", is_in=make_codelist("abc"))
            .filter("date", greater_than="2021-01-01")
        )
        _abc_values = _abc.latest()
        abc_value = _abc_values.get("test_value")

    column_definitions = get_column_definitions(Cohort)
    assert sorted(column_definitions.keys()) == ["abc_value", "population"]

    output_value = column_definitions["abc_value"]
    # This final value is the result of a chained filter and latest query:
    # table("clinical_events").filter("code", is_in="abc").filter("date",greater_than="2021-01-01").latest()

    assert isinstance(output_value, ValueFromRow)
    row = output_value.source
    assert isinstance(row, Row)
    # The row comes from a filtered table, which is itself from a filtered table, in the reverse
    # order that the study definition filtered them
    last_filtered_table = row.source
    assert isinstance(last_filtered_table, FilteredTable)
    assert last_filtered_table.operator == "__gt__"
    assert last_filtered_table.column == "date"
    assert last_filtered_table.value == "2021-01-01"

    penultimate_filtered_table = last_filtered_table.source
    assert isinstance(penultimate_filtered_table, FilteredTable)
    assert penultimate_filtered_table.operator == "in_"
    assert penultimate_filtered_table.column == "code"
    assert isinstance(penultimate_filtered_table.value, Codelist)
    assert penultimate_filtered_table.value.codes == ("abc",)
    initial_table = penultimate_filtered_table.source
    assert isinstance(initial_table, Table)
    assert initial_table.name == "clinical_events"


def test_cohort_column_definitions_between_operator():
    """A between operator is turned into a chained lt and gt"""

    class Cohort(OldCohortWithPopulation):
        _event_table = table("clinical_events")
        _first_date = _event_table.earliest().get("date")
        _last_date = _event_table.latest().get("date")
        _date_between = _event_table.filter(
            "date", between=[_first_date, _last_date]
        ).latest()
        value_between = _date_between.get("test_value")

    column_definitions = get_column_definitions(Cohort)
    row = column_definitions["value_between"].source
    last_filtered_table = row.source
    assert last_filtered_table.operator == "__le__"
    penultimate_filtered_table = last_filtered_table.source
    assert penultimate_filtered_table.operator == "__ge__"


@pytest.mark.parametrize(
    "operator",
    [
        "greater_than",
        "greater_than_or_equals",
        "less_than",
        "less_than_or_equals",
        "on_or_before",
        "on_or_after",
    ],
)
def test_cohort_column_definitions_filter_operators(operator):
    class Cohort(OldCohortWithPopulation):
        _filtered = (
            table("clinical_events").filter("date", **{operator: "2021-01-01"}).latest()
        )
        output_value = _filtered.get("test_value")

    column_definitions = get_column_definitions(Cohort)
    operator_mapping = {
        "equals": "__eq__",
        "less_than": "__lt__",
        "less_than_or_equals": "__le__",
        "greater_than": "__gt__",
        "greater_than_or_equals": "__ge__",
        "on_or_before": "__le__",
        "on_or_after": "__ge__",
    }
    assert (
        column_definitions["output_value"].source.source.operator
        == operator_mapping[operator]
    )


def test_cohort_column_definitions_multiple_field_operators():
    class Cohort(OldCohortWithPopulation):
        _filtered = (
            table("clinical_events")
            .filter("numerical_value", greater_than=2, less_than_or_equals=6)
            .latest()
        )
        output_value = _filtered.get("test_value")

    column_definitions = get_column_definitions(Cohort)
    row = column_definitions["output_value"].source
    last_filtered_table = row.source
    assert last_filtered_table.operator == "__le__"
    penultimate_filtered_table = last_filtered_table.source
    assert penultimate_filtered_table.operator == "__gt__"


def test_cohort_column_definitions_multiple_equals_operators():
    class Cohort(OldCohortWithPopulation):
        _filtered = (
            table("clinical_events")
            .filter("code", is_in=make_codelist(3))
            .filter(positive_test=True)
            .latest()
        )
        output_value = _filtered.get("test_value")

    column_definitions = get_column_definitions(Cohort)
    row = column_definitions["output_value"].source
    last_filtered_table = row.source
    assert last_filtered_table.operator == "__eq__"
    assert last_filtered_table.column == "positive_test"
    penultimate_filtered_table = last_filtered_table.source
    assert penultimate_filtered_table.operator == "in_"
    assert penultimate_filtered_table.column == "code"
