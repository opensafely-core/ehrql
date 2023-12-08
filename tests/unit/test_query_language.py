import operator
from datetime import date
from inspect import signature

import pytest

from ehrql.codes import SNOMEDCTCode
from ehrql.file_formats import FILE_FORMATS, write_dataset
from ehrql.query_language import (
    BaseSeries,
    BoolEventSeries,
    BoolPatientSeries,
    CodePatientSeries,
    Dataset,
    DateDifference,
    DateEventSeries,
    DateFunctions,
    DatePatientSeries,
    EventFrame,
    FloatEventSeries,
    FloatPatientSeries,
    IntEventSeries,
    IntPatientSeries,
    Parameter,
    PatientFrame,
    SchemaError,
    Series,
    StrEventSeries,
    StrPatientSeries,
    compile,
    create_dataset,
    days,
    months,
    parse_date_if_str,
    table,
    table_from_file,
    table_from_rows,
    weeks,
    years,
)
from ehrql.query_model.column_specs import ColumnSpec
from ehrql.query_model.nodes import (
    Column,
    Function,
    InlinePatientTable,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    TableSchema,
    Value,
)


@table
class patients(PatientFrame):
    date_of_birth = Series(date)
    i = Series(int)
    f = Series(float)


patients_schema = TableSchema(
    date_of_birth=Column(date), i=Column(int), f=Column(float)
)


@table
class events(EventFrame):
    event_date = Series(date)
    f = Series(float)


events_schema = TableSchema(event_date=Column(date), f=Column(float))


def test_create_dataset():
    assert isinstance(create_dataset(), Dataset)


def test_dataset():
    year_of_birth = patients.date_of_birth.year
    dataset = Dataset()
    dataset.define_population(year_of_birth <= 2000)
    dataset.year_of_birth = year_of_birth
    dataset.configure_dummy_data(population_size=123)

    assert dataset.year_of_birth is year_of_birth
    assert dataset.dummy_data_config.population_size == 123

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
    dataset.define_population(patients.exists_for_patient())
    dataset.foo = patients.date_of_birth.year
    dataset.baz = patients.date_of_birth.year + 100
    dataset.bar = patients.date_of_birth.year - 100

    variables = list(compile(dataset).keys())
    assert variables == ["population", "foo", "baz", "bar"]


@pytest.mark.parametrize(
    "name",
    ["foo", "Foo", "f", "f_oo", "f1"],
)
def test_dataset_accepts_valid_variable_names(name):
    setattr(Dataset(), name, patients.i)


def test_add_column():
    dataset = Dataset()
    dataset.add_column("foo", patients.i)
    variables = list(compile(dataset).keys())
    assert variables == ["foo"]


@pytest.mark.parametrize(
    "variable_name,error",
    [
        ("population", "Cannot set variable 'population'; use define_population"),
        ("variables", "'variables' is not an allowed variable name"),
        ("patient_id", "'patient_id' is not an allowed variable name"),
        (
            "dummy_data_config",
            "'dummy_data_config' is not an allowed variable name",
        ),
        ("_something", "Variable names must start with a letter"),
        ("1something", "Variable names must start with a letter"),
        ("something!", "contain only alphanumeric characters and underscores"),
    ],
)
def test_dataset_rejects_invalid_variable_names(variable_name, error):
    with pytest.raises(AttributeError, match=error):
        setattr(Dataset(), variable_name, patients.i)


def test_cannot_define_population_more_than_once():
    dataset = Dataset()
    dataset.define_population(patients.exists_for_patient())
    with pytest.raises(AttributeError, match="no more than once"):
        dataset.define_population(patients.exists_for_patient())


def test_cannot_reassign_dataset_variable():
    dataset = Dataset()
    dataset.foo = patients.date_of_birth.year
    with pytest.raises(AttributeError, match="already set"):
        dataset.foo = patients.date_of_birth.year + 100


def test_cannot_assign_frame_to_variable():
    with pytest.raises(TypeError, match="Invalid variable 'patient'"):
        Dataset().patient = patients


def test_cannot_assign_event_series_to_variable():
    with pytest.raises(TypeError, match="Invalid variable 'event_date'"):
        Dataset().event_date = events.event_date


