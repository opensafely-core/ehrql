"""
Temporary migration code which takes a dataset definition created using the new Query Model
and outputs the equivalent using the old Query Model. This exists so we can start
developing other parts of the system using the new Query Model without first having to
rewrite the Query Engine. The intention is to refactor the Query Engine to accept
structures that look more and more like the new Query Model. Eventually they will just
*be* the new Query Model and this translation layer goes away.

Lines excluded from test coverage were exercised when we previously checked we could
convert the entire old test suite but are covered no longer.
"""
import dataclasses
from functools import cache, singledispatch

from databuilder.codes import CTV3Code

from .. import query_model as new
from . import query_model_old as old

OPERATOR_MAP = {
    new.Function.EQ: "__eq__",
    new.Function.NE: "__ne__",
    new.Function.LT: "__lt__",
    new.Function.LE: "__le__",
    new.Function.GT: "__gt__",
    new.Function.GE: "__ge__",
    new.Function.In: "in_",
}

CONNECTOR_MAP = {
    new.Function.And: "and_",
    new.Function.Or: "or_",
}

FUNCTION_CLASS_MAP = {
    new.Function.RoundToFirstOfMonth: old.RoundToFirstOfMonth,
    new.Function.RoundToFirstOfYear: old.RoundToFirstOfYear,
    new.Function.DateAdd: old.DateAddition,
    new.Function.Add: old.DateDeltaAddition,
    new.Function.DateSubtract: old.DateSubtraction,
    new.Function.Subtract: old.DateDeltaSubtraction,
    new.Function.YearFromDate: old.YearFromDate,
}

AGGREGATE_MAP = {
    new.AggregateByPatient.Exists: "exists",
    new.AggregateByPatient.Min: "min",
    new.AggregateByPatient.Max: "max",
    new.AggregateByPatient.Count: "count",
    new.AggregateByPatient.Sum: "sum",
}


def convert(new_dataset):
    old_dataset = {column: convert_node(node) for column, node in new_dataset.items()}
    convert_node.cache_clear()
    return old_dataset


def convert_value(value):
    if isinstance(value, new.Value):
        return convert_value_node(value)
    elif isinstance(value, new.Node):
        return convert_node(value)
    else:
        assert False, f"Unhandled value {value!r}"


@cache
@singledispatch
def convert_node(node):
    assert False, f"Unhandled node type {type(node)}"


def convert_value_node(node: new.Value):
    value = node.value
    if isinstance(value, frozenset):
        if any(isinstance(v, CTV3Code) for v in value):
            return convert_codelist(value)
        else:
            return tuple(value)
    else:
        return value


@convert_node.register
def convert_table(node: new.SelectTable):
    return old.Table(node.name)


@convert_node.register
def convert_patient_table(node: new.SelectPatientTable):
    return old.Row(old.Table(node.name), ("patient_id",), descending=False)


@convert_node.register
def convert_filter(node: new.Filter):
    source = convert_node(node.source)
    condition = node.condition

    or_null = False
    if isinstance(condition, new.Function.Or):
        assert isinstance(condition.rhs, new.Function.IsNull)
        assert condition.rhs.source == condition.lhs.lhs
        condition = condition.lhs
        or_null = True

    if isinstance(condition, new.Function.IsNull):  # pragma: no cover
        lhs = condition.source
        rhs = new.Value(None)
        condition = "__eq__"
    elif isinstance(condition, new.Function.Not):
        if isinstance(condition.source, new.Function.IsNull):  # pragma: no cover
            lhs = condition.source
            rhs = new.Value(None)
            operator = "__ne__"
        else:
            assert isinstance(condition.source, new.Function.In)
            lhs = condition.source.lhs
            rhs = condition.source.rhs
            operator = "not_in"
    else:
        lhs = condition.lhs
        rhs = condition.rhs
        operator = OPERATOR_MAP[condition.__class__]

    assert isinstance(lhs, new.SelectColumn)
    assert lhs.source == node.source
    column = column_name(lhs.name)

    value = convert_value(rhs)

    return old.FilteredTable(
        source=source, column=column, operator=operator, value=value, or_null=or_null
    )


