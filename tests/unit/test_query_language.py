from datetime import date

import pytest

from databuilder.query_language import (
    Dataset,
    DateEventSeries,
    EventFrame,
    IntEventSeries,
    IntPatientSeries,
    PatientFrame,
    SchemaError,
    Series,
    StrEventSeries,
    StrPatientSeries,
    compile,
    table,
)
from databuilder.query_model import (
    Function,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    TableSchema,
    TypeValidationError,
    Value,
)

patients_schema = TableSchema(date_of_birth=date)
patients = PatientFrame(SelectPatientTable("patients", patients_schema))
events_schema = TableSchema(event_date=date)
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
    schema=TableSchema(int_column=int, date_column=date),
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