def test_accessing_unassigned_variable_gives_helpful_error():
    with pytest.raises(AttributeError, match="'foo' has not been defined"):
        Dataset().foo


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
    assert ql_element._qm_node == qm_element


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


@pytest.mark.parametrize(
    "lhs,op,rhs,expected_type",
    [
        (patients.f, "-", 10, FloatPatientSeries),
        (patients.f, "+", 10, FloatPatientSeries),
        (patients.f, "<", 10, BoolPatientSeries),
        (events.f, "-", 10, FloatEventSeries),
        (events.f, "<", 10, BoolEventSeries),
        (events.f, ">", 10, BoolEventSeries),
        (events.f, "<", 10.0, BoolEventSeries),
    ],
)
def test_automatic_cast(lhs, op, rhs, expected_type):
    if op == "+":
        result = lhs + rhs
    elif op == "-":
        result = lhs - rhs
    elif op == ">":
        result = lhs > rhs
    elif op == "<":
        result = lhs < rhs
    else:
        assert False
    assert isinstance(result, expected_type)


def test_is_in_rejects_unknown_types():
    with pytest.raises(TypeError, match="Invalid argument type"):
        patients.i.is_in(1)


def test_is_in_rejects_patient_series():
    with pytest.raises(TypeError, match="must be an EventSeries"):
        events.f.is_in(patients.f)


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
    assert some_table._qm_node.name == "some_table"
    assert isinstance(some_table.some_int, IntPatientSeries)
    assert isinstance(some_table.some_str, StrPatientSeries)


def test_construct_constructs_event_frame():
    @table
    class some_table(EventFrame):
        some_int = Series(int)
        some_str = Series(str)

    assert isinstance(some_table, EventFrame)
    assert some_table._qm_node.name == "some_table"
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


def test_table_from_rows():
    @table_from_rows([(1, 100), (2, 200)])
    class some_table(PatientFrame):
        some_int = Series(int)

    assert isinstance(some_table, PatientFrame)
    assert isinstance(some_table._qm_node, InlinePatientTable)


def test_table_from_rows_only_accepts_patient_frame():
    with pytest.raises(
        SchemaError, match="`@table_from_rows` can only be used with `PatientFrame`"
    ):

        @table_from_rows([])
        class some_table(EventFrame):
            some_int = Series(int)


@pytest.mark.parametrize("file_extension", FILE_FORMATS)
def test_table_from_file(file_extension, tmp_path):
    file_data = [
        (1, 100, "a", date(2021, 1, 1)),
        (2, 200, "b", date(2022, 2, 2)),
    ]
    filename = tmp_path / f"test_file{file_extension}"

    column_specs = {
        "patient_id": ColumnSpec(int),
        "i": ColumnSpec(int),
        "s": ColumnSpec(str),
        "d": ColumnSpec(date),
    }
    write_dataset(filename, file_data, column_specs)

    @table_from_file(filename)
    class some_table(PatientFrame):
        i = Series(int)
        s = Series(str)
        d = Series(date)

    assert isinstance(some_table, PatientFrame)
    assert isinstance(some_table._qm_node, InlinePatientTable)
    assert some_table._qm_node.schema.column_types == [
        ("i", int),
        ("s", str),
        ("d", date),
    ]
    assert list(some_table._qm_node.rows) == file_data


def test_table_from_file_only_accepts_patient_frame():
    with pytest.raises(
        SchemaError,
        match="`@table_from_file` can only be used with `PatientFrame`",
    ):

        @table_from_file("")
        class some_table(EventFrame):
            some_int = Series(int)


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
        (100, operator.add, patients.date_of_birth),
        (100, operator.sub, patients.date_of_birth),
        (patients.date_of_birth, operator.add, 100),
        (patients.date_of_birth, operator.sub, 100),
        (100, operator.add, days(100)),
        (100, operator.sub, days(100)),
        (days(100), operator.add, 100),
        (days(100), operator.sub, 100),
        (date(2010, 1, 1), operator.add, patients.date_of_birth - "2000-01-01"),
    ],
)
def test_unsupported_date_operations(lhs, op, rhs):
    with pytest.raises(TypeError, match="unsupported operand type"):
        op(lhs, rhs)