@convert_node.register
def convert_select_column(node: new.SelectColumn):
    source = convert_node(node.source)
    column = column_name(node.name)
    if isinstance(source, old.Row):
        return old.ValueFromRow(source, column)
    else:
        return old.Column(source, column)


@convert_node.register
def convert_sort_and_select(node: new.PickOneRowPerPatient):
    descending = node.position == new.Position.LAST
    assert isinstance(node.source, new.Sort)
    sort_columns = []
    while isinstance(node.source, new.Sort):
        assert isinstance(node.source.sort_by, new.SelectColumn)
        sort_columns.insert(0, node.source.sort_by.name)
        node = node.source
    return old.Row(convert_node(node.source), tuple(sort_columns), descending)


@convert_node.register
def convert_combine_as_set(node: new.AggregateByPatient.CombineAsSet):
    return convert_node(node.source)


def convert_aggregation(node):
    function = AGGREGATE_MAP[node.__class__]
    if isinstance(node.source, new.Frame):
        source = new.SelectColumn(node.source, "patient_id")
    else:
        source = node.source
        assert isinstance(source, new.SelectColumn)
    source_table = convert_node(source.source)
    input_column = column_name(source.name)
    output_column = f"{input_column}_{function}"
    row = old.RowFromAggregate(source_table, function, input_column, output_column)
    return old.ValueFromAggregate(row, output_column)


for type_ in AGGREGATE_MAP.keys():
    convert_node.register(type_)(convert_aggregation)


@convert_node.register
def convert_categorise(node: new.Categorise):
    definitions = {
        convert_value(key): convert_node(value)
        for key, value in node.categories.items()
    }
    if node.default is not None:
        default = convert_value(node.default)
    else:
        default = None
    return old.ValueFromCategory(definitions, default)


def convert_function(node):
    node_class = FUNCTION_CLASS_MAP[node.__class__]
    args = [getattr(node, field.name) for field in dataclasses.fields(node)]
    args = [convert_value(arg) for arg in args]
    return node_class(*args)


for type_ in FUNCTION_CLASS_MAP.keys():
    convert_node.register(type_)(convert_function)


@convert_node.register
def convert_date_difference_in_years(node: new.Function.DateDifferenceInYears):
    return old.DateDifference(convert_value(node.lhs), convert_value(node.rhs), "years")


def convert_connector(node):
    connector = CONNECTOR_MAP[node.__class__]
    return old.Comparator(
        connector=connector, lhs=convert_value(node.lhs), rhs=convert_value(node.rhs)
    )


for type_ in CONNECTOR_MAP.keys():
    convert_node.register(type_)(convert_connector)


def convert_operator(node):
    operator = OPERATOR_MAP[node.__class__]
    return old.Comparator(
        operator=operator, lhs=convert_value(node.lhs), rhs=convert_value(node.rhs)
    )


for type_ in OPERATOR_MAP.keys():
    convert_node.register(type_)(convert_operator)


@convert_node.register
def convert_not(node: new.Function.Not):
    if hasattr(node, "source") and isinstance(node.source, new.Function.IsNull):
        return old.Comparator(
            operator="__ne__", lhs=convert_value(node.source.source), rhs=None
        )
    source = convert_node(node.source)
    assert isinstance(source, old.Comparator)
    assert not source.negated
    return old.Comparator(
        operator=source.operator,
        connector=source.connector,
        lhs=source.lhs,
        rhs=source.rhs,
        negated=True,
    )


def convert_codelist(codes):
    assert all(isinstance(c, CTV3Code) for c in codes)
    return old.Codelist(tuple(c.value for c in codes), system="ctv3")


def column_name(column):
    return column
