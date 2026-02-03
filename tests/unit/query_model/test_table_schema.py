import datetime
import re

import pytest

from ehrql.query_model.table_schema import Column, Constraint, TableSchema
from ehrql.utils.regex_utils import RegexError


def test_table_schema_equality():
    t1 = TableSchema(i=Column(int))
    t2 = TableSchema(i=Column(int))
    t3 = TableSchema(j=Column(int))
    assert t1 == t2
    assert t1 != t3
    assert t1 != "a fish"


def test_table_schema_hash():
    t1 = TableSchema(i=Column(int))
    t2 = TableSchema(i=Column(int))
    d = {t1: "hello"}
    assert d[t2] == "hello"


def test_repr_roundtrip():
    schema = TableSchema(
        c1=Column(int),
        c2=Column(datetime.date),
    )

    assert eval(repr(schema)) == schema


def test_from_primitives():
    t1 = TableSchema.from_primitives(
        c1=int,
        c2=str,
    )
    t2 = TableSchema(
        c1=Column(int),
        c2=Column(str),
    )
    assert t1 == t2


def test_table_schema_rejects_patient_id_column():
    with pytest.raises(
        ValueError,
        match=(
            "`patient_id` is an implicitly included column on every table and"
            " must not be explicitly specified"
        ),
    ):
        TableSchema(patient_id=Column(int))


def test_get_column():
    schema = TableSchema(i=Column(int))
    assert schema.get_column("i") == Column(int)


def test_get_column_type():
    schema = TableSchema(i=Column(int))
    assert schema.get_column_type("i") is int


def test_column_names():
    schema = TableSchema(
        c1=Column(int),
        c2=Column(datetime.date),
    )
    assert schema.column_names == ["c1", "c2"]


def test_column_types():
    schema = TableSchema(
        c1=Column(int),
        c2=Column(datetime.date),
    )
    assert schema.column_types == [("c1", int), ("c2", datetime.date)]


def test_get_column_categories():
    schema = TableSchema(
        c1=Column(
            str,
            constraints=[
                Constraint.Categorical(["a", "b", "c"]),
            ],
        ),
    )
    assert schema.get_column_categories("c1") == ("a", "b", "c")


def test_get_column_categories_where_no_categories_defined():
    schema = TableSchema(c1=Column(str))
    assert schema.get_column_categories("c1") is None


def test_categorical_constraint_casts_lists_to_tuple():
    assert Constraint.Categorical([1, 2, 3]) == Constraint.Categorical((1, 2, 3))


def test_categorical_constraint_description():
    assert (
        Constraint.Categorical([1, 2, 3]).description
        == "Possible values: `1`, `2`, `3`"
    )


def test_regex_constraint_description():
    assert (
        Constraint.Regex("ABC[0-9]").description
        == "Matches regular expression: `ABC[0-9]`"
    )


def test_regex_constraint_validates_regex():
    with pytest.raises(RegexError, match="unsupported"):
        # This regex is valid but not supported by our generator code
        Constraint.Regex("(?i:TEST)")


def test_column_casts_constraint_lists_to_tuple():
    column = Column(str, constraints=[Constraint.NotNull(), Constraint.Unique()])
    assert column.constraints == (Constraint.NotNull(), Constraint.Unique())


def test_supplying_multiple_instances_of_same_constraint_raises_error():
    with pytest.raises(
        ValueError, match="'Constraint.Categorical' specified more than once"
    ):
        Column(
            int,
            constraints=[
                Constraint.Categorical([1, 2]),
                Constraint.Categorical([3, 4]),
            ],
        )


def test_supplying_dummy_data_constraint_of_same_type_as_existing_constraint_raises_error():
    with pytest.raises(
        ValueError,
        match=(
            "'Constraint.Categorical' cannot be specified as a dummy data "
            "constraint as a column constraint of the same type already exists"
        ),
    ):
        Column(
            int,
            constraints=[Constraint.Categorical([1, 2])],
            dummy_data_constraints=[Constraint.Categorical([3, 4])],
        )


def test_supplying_multiple_instances_of_same_dummy_data_constraint_raises_error():
    with pytest.raises(
        ValueError, match="'Constraint.Categorical' specified more than once"
    ):
        Column(
            int,
            dummy_data_constraints=[
                Constraint.Categorical([1, 2]),
                Constraint.Categorical([3, 4]),
            ],
        )


def test_supplying_date_after_as_a_column_constraint_raises_error():
    with pytest.raises(
        ValueError,
        match=(
            "'Constraint.DateAfter' can only be specified as a dummy data constraint."
        ),
    ):
        Column(datetime.date, constraints=[Constraint.DateAfter(["other_date"])])


def test_supplying_date_after_on_a_non_date_column_raises_error():
    with pytest.raises(
        ValueError,
        match=re.escape(
            "'Constraint.DateAfter' cannot be specified on a column with type 'int'."
        ),
    ):
        Column(int, dummy_data_constraints=[Constraint.DateAfter(["other_date"])])


