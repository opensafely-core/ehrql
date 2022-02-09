"""
Temporary migration code which takes a dataset definition created using the old Query Model
and outputs the equivalent using the new Query Model.

Lines excluded from test coverage were exercised when we previously checked we could
convert the entire old test suite but are covered no longer.
"""
import datetime
import re
from functools import cache, singledispatch

from databuilder import query_model as new

from . import query_model_old as old

DATE_RE = re.compile(r"^\d\d\d\d-\d\d-\d\d$")

OPERATOR_MAP = {
    "__eq__": new.Function.EQ,
    "__ne__": new.Function.NE,
    "__lt__": new.Function.LT,
    "__le__": new.Function.LE,
    "__gt__": new.Function.GT,
    "__ge__": new.Function.GE,
    "in_": new.Function.In,
    "not_in": lambda lhs, rhs: new.Function.Not(new.Function.In(lhs, rhs)),
    "and_": new.Function.And,
    "or_": new.Function.Or,
    "not_": new.Function.Not,
}


FUNCTION_CLASS_MAP = {
    old.DateDifference: new.Function.DateDifference,
    old.RoundToFirstOfMonth: new.Function.RoundToFirstOfMonth,
    old.RoundToFirstOfYear: new.Function.RoundToFirstOfYear,
    old.DateAddition: new.Function.DateAdd,
    old.DateDeltaAddition: new.Function.Add,
    old.DateSubtraction: new.Function.DateSubtract,
    old.DateDeltaSubtraction: new.Function.Subtract,
}


AGGREGATE_MAP = {
    "exists": new.AggregateByPatient.Exists,
    "min": new.AggregateByPatient.Min,
    "max": new.AggregateByPatient.Max,
    "count": new.AggregateByPatient.Count,
    "sum": new.AggregateByPatient.Sum,
}


def convert(old_cohort):
    new_cohort = {column: convert_node(node) for column, node in old_cohort.items()}
    convert_node.cache_clear()
    return new_cohort


def convert_value(value):
    if isinstance(value, old.QueryNode):
        return convert_node(value)
    else:
        if isinstance(value, tuple):
            value = frozenset(value)
        if isinstance(value, str) and DATE_RE.match(value):
            value = datetime.date.fromisoformat(value)
        return new.Value(value)


@cache
@singledispatch
def convert_node(node):
    assert False, f"Unhandled node type {type(node)}"


@convert_node.register
def convert_table(node: old.Table):
    return new.SelectTable(node.name)


@convert_node.register
def convert_filtered_table(node: old.FilteredTable):
    source = convert_node(node.source)
    column = select_column(source, node.column)
    operator = OPERATOR_MAP[node.operator]
    if node.operator in ("in_", "not_in") and isinstance(node.value, old.Column):
        value = new.AggregateByPatient.CombineAsSet(convert_node(node.value))
    else:
        value = convert_value(node.value)
    if node.operator == "__eq__" and node.value is None:  # pragma: no cover
        condition = new.Function.IsNull(column)
    elif node.operator == "__ne__" and node.value is None:  # pragma: no cover
        condition = new.Function.Not(new.Function.IsNull(column))
    else:
        condition = operator(column, value)
    if node.or_null:
        column_is_null = new.Function.IsNull(column)
        condition = new.Function.Or(condition, column_is_null)
    return new.Filter(source, condition)


@convert_node.register
def convert_column(node: old.Column):
    return select_column(convert_node(node.source), node.column)


@convert_node.register
def convert_row(node: old.Row):
    if node.sort_columns == ("patient_id",):
        if isinstance(node.source, old.Table) and node.source.name == "patients":
            return new.SelectPatientTable(node.source.name)
    source = convert_node(node.source)
    sort_columns = [select_column(source, column) for column in node.sort_columns]
    for column in sort_columns:
        source = new.Sort(source, column)
    position = new.Position.LAST if node.descending else new.Position.FIRST
    return new.PickOneRowPerPatient(source, position)


@convert_node.register
def convert_value_from_row(node: old.ValueFromRow):
    return select_column(convert_node(node.source), node.column)


@convert_node.register
def convert_value_from_aggregate(node: old.ValueFromAggregate):
    old_aggregate = node.source
    assert isinstance(old_aggregate, old.RowFromAggregate)
    source = convert_node(old_aggregate.source)
    column = select_column(source, old_aggregate.input_column)
    Aggregation = AGGREGATE_MAP[old_aggregate.function]
    return Aggregation(column)


@convert_node.register
def convert_value_from_category(node: old.ValueFromCategory):
    definitions = {
        convert_value(key): convert_node(value)
        for key, value in node.definitions.items()
    }
    if node.default is not None:
        default = convert_value(node.default)
    else:
        default = None
    return new.Categorise(definitions, default)


@convert_node.register
def convert_value_from_function(node: old.ValueFromFunction):
    Function = FUNCTION_CLASS_MAP[type(node)]
    return Function(*[convert_value(arg) for arg in node.arguments])


@convert_node.register
def convert_comparator(node: old.Comparator):
    if node.connector is not None:
        Function = OPERATOR_MAP[node.connector]
    else:
        Function = OPERATOR_MAP[node.operator]
    if node.operator == "__eq__" and node.rhs is None:  # pragma: no cover
        result = new.Function.IsNull(convert_value(node.lhs))
    if node.operator == "__ne__" and node.rhs is None:
        result = new.Function.Not(new.Function.IsNull(convert_value(node.lhs)))
    else:
        lhs = convert_value(node.lhs)
        rhs = convert_value(node.rhs)
        result = Function(lhs, rhs)
    if node.negated:
        result = new.Function.Not(result)
    return result


@convert_node.register
def convert_codelist(node: old.Codelist):
    assert not node.has_categories
    code_set = frozenset(new.Code(code, system=node.system) for code in node.codes)
    return new.Value(code_set)


def select_column(table_value, column):
    return new.SelectColumn(table_value, column)