@pytest.mark.parametrize(
    "lhs,op,rhs,expected",
    [
        # Test each type of Duration constructor
        ("2020-01-01", operator.add, days(10), date(2020, 1, 11)),
        ("2020-01-01", operator.add, weeks(1), date(2020, 1, 8)),
        ("2020-01-01", operator.add, months(10), date(2020, 11, 1)),
        ("2020-01-01", operator.add, years(10), date(2030, 1, 1)),
        # Order reversed
        (days(10), operator.add, "2020-01-01", date(2020, 1, 11)),
        # Subtraction
        ("2020-01-01", operator.sub, years(10), date(2010, 1, 1)),
        # Date objects rather than ISO strings
        (date(2020, 1, 1), operator.add, years(10), date(2030, 1, 1)),
        (years(10), operator.add, date(2020, 1, 1), date(2030, 1, 1)),
        (date(2020, 1, 1), operator.sub, years(10), date(2010, 1, 1)),
        # Test addition of Durations
        (days(10), operator.add, days(5), days(15)),
        (weeks(10), operator.add, weeks(5), weeks(15)),
        (months(10), operator.add, months(5), months(15)),
        (years(10), operator.add, years(5), years(15)),
        # Test subtraction of Durations
        (days(10), operator.sub, days(5), days(5)),
        (weeks(10), operator.sub, weeks(5), weeks(5)),
        (months(10), operator.sub, months(5), months(5)),
        (years(10), operator.sub, years(5), years(5)),
        # Test comparison of Durations
        (days(5), operator.eq, days(5), True),
        (months(5), operator.eq, years(5), False),
        (weeks(5), operator.eq, weeks(4), False),
        (weeks(1), operator.eq, days(7), False),
        (days(5), operator.ne, days(5), False),
        (months(5), operator.ne, years(5), True),
    ],
)
def test_static_date_operations(lhs, op, rhs, expected):
    assert op(lhs, rhs) == expected


@pytest.mark.parametrize(
    "lhs,op,rhs,expected_type",
    [
        # Test each type of Duration constructor
        (patients.date_of_birth, operator.add, days(10), DatePatientSeries),
        (patients.date_of_birth, operator.add, weeks(10), DatePatientSeries),
        (patients.date_of_birth, operator.add, months(10), DatePatientSeries),
        (patients.date_of_birth, operator.add, years(10), DatePatientSeries),
        # Order reversed
        (days(10), operator.add, patients.date_of_birth, DatePatientSeries),
        # Subtraction
        (patients.date_of_birth, operator.sub, days(10), DatePatientSeries),
        # Date differences
        (patients.date_of_birth, operator.sub, "2020-01-01", DateDifference),
        (patients.date_of_birth, operator.sub, date(2020, 1, 1), DateDifference),
        # Order reversed
        ("2020-01-01", operator.sub, patients.date_of_birth, DateDifference),
        (date(2020, 1, 1), operator.sub, patients.date_of_birth, DateDifference),
        # DateDifference attributes
        (
            (patients.date_of_birth - "2020-01-01").days,
            operator.add,
            1,
            IntPatientSeries,
        ),
        (
            (patients.date_of_birth - "2020-01-01").weeks,
            operator.add,
            1,
            IntPatientSeries,
        ),
        (
            (patients.date_of_birth - "2020-01-01").months,
            operator.add,
            1,
            IntPatientSeries,
        ),
        (
            (patients.date_of_birth - "2020-01-01").years,
            operator.add,
            1,
            IntPatientSeries,
        ),
        # Test with a "dynamic" duration
        (patients.date_of_birth, operator.add, days(patients.i), DatePatientSeries),
        (patients.date_of_birth, operator.add, weeks(patients.i), DatePatientSeries),
        (patients.date_of_birth, operator.add, months(patients.i), DatePatientSeries),
        (patients.date_of_birth, operator.add, years(patients.i), DatePatientSeries),
        # Test with a dynamic duration and a static date
        (date(2020, 1, 1), operator.add, days(patients.i), DatePatientSeries),
        (date(2020, 1, 1), operator.add, weeks(patients.i), DatePatientSeries),
        (date(2020, 1, 1), operator.add, months(patients.i), DatePatientSeries),
        (date(2020, 1, 1), operator.add, years(patients.i), DatePatientSeries),
        # Test comparison of Durations
        (days(patients.i), operator.eq, days(patients.i), BoolPatientSeries),
        (months(patients.i), operator.eq, years(patients.i), bool),
        (days(patients.i), operator.ne, days(patients.i), BoolPatientSeries),
        (months(patients.i), operator.ne, years(patients.i), bool),
    ],
)
def test_ehrql_date_operations(lhs, op, rhs, expected_type):
    assert isinstance(op(lhs, rhs), expected_type)


