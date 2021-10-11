import pytest
from lib.util import make_codelist

from cohortextractor.codelistlib import Codelist
from cohortextractor.query_language import (
    FilteredTable,
    Row,
    Table,
    ValidationError,
    ValueFromRow,
    table,
)
from cohortextractor.query_utils import get_column_definitions


def test_cohort_filter_table_codelist_validation():
    """A code filter must filter on a codelist"""
    with pytest.raises(ValidationError):

        class Cohort:
            #  Define tables of interest, filtered to relevant values
            abc_table = table("clinical_events").filter(code="abc")


def test_cohort_column_definitions_simple_query():
    class Cohort:
        #  Define tables of interest, filtered to relevant values
        _abc_table = table("clinical_events").filter(code=make_codelist("abc"))
        # Get a single row per patient by selecting the latest event
        _abc_values = _abc_table.latest()
        # define columns in output
        abc_value = _abc_values.get("test_value")
        date = _abc_values.get("date")

    column_definitions = get_column_definitions(Cohort)

    assert list(column_definitions.keys()) == ["abc_value", "date"]
    for output_value in column_definitions.values():
        # There are 2 outputs, each a simple get on a Row from the same FilteredTable
        assert isinstance(output_value, ValueFromRow)
        assert isinstance(output_value.source, Row)
        assert isinstance(output_value.source.source, FilteredTable)
        assert output_value.source.source.operator == "__eq__"


def test_cohort_column_definitions_chained_query():
    class Cohort:
        _abc = (
            table("clinical_events")
            .filter(code=make_codelist("abc"))
            .filter("date", greater_than="2021-01-01")
        )
        _abc_values = _abc.latest()
        abc_value = _abc_values.get("test_value")

    column_definitions = get_column_definitions(Cohort)
    assert list(column_definitions.keys()) == ["abc_value"]

    output_value = column_definitions["abc_value"]
    # This final value is the result of a chained filter and latest query:
    # table("clinical_events").filter(code="abc").filter("date",greater_than="2021-01-01").latest()

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
    assert penultimate_filtered_table.operator == "__eq__"
    assert penultimate_filtered_table.column == "code"
    assert isinstance(penultimate_filtered_table.value, Codelist)
    assert penultimate_filtered_table.value.codes == ["abc"]
    initial_table = penultimate_filtered_table.source
    assert isinstance(initial_table, Table)
    assert initial_table.name == "clinical_events"


def test_cohort_column_definitions_between_operator():
    """A between operator is turned into a chained lt and gt"""

    class Cohort:
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
    class Cohort:
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
    class Cohort:
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
    class Cohort:
        _filtered = (
            table("clinical_events")
            .filter(code=make_codelist(3), positive_test=True)
            .latest()
        )
        output_value = _filtered.get("test_value")

    column_definitions = get_column_definitions(Cohort)
    row = column_definitions["output_value"].source
    last_filtered_table = row.source
    assert last_filtered_table.operator == "__eq__"
    assert last_filtered_table.column == "positive_test"
    penultimate_filtered_table = last_filtered_table.source
    assert penultimate_filtered_table.operator == "__eq__"
    assert penultimate_filtered_table.column == "code"
