import datetime

import pytest

from ehrql import Dataset, days, maximum_of
from ehrql.codes import CTV3Code
from ehrql.dummy_data_nextgen.query_info import ColumnInfo, QueryInfo, TableInfo
from ehrql.tables import (
    Constraint,
    EventFrame,
    PatientFrame,
    Series,
    table,
    table_from_rows,
)


@table
class patients(PatientFrame):
    date_of_birth = Series(datetime.date)
    sex = Series(
        str,
        constraints=[
            Constraint.Categorical(
                ["male", "female", "intersex"],
            )
        ],
    )


@table
class events(EventFrame):
    date = Series(datetime.date)
    code = Series(CTV3Code)
    numeric_value = Series(float)


def test_query_info_from_dataset():
    dataset = Dataset()
    dataset.define_population(events.exists_for_patient())
    dataset.date_of_birth = patients.date_of_birth
    dataset.sex = patients.sex
    dataset.has_event = events.where(
        events.code == CTV3Code("abc00")
    ).exists_for_patient()

    query_info = QueryInfo.from_dataset(dataset._compile())

    assert query_info == QueryInfo(
        tables={
            "events": TableInfo(
                name="events",
                has_one_row_per_patient=False,
                columns={
                    "code": ColumnInfo(
                        name="code",
                        type=str,
                        _values_used={"abc00"},
                    )
                },
            ),
            "patients": TableInfo(
                name="patients",
                has_one_row_per_patient=True,
                columns={
                    "date_of_birth": ColumnInfo(
                        name="date_of_birth",
                        type=datetime.date,
                    ),
                    "sex": ColumnInfo(
                        name="sex",
                        type=str,
                        constraints=(
                            Constraint.Categorical(
                                values=("male", "female", "intersex")
                            ),
                        ),
                    ),
                },
            ),
        },
        population_table_names=["events"],
        other_table_names=["patients"],
    )


def test_query_info_records_values():
    @table
    class test_table(PatientFrame):
        value = Series(str)

    dataset = Dataset()
    dataset.define_population(test_table.exists_for_patient())
    dataset.q1 = (
        # NOTE: If we add examples here we should add the same examples to the inline
        # patient table test below so we can check they are correctly handled in that
        # context
        (test_table.value == "a")
        | test_table.value.is_in(["b", "c"])
        | test_table.value.contains("d")
    )

    query_info = QueryInfo.from_dataset(dataset._compile())
    column_info = query_info.tables["test_table"].columns["value"]

    assert column_info._values_used == {"a", "b", "c", "d"}


def test_query_info_ignores_inline_patient_tables():
    # InlinePatientTable nodes are unusual from the point of view of dummy data because
    # they come bundled with their own data (presumably based on dummy data generated
    # further upstream in the data processing pipeline) so we don't need to generate any
    # for them. This means that the QueryInfo class can, and should, ignore them.
    @table_from_rows([])
    class inline_table(PatientFrame):
        value = Series(str)

    dataset = Dataset()
    dataset.define_population(events.exists_for_patient())
    dataset.q1 = (
        (inline_table.value == "a")
        | inline_table.value.is_in(["b", "c"])
        | inline_table.value.contains("d")
    )

    query_info = QueryInfo.from_dataset(dataset._compile())

    assert query_info == QueryInfo(
        tables={
            "events": TableInfo(
                name="events", has_one_row_per_patient=False, columns={}
            )
        },
        population_table_names=["events"],
        other_table_names=[],
    )


def test_query_info_ignores_complex_comparisons():
    # By "complex" here we just mean anything other than a direct comparison between a
    # selected column and a static value. We don't attempt to handle these, but we want
    # to make sure we don't blow up with an error, or misinterpret them.
    dataset = Dataset()
    dataset.define_population(events.exists_for_patient())
    dataset.q1 = patients.date_of_birth.year.is_in([2000, 2010, 2020])
    dataset.q2 = patients.date_of_birth + days(100) == "2021-10-20"
    dataset.q3 = patients.date_of_birth == "2022-10-05"

    query_info = QueryInfo.from_dataset(dataset._compile())
    column_info = query_info.tables["patients"].columns["date_of_birth"]

    assert column_info.values_used == [datetime.date(2022, 10, 5)]