@pytest.mark.parametrize(
    "lhs,op,rhs",
    [
        (days(10), operator.add, months(10)),
        (days(10), operator.sub, months(10)),
        (days(10), operator.add, years(10)),
        (days(10), operator.sub, years(10)),
        (months(10), operator.add, years(10)),
        (months(10), operator.sub, years(10)),
    ],
)
def test_incompatible_duration_operations(lhs, op, rhs):
    with pytest.raises(TypeError):
        op(lhs, rhs)


fn_names = sorted(
    (
        {k for k, v in DateFunctions.__dict__.items() if callable(v)}
        | {
            k
            for k, v in BaseSeries.__dict__.items()
            # exclude dunder methods as lots inherited from dataclass
            # which don't fit the test pattern below
            if callable(v) and not k.startswith("__")
        }
    )
    # Exclude methods which don't return an ehrQL series
    - {
        "__add__",
        "__sub__",
        "__radd__",
        "__rsub__",
        "_cast",
    },
)


@pytest.mark.parametrize("fn_name", fn_names)
def test_ehrql_date_string_equivalence(fn_name):
    @table
    class p(PatientFrame):
        d = Series(date)

    f = getattr(p.d, fn_name)
    n_params = len(signature(f).parameters)
    date_args = [date(2000, 1, 1) for i in range(n_params)]
    str_args = ["2000-01-01" for i in range(n_params)]

    if fn_name == "map_values":
        date_args = {d: "a" for d in date_args}
        str_args = {s: "a" for s in str_args}

    # avoid over-unpacking iterable params
    if fn_name in ["is_in", "is_not_in", "map_values"]:
        date_args = [date_args]
        str_args = [str_args]
    if fn_name == "is_during":
        date_args = [(date_args[0], date_args[0])]
        str_args = [(str_args[0], str_args[0])]

    assert f(*date_args)._qm_node == f(*str_args)._qm_node


def test_code_series_instances_have_correct_type_attribute():
    @table
    class p(PatientFrame):
        code = Series(SNOMEDCTCode)

    # The series itself is a generic "BaseCode" series
    assert isinstance(p.code, CodePatientSeries)
    # But it knows the specfic coding system type it wraps
    assert p.code._type is SNOMEDCTCode


def test_strings_are_cast_to_codes():
    @table
    class p(PatientFrame):
        code = Series(SNOMEDCTCode)

    eq_series = p.code == "123000"
    assert eq_series._qm_node.rhs == Value(SNOMEDCTCode("123000"))

    is_in_series = p.code.is_in(["456000", "789000"])
    assert is_in_series._qm_node.rhs == Value(
        frozenset({SNOMEDCTCode("456000"), SNOMEDCTCode("789000")})
    )

    mapping = {"456000": "foo", "789000": "bar"}
    mapped_series = p.code.is_in(mapping)
    assert mapped_series._qm_node.rhs == Value(
        frozenset({SNOMEDCTCode("456000"), SNOMEDCTCode("789000")})
    )

    # Test invalid codes are rejected
    with pytest.raises(ValueError, match="Invalid SNOMEDCTCode"):
        p.code == "abc"