def test_supplying_class_instead_of_instance_raises_error():
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Constraint should be instance not class e.g."
            " 'Constraint.NotNull()' not 'Constraint.NotNull'"
        ),
    ):
        Column(int, constraints=[Constraint.NotNull])


def test__validate_date_after_constraints():
    # Should not raise errors
    TableSchema(
        c1=Column(
            datetime.date,
            dummy_data_constraints=[Constraint.NotNull()],
        ),
        c2=Column(
            datetime.date,
            dummy_data_constraints=[Constraint.DateAfter(["c1"])],
        ),
        c3=Column(
            datetime.date,
            dummy_data_constraints=[Constraint.DateAfter(["c1", "c2"])],
        ),
    )


def test__validate_date_after_constraints_with_nonexistent_column():
    c1 = Column(
        datetime.date, dummy_data_constraints=[Constraint.DateAfter(["c2", "c3"])]
    )

    with pytest.raises(
        ValueError,
        match="Column 'c1' has a 'Constraint.DateAfter' dummy data constraint referring to non-existent column 'c3'",
    ):
        TableSchema(c1=c1, c2=Column(datetime.date))


def test__validate_date_after_constraints_with_non_date_column():
    c1 = Column(datetime.date, dummy_data_constraints=[Constraint.DateAfter(["c2"])])

    with pytest.raises(
        ValueError,
        match="Column 'c1' cannot be a date after 'c2' as 'c2' is not a date column",
    ):
        TableSchema(c1=c1, c2=Column(int))


def test__validate_date_after_constraints_with_cyclic_dependency():
    with pytest.raises(
        ValueError,
        match=(
            "Column 'c1' has a cyclic dependency in its 'Constraint.DateAfter' "
            "dummy data constraints"
        ),
    ):
        TableSchema(
            c1=Column(
                datetime.date,
                dummy_data_constraints=[Constraint.DateAfter(["c3"])],
            ),
            c2=Column(
                datetime.date,
                dummy_data_constraints=[Constraint.DateAfter(["c1"])],
            ),
            c3=Column(
                datetime.date,
                dummy_data_constraints=[Constraint.DateAfter(["c2"])],
            ),
        )


def test__validate_date_after_constraints_with_transitive_dependency():
    with pytest.raises(
        ValueError,
        match=(
            "Column 'c1' is not declared in column 'c3's 'Constraint.DateAfter', "
            "but is transitively required to be before 'c3'"
        ),
    ):
        TableSchema(
            c1=Column(datetime.date),
            c2=Column(
                datetime.date,
                dummy_data_constraints=[Constraint.DateAfter(["c1"])],
            ),
            c3=Column(
                datetime.date,
                dummy_data_constraints=[Constraint.DateAfter(["c2"])],
            ),
        )


def test__validate_date_after_constraints_with_mismatched_constraints():
    c1 = Column(
        datetime.date,
        constraints=[Constraint.GeneralRange(minimum=datetime.date(2000, 1, 1))],
        dummy_data_constraints=[Constraint.DateAfter(["c2"])],
    )
    c2 = Column(
        datetime.date,
        constraints=[Constraint.GeneralRange(minimum=datetime.date(1990, 1, 1))],
    )

    with pytest.raises(
        ValueError,
        match=(
            "Columns 'c1' and 'c2' have incompatible constraints "
            "for a 'Constraint.DateAfter' relationship"
        ),
    ):
        TableSchema(c1=c1, c2=c2)


def test_range_constraint_description():
    assert (
        Constraint.ClosedRange(0, 10, 2).description
        == "Always >= 0, <= 10, and a multiple of 2"
    )


def test_range_constraint_description_step_1():
    assert Constraint.ClosedRange(0, 10).description == "Always >= 0 and <= 10"


def test_table_schema_general_range_constraint_description():
    assert Constraint.GeneralRange(minimum=1).description == "Always >= 1"
    assert (
        Constraint.GeneralRange(minimum=1, includes_minimum=False).description
        == "Always > 1"
    )
    assert Constraint.GeneralRange(maximum=1).description == "Always <= 1"
    assert (
        Constraint.GeneralRange(maximum=1, includes_maximum=False).description
        == "Always < 1"
    )

    assert (
        Constraint.GeneralRange(minimum=1, maximum=2).description == "Always >= 1, <= 2"
    )

    assert Constraint.GeneralRange().description == "Any value"


def test_date_after_constraint_description():
    assert (
        Constraint.DateAfter(["date_1"]).description
        == "Date must be on or after the date value in column(s) date_1"
    )
    assert (
        Constraint.DateAfter(["date_1", "date_2"]).description
        == "Date must be on or after the date value in column(s) date_1, date_2"
    )
