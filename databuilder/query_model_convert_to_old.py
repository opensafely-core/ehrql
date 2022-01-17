from functools import cache, singledispatch

from . import query_model as new
from . import query_model_old as old

OPERATOR_MAP = {
    new.Function.EQ: "__eq__",
    new.Function.NE: "__ne__",
    new.Function.LT: "__lt__",
    new.Function.LE: "__le__",
    new.Function.GT: "__gt__",
    new.Function.GE: "__ge__",
    new.Function.IN: "in_",
    new.Function.NOT_IN: "not_in",
    new.Function.NOT: "not_",
    new.Function.IS_NULL: "is_null",
}

CONNECTOR_MAP = {
    new.Function.AND: "and_",
    new.Function.OR: "or_",
}

FUNCTION_CLASS_MAP = {
    new.Function.DATE_DIFFERENCE: old.DateDifference,
    new.Function.ROUND_TO_FIRST_OF_MONTH: old.RoundToFirstOfMonth,
    new.Function.ROUND_TO_FIRST_OF_YEAR: old.RoundToFirstOfYear,
    new.Function.DATE_ADD: old.DateAddition,
    new.Function.DATE_DELTA_ADD: old.DateDeltaAddition,
    new.Function.DATE_SUBTRACT: old.DateSubtraction,
    new.Function.DATE_DELTA_SUBTRACT: old.DateDeltaSubtraction,
}


def convert(new_cohort):
    old_cohort = {column: convert_node(node) for column, node in new_cohort.items()}
    convert_node.cache_clear()
    return old_cohort


def convert_value(value):
    if isinstance(value, new.QueryNode):
        return convert_node(value)
    else:
        return value


@cache
@singledispatch
def convert_node(node):
    assert False, f"Unhandled node type {type(node)}"


@convert_node.register
def convert_table(node: new.SelectTable):
    return old.Table(node.name)


@convert_node.register
def convert_filter(node: new.Filter):
    source = convert_node(node.source)
    condition = node.condition

    or_null = False
    if condition.function == new.Function.OR:
        lhs, rhs = condition.arguments
        assert isinstance(lhs, new.ApplyFunction)
        assert isinstance(rhs, new.ApplyFunction)
        column_is_null = new.ApplyFunction(new.Function.EQ, (lhs.arguments[0], None))
        assert rhs == column_is_null

        condition = lhs
        or_null = True

    assert condition.function in OPERATOR_MAP
    operator = OPERATOR_MAP[condition.function]

    lhs, rhs = condition.arguments
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
def convert_sort_and_select(node: new.SortAndSelectFirst):
    sort_columns = []
    for column in node.sort_columns:
        assert isinstance(column, new.SelectColumn)
        assert column.source == node.source
        sort_columns.append(column_name(column.name))
    return old.Row(convert_node(node.source), tuple(sort_columns), node.descending)


@convert_node.register
def convert_aggregate(node: new.Aggregate):
    function = node.function.value
    assert len(node.arguments) == 1
    source_column = node.arguments[0]
    assert isinstance(source_column, new.SelectColumn)
    source_table = convert_node(source_column.source)
    input_column = column_name(source_column.name)
    output_column = f"{input_column}_{function}"
    row = old.RowFromAggregate(source_table, function, input_column, output_column)
    return old.ValueFromAggregate(row, output_column)


@convert_node.register
def convert_categorise(node: new.Categorise):
    definitions = {key: convert_node(value) for key, value in node.categories.items()}
    return old.ValueFromCategory(definitions, convert_value(node.default))


@convert_node.register
def convert_apply_function(node: new.ApplyFunction):
    negated = False
    if node.function == new.Function.NOT:
        assert len(node.arguments) == 1
        node = node.arguments[0]
        negated = True

    arguments = tuple(convert_value(arg) for arg in node.arguments)

    if node.function in CONNECTOR_MAP:
        connector = CONNECTOR_MAP[node.function]
        assert len(arguments) == 2
        return old.Comparator(
            connector=connector, lhs=arguments[0], rhs=arguments[1], negated=negated
        )
    elif node.function in OPERATOR_MAP:
        operator = OPERATOR_MAP[node.function]
        assert len(arguments) == 2
        return old.Comparator(
            operator=operator, lhs=arguments[0], rhs=arguments[1], negated=negated
        )
    else:
        assert not negated
        node_class = FUNCTION_CLASS_MAP[node.function]
        return node_class(*arguments)


@convert_node.register
def convert_codelist(node: new.Codelist):
    return old.Codelist(node.codes, node.system, node.has_categories)


def column_name(column):
    if column is new.DEFAULT_JOIN_COLUMN:
        return "patient_id"
    else:
        return column
