from datetime import date

import pytest

from databuilder.query_language import (
    CategoricalConstraint,
    Dataset,
    DateDifference,
    DateEventSeries,
    DatePatientSeries,
    EventFrame,
    IntEventSeries,
    IntPatientSeries,
    PatientFrame,
    SchemaError,
    Series,
    StrEventSeries,
    StrPatientSeries,
    compile,
    days,
    months,
    table,
    years,
)
from databuilder.query_model.nodes import (
    Column,
    Function,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    TableSchema,
    TypeValidationError,
    Value,
)

patients_schema = TableSchema(date_of_birth=Column(date))
patients = PatientFrame(SelectPatientTable("patients", patients_schema))
events_schema = TableSchema(event_date=Column(date))
events = EventFrame(SelectTable("coded_events", events_schema))


def test_dataset():
    year_of_birth = patients.date_of_birth.year
    dataset = Dataset()
    dataset.set_population(year_of_birth <= 2000)
    dataset.year_of_birth = year_of_birth

    assert compile(dataset) == {
        "year_of_birth": Function.YearFromDate(
            source=SelectColumn(
                name="date_of_birth",
                source=SelectPatientTable("patients", patients_schema),
            )
        ),
        "population": Function.LE(
            lhs=Function.YearFromDate(
                source=SelectColumn(
                    name="date_of_birth",
                    source=SelectPatientTable("patients", patients_schema),
                )
            ),
            rhs=Value(2000),
        ),
    }


def test_dataset_preserves_variable_order():
    dataset = Dataset()
    dataset.set_population(patients.exists_for_patient())
    dataset.foo = patients.date_of_birth.year
    dataset.baz = patients.date_of_birth.year + 100
    dataset.bar = patients.date_of_birth.year - 100

    variables = list(compile(dataset).keys())
    assert variables == ["population", "foo", "baz", "bar"]


def test_assign_population_variable():
    dataset = Dataset()
    with pytest.raises(AttributeError, match="Cannot set column 'population'"):
        dataset.population = patients.exists_for_patient()


def test_cannot_reassign_dataset_column():
    dataset = Dataset()
    dataset.set_population(patients.exists_for_patient())
    dataset.foo = patients.date_of_birth.year
    with pytest.raises(AttributeError, match="already set"):
        dataset.foo = patients.date_of_birth.year + 100


def test_cannot_assign_frame_to_column():
    dataset = Dataset()
    dataset.set_population(patients.exists_for_patient())
    with pytest.raises(TypeError, match="Invalid column 'event_date'"):
        dataset.event_date = events.event_date


# The problem: We'd like to test that operations on query language (QL) elements return
# the correct query model (QM) elements. We like tests that emphasise what is being
# tested, and de-emphasise the scaffolding. We dislike test code that looks like
# production code.

# We'd like Series objects with specific "inner" types. How these Series objects are
# instantiated isn't important.
qm_table = SelectTable(
    name="table",
    schema=TableSchema(int_column=Column(int), date_column=Column(date)),
)
qm_int_series = SelectColumn(source=qm_table, name="int_column")
qm_date_series = SelectColumn(source=qm_table, name="date_column")


def assert_produces(ql_element, qm_element):
    assert ql_element.qm_node == qm_element


class TestIntEventSeries:
    def test_le_value(self):
        assert_produces(
            IntEventSeries(qm_int_series) <= 2000,
            Function.LE(qm_int_series, Value(2000)),
        )

    def test_le_value_reverse(self):
        assert_produces(
            2000 >= IntEventSeries(qm_int_series),
            Function.LE(qm_int_series, Value(2000)),
        )

    def test_le_intseries(self):
        assert_produces(
            IntEventSeries(qm_int_series) <= IntEventSeries(qm_int_series),
            Function.LE(qm_int_series, qm_int_series),
        )

    def test_radd(self):
        assert_produces(
            1 + IntEventSeries(qm_int_series),
            Function.Add(qm_int_series, Value(1)),
        )

    def test_rsub(self):
        assert_produces(
            1 - IntEventSeries(qm_int_series),
            Function.Add(
                Function.Negate(qm_int_series),
                Value(1),
            ),
        )


class TestDateSeries:
    def test_year(self):
        assert_produces(
            DateEventSeries(qm_date_series).year, Function.YearFromDate(qm_date_series)
        )


def test_is_in():
    int_series = IntEventSeries(qm_int_series)
    assert_produces(
        int_series.is_in([1, 2]), Function.In(qm_int_series, Value(frozenset([1, 2])))
    )


def test_passing_a_single_value_to_is_in_raises_error():
    int_series = IntEventSeries(qm_int_series)
    with pytest.raises(TypeValidationError):
        int_series.is_in(1)


def test_series_are_not_hashable():
    # The issue here is not mutability but the fact that we overload `__eq__` for
    # syntatic sugar, which makes these types spectacularly ill-behaved as dict keys
    int_series = IntEventSeries(qm_int_series)
    with pytest.raises(TypeError):
        {int_series: True}


# TEST CLASS-BASED FRAME CONSTRUCTOR
#


