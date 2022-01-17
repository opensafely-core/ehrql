from functools import cache, singledispatch

from . import query_model as new
from . import query_model_old as old

OPERATOR_MAP = {
    "__eq__": new.Function.EQ,
    "__ne__": new.Function.NE,
    "__lt__": new.Function.LT,
    "__le__": new.Function.LE,
    "__gt__": new.Function.GT,
    "__ge__": new.Function.GE,
    "in_": new.Function.IN,
    "not_in": new.Function.NOT_IN,
    "and_": new.Function.AND,
    "or_": new.Function.OR,
    "not_": new.Function.NOT,
    "is_null": new.Function.IS_NULL,
}


FUNCTION_CLASS_MAP = {
    old.DateDifference: new.Function.DATE_DIFFERENCE,
    old.RoundToFirstOfMonth: new.Function.ROUND_TO_FIRST_OF_MONTH,
    old.RoundToFirstOfYear: new.Function.ROUND_TO_FIRST_OF_YEAR,
    old.DateAddition: new.Function.DATE_ADD,
    old.DateDeltaAddition: new.Function.DATE_DELTA_ADD,
    old.DateSubtraction: new.Function.DATE_SUBTRACT,
    old.DateDeltaSubtraction: new.Function.DATE_DELTA_SUBTRACT,
}


def convert(old_cohort):
    new_cohort = {column: convert_node(node) for column, node in old_cohort.items()}
    convert_node.cache_clear()
    return new_cohort


def convert_value(value):
    if isinstance(value, old.QueryNode):
        return convert_node(value)
    else:
        return value


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
    value = convert_value(node.value)
    condition = new.ApplyFunction(operator, (column, value))
    if node.or_null:
        column_is_null = new.ApplyFunction(new.Function.EQ, (column, None))
        condition = new.ApplyFunction(new.Function.OR, (condition, column_is_null))
    return new.Filter(source, condition)


@convert_node.register
def convert_column(node: old.Column):
    return select_column(convert_node(node.source), node.column)


@convert_node.register
def convert_row(node: old.Row):
    source = convert_node(node.source)
    sort_columns = tuple(select_column(source, column) for column in node.sort_columns)
    return new.SortAndSelectFirst(source, sort_columns, node.descending)


@convert_node.register
def convert_value_from_row(node: old.ValueFromRow):
    return select_column(convert_node(node.source), node.column)


@convert_node.register
def convert_value_from_aggregate(node: old.ValueFromAggregate):
    old_aggregate = node.source
    assert isinstance(old_aggregate, old.RowFromAggregate)
    source = convert_node(old_aggregate.source)
    return new.Aggregate(
        new.AggregationFunction(old_aggregate.function),
        (select_column(source, old_aggregate.input_column),),
    )


@convert_node.register
def convert_value_from_category(node: old.ValueFromCategory):
    definitions = {key: convert_node(value) for key, value in node.definitions.items()}
    return new.Categorise(definitions, convert_value(node.default))


@convert_node.register
def convert_value_from_function(node: old.ValueFromFunction):
    function = FUNCTION_CLASS_MAP[type(node)]
    return new.ApplyFunction(
        function, tuple(convert_value(arg) for arg in node.arguments)
    )


@convert_node.register
def convert_comparator(node: old.Comparator):
    if node.connector is not None:
        function = OPERATOR_MAP[node.connector]
    else:
        function = OPERATOR_MAP[node.operator]
    lhs = convert_value(node.lhs)
    rhs = convert_value(node.rhs)
    result = new.ApplyFunction(function, (lhs, rhs))
    if node.negated:
        result = new.ApplyFunction(new.Function.NOT, (result,))
    return result


@convert_node.register
def convert_codelist(node: old.Codelist):
    return new.Codelist(node.codes, node.system, node.has_categories)


def select_column(table_value, column):
    if column == "patient_id":
        column = new.DEFAULT_JOIN_COLUMN
    return new.SelectColumn(table_value, column)