def test_query_info_specialize_bug():
    # This test reproduces an error encountered in real-world ehrQL which included
    # queries that specialised down to comparisons between pure values and an
    # unspecializable query involving a column, and resulted in a query with
    # no column references that hit the assertion that len(columns_for_query(result)) == 1
    dataset = Dataset()

    # We can't create `Value(False)` directly in the query language, so this is the
    # easiest way
    pure_value = maximum_of(0, 0) != 0

    # We need something which is not a pure value but which `specialize` can't currently
    # handle. This is probably the simplest option but there are lots of others. I've
    # listed a couple of others below.
    unspecializable_thing = events.count_for_patient() == 0
    # unspecializable_thing = events.sort_by(events.i).first_for_patient().i == 0
    # unspecializable_thing = events.i.count_distinct_for_patient() == 0

    # This is the core of the problematic construction. It also works with `&` instead
    # to hit the other assertion.
    query = pure_value | (pure_value & unspecializable_thing)

    dataset.define_population(query)

    # Ensure there's at least one column reference in the dataset (doesn't matter what
    # it is) so that it always tries to specialise
    dataset.dob = patients.date_of_birth
    QueryInfo.from_dataset(dataset._compile())


def test_query_info_specialize_bug_values_used():
    dataset = Dataset()

    pure_value = maximum_of(0, 0) != 0

    # Define the unspecializable thing using a column reference, so we can confirm that
    # the query info includes the expected values_used
    unspecializable_thing = (
        events.sort_by(events.date).first_for_patient().date == "2020-01-01"
    )

    query = pure_value | (pure_value & unspecializable_thing)

    dataset.define_population(query)

    query_info = QueryInfo.from_dataset(dataset._compile())
    column_info = query_info.tables["events"].columns["date"]
    assert column_info.values_used == [datetime.date(2020, 1, 1)]


def test_query_info_contains_additional_column_constraint(monkeypatch):
    dataset = Dataset()
    dataset.define_population(events.exists_for_patient())
    last_event = events.sort_by(events.date).last_for_patient()

    dataset.date = last_event.date

    dataset = Dataset()
    dataset.define_population(events.exists_for_patient())

    last_event = events.sort_by(events.date).last_for_patient()

    dataset.date = last_event.date

    monkeypatch.setattr(
        "ehrql.dummy_data_nextgen.query_info.get_dummy_data_constraints",
        lambda table_name, column_name: {
            "events": {
                "date": [Constraint.FirstOfMonth()],
            }
        }.get(table_name, {}).get(column_name, []),
    )
    query_info = QueryInfo.from_dataset(dataset._compile())
    column_info = query_info.tables["events"].columns["date"]

    assert column_info.constraints == (Constraint.FirstOfMonth(),)


@pytest.mark.parametrize(
    "generation_order,expected_order",
    [
        (
            ["numeric_value", "code", "date"],
            ["numeric_value", "code", "date"],
        ),
        (
            ["numeric_value", "date"],
            ["code", "numeric_value", "date"],
        ),
        (
            [],
            ["code", "date", "numeric_value"],  # default is alphabetical by name
        ),
    ],
)
def test_query_info_uses_specified_generation_order_if_available(
    generation_order, expected_order, monkeypatch
):
    dataset = Dataset()
    dataset.define_population(events.exists_for_patient())
    last_event = events.sort_by(events.date).last_for_patient()

    dataset.date = last_event.date
    dataset.code = last_event.code
    dataset.numeric_value = last_event.numeric_value

    monkeypatch.setattr(
        "ehrql.dummy_data_nextgen.query_info.get_dummy_data_column_generation_order",
        lambda table_name: generation_order,
    )

    query_info = QueryInfo.from_dataset(dataset._compile())
    table_info = query_info.tables["events"]
    column_names = list(table_info.columns.keys())

    assert column_names == expected_order