def test_frame_classes_are_preserved():
    @table
    class e(EventFrame):
        start_date = Series(date)

        def after_2020(self):
            return self.where(self.start_date > "2020-01-01")

    # Check that the helper method is preserved through `where`
    filtered_frame = e.where(e.start_date > "1990-01-01")
    assert isinstance(filtered_frame.after_2020(), EventFrame)

    # Check that the helper method is preserved through `sort_by`
    sorted_frame = e.sort_by(e.start_date)
    assert isinstance(sorted_frame.after_2020(), EventFrame)

    # Check that helper method is not available on patient frame
    latest_event = sorted_frame.last_for_patient()
    assert not hasattr(latest_event, "after_2020")

    # Check that column is still available. We're using `dir()` here to confirm that the
    # column is explicitly defined on the object and is available as an auto-complete
    # suggestion. Using `hasattr()` wouldn't tell us whether the attribute was only
    # available via a magic `__getattr__` method.
    assert "start_date" in dir(latest_event)


@pytest.mark.parametrize(
    "value,expected",
    [
        # Strings are parsed as dates
        ("2021-03-04", date(2021, 3, 4)),
        # Other types are passed through
        (1.23, 1.23),
        (b"abc", b"abc"),
    ],
)
def test_parse_date_if_str(value, expected):
    assert parse_date_if_str(value) == expected


@pytest.mark.parametrize(
    "value,error",
    [
        ("1st March 2020", "Invalid isoformat string: '1st March 2020'"),
        ("2021-02-29", "day is out of range for month in '2021-02-29'"),
    ],
)
def test_parse_date_if_str_errors(value, error):
    with pytest.raises(ValueError, match=error):
        parse_date_if_str(value)


def test_parameter():
    series = Parameter("test_param", date)
    assert isinstance(series, DatePatientSeries)


# The behaviour of `date_utils.generate_intervals` is covered more fully by its own unit
# tests, we just need to test enough below to confirm that it's wired up correctly.


@pytest.mark.parametrize(
    "constructor,value,start_date,expected",
    [
        (
            weeks,
            1,
            "2020-01-01",
            [(date(2020, 1, 1), date(2020, 1, 7))],
        ),
        (
            months,
            1,
            "2020-01-01",
            [(date(2020, 1, 1), date(2020, 1, 31))],
        ),
        (
            years,
            1,
            "2020-01-01",
            [(date(2020, 1, 1), date(2020, 12, 31))],
        ),
    ],
)
def test_duration_starting_on(constructor, value, start_date, expected):
    assert constructor(value).starting_on(start_date) == expected


def test_duration_ending_on():
    assert months(3).ending_on("2020-06-30") == [
        (date(2020, 3, 31), date(2020, 4, 30)),
        (date(2020, 5, 1), date(2020, 5, 30)),
        (date(2020, 5, 31), date(2020, 6, 30)),
    ]


@pytest.mark.parametrize(
    "value,start_date,error",
    [
        (
            patients.i,
            "2020-01-01",
            r"weeks\.starting_on\(\) can only be used with a literal integer value, not an integer series",
        ),
        (
            10,
            patients.date_of_birth,
            r"weeks\.starting_on\(\) can only be used with a literal date, not a date series",
        ),
        (
            -10,
            "2020-01-01",
            r"weeks\.starting_on\(\) can only be used with positive numbers",
        ),
    ],
)
def test_duration_generate_intervals_rejects_invalid_arguments(
    value, start_date, error
):
    with pytest.raises((TypeError, ValueError), match=error):
        weeks(value).starting_on(start_date)


@pytest.mark.parametrize(
    "maximum_gap,error",
    [
        (10, r"must be supplied as `days\(\)` or `weeks\(\)`"),
        (patients.i, r"must be supplied as `days\(\)` or `weeks\(\)`"),
        (months(2), r"must be supplied as `days\(\)` or `weeks\(\)`"),
        (years(2), r"must be supplied as `days\(\)` or `weeks\(\)`"),
        (days(patients.i), "must be a single, fixed number of days"),
        (weeks(patients.i), "must be a single, fixed number of weeks"),
    ],
)
def test_count_episodes_for_patient_rejects_invalid_arguments(maximum_gap, error):
    with pytest.raises((TypeError, ValueError), match=error):
        events.event_date.count_episodes_for_patient(maximum_gap)


def test_count_episodes_for_patient_handles_weeks():
    using_days = events.event_date.count_episodes_for_patient(days(14))
    using_weeks = events.event_date.count_episodes_for_patient(weeks(2))
    assert using_days._qm_node == using_weeks._qm_node