def test_construct_constructs_patient_frame():
    @table
    class some_table(PatientFrame):
        some_int = Series(int)
        some_str = Series(str)

    assert isinstance(some_table, PatientFrame)
    assert some_table.qm_node.name == "some_table"
    assert isinstance(some_table.some_int, IntPatientSeries)
    assert isinstance(some_table.some_str, StrPatientSeries)


def test_construct_constructs_event_frame():
    @table
    class some_table(EventFrame):
        some_int = Series(int)
        some_str = Series(str)

    assert isinstance(some_table, EventFrame)
    assert some_table.qm_node.name == "some_table"
    assert isinstance(some_table.some_int, IntEventSeries)
    assert isinstance(some_table.some_str, StrEventSeries)


def test_construct_enforces_correct_base_class():
    with pytest.raises(SchemaError, match="Schema class must subclass"):

        @table
        class some_table(Dataset):
            some_int = Series(int)


def test_construct_enforces_exactly_one_base_class():
    with pytest.raises(SchemaError, match="Schema class must subclass"):

        @table
        class some_table(PatientFrame, Dataset):
            some_int = Series(int)


def test_must_reference_instance_not_class():
    class some_table(PatientFrame):
        some_int = Series(int)

    with pytest.raises(SchemaError, match="Missing `@table` decorator"):
        some_table.some_int


def test_categories_are_passed_through_to_schema():
    @table
    class some_table(PatientFrame):
        some_str = Series(str, constraints=[CategoricalConstraint("a", "b", "c")])

    schema = some_table.qm_node.schema
    assert schema.get_column_categories("some_str") == ("a", "b", "c")


def test_boolean_operators_raise_errors():
    exists = patients.exists_for_patient()
    has_dob = patients.date_of_birth.is_not_null()
    error = "The keywords 'and', 'or', and 'not' cannot be used with ehrQL"
    with pytest.raises(TypeError, match=error):
        not exists
    with pytest.raises(TypeError, match=error):
        exists and has_dob
    with pytest.raises(TypeError, match=error):
        exists or has_dob
    with pytest.raises(TypeError, match=error):
        date(2000, 1, 1) < patients.date_of_birth < date(2020, 1, 1)


@pytest.mark.parametrize(
    "lhs,op,rhs",
    [
        (100, "+", patients.date_of_birth),
        (100, "-", patients.date_of_birth),
        (patients.date_of_birth, "+", 100),
        (patients.date_of_birth, "-", 100),
        (100, "+", days(100)),
        (100, "-", days(100)),
        (days(100), "+", 100),
        (days(100), "-", 100),
        (date(2010, 1, 1), "+", patients.date_of_birth - "2000-01-01"),
    ],
)
def test_unsupported_date_operations(lhs, op, rhs):
    with pytest.raises(TypeError, match="unsupported operand type"):
        if op == "+":
            lhs + rhs
        elif op == "-":
            lhs - rhs
        else:
            assert False


@pytest.mark.parametrize(
    "lhs,op,rhs,expected",
    [
        # Test each type of Duration constructor
        ("2020-01-01", "+", days(10), date(2020, 1, 11)),
        ("2020-01-01", "+", months(10), date(2020, 11, 1)),
        ("2020-01-01", "+", years(10), date(2030, 1, 1)),
        # Order reversed
        (days(10), "+", "2020-01-01", date(2020, 1, 11)),
        # Subtraction
        ("2020-01-01", "-", years(10), date(2010, 1, 1)),
        # Date objects rather than ISO strings
        (date(2020, 1, 1), "+", years(10), date(2030, 1, 1)),
        (years(10), "+", date(2020, 1, 1), date(2030, 1, 1)),
        (date(2020, 1, 1), "-", years(10), date(2010, 1, 1)),
    ],
)
def test_static_date_operations(lhs, op, rhs, expected):
    if op == "+":
        result = lhs + rhs
    elif op == "-":
        result = lhs - rhs
    else:
        assert False
    assert result == expected


@pytest.mark.parametrize(
    "lhs,op,rhs,expected_type",
    [
        # Test each type of Duration constructor
        (patients.date_of_birth, "+", days(10), DatePatientSeries),
        (patients.date_of_birth, "+", months(10), DatePatientSeries),
        (patients.date_of_birth, "+", years(10), DatePatientSeries),
        # Order reversed
        (days(10), "+", patients.date_of_birth, DatePatientSeries),
        # Subtraction
        (patients.date_of_birth, "-", days(10), DatePatientSeries),
        # Date differences
        (patients.date_of_birth, "-", "2020-01-01", DateDifference),
        (patients.date_of_birth, "-", date(2020, 1, 1), DateDifference),
        # Order reversed
        ("2020-01-01", "-", patients.date_of_birth, DateDifference),
        (date(2020, 1, 1), "-", patients.date_of_birth, DateDifference),
        # DateDifference attributes
        ((patients.date_of_birth - "2020-01-01").days, "+", 1, IntPatientSeries),
        ((patients.date_of_birth - "2020-01-01").months, "+", 1, IntPatientSeries),
        ((patients.date_of_birth - "2020-01-01").years, "+", 1, IntPatientSeries),
    ],
)
def test_ehrql_date_operations(lhs, op, rhs, expected_type):
    if op == "+":
        result = lhs + rhs
    elif op == "-":
        result = lhs - rhs
    else:
        assert False
    assert isinstance(result, expected_type)
