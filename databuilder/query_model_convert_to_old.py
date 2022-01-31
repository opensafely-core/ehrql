import dataclasses
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
    new.Function.In: "in_",
}

CONNECTOR_MAP = {
    new.Function.And: "and_",
    new.Function.Or: "or_",
}

FUNCTION_CLASS_MAP = {
    new.Function.DateDifference: old.DateDifference,
    new.Function.RoundToFirstOfMonth: old.RoundToFirstOfMonth,
    new.Function.RoundToFirstOfYear: old.RoundToFirstOfYear,
    new.Function.DateAdd: old.DateAddition,
    new.Function.Add: old.DateDeltaAddition,
    new.Function.DateSubtract: old.DateSubtraction,
    new.Function.Subtract: old.DateDeltaSubtraction,
}

AGGREGATE_MAP = {
    new.AggregateByPatient.Exists: "exists",
    new.AggregateByPatient.Min: "min",
    new.AggregateByPatient.Max: "max",
    new.AggregateByPatient.Count: "count",
    new.AggregateByPatient.Sum: "sum",
}


def convert(new_cohort):
    old_cohort = {column: convert_node(node) for column, node in new_cohort.items()}
    convert_node.cache_clear()
    return old_cohort


def convert_value(value):
    if isinstance(value, new.Node):
        return convert_node(value)
    if isinstance(value, tuple) and any(isinstance(v, new.Code) for v in value):
        return convert_codelist(value)
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

    if isinstance(condition, new.Function.IsNull):
        condition = new.Function.EQ(condition.source, None)

    if isinstance(condition, new.Function.Not):
        assert isinstance(condition.source, new.Function.In)
        condition = condition.source
        operator = "not_in"
    else:
        operator = OPERATOR_MAP[condition.__class__]

    lhs, rhs = condition.lhs, condition.rhs
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


@convert_node.register
def convert_aggregate(node: new.Aggregation):
    function = AGGREGATE_MAP[node.__class__]
    assert isinstance(node.source, new.SelectColumn)
    source_table = convert_node(node.source.source)
    input_column = column_name(node.source.name)
    output_column = f"{input_column}_{function}"
    row = old.RowFromAggregate(source_table, function, input_column, output_column)
    return old.ValueFromAggregate(row, output_column)


@convert_node.register
def convert_categorise(node: new.Categorise):
    definitions = {key: convert_node(value) for key, value in node.categories.items()}
    return old.ValueFromCategory(definitions, convert_value(node.default))


def convert_function(node):
    node_class = FUNCTION_CLASS_MAP[node.__class__]
    args = [getattr(node, field.name) for field in dataclasses.fields(node)]
    args = [convert_value(arg) for arg in args]
    return node_class(*args)


for type_ in FUNCTION_CLASS_MAP.keys():
    convert_node.register(type_)(convert_function)


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
    system = codes[0].system
    return old.Codelist(tuple(c.value for c in codes), system=system)


def column_name(column):
    # if column is new.DEFAULT_JOIN_COLUMN:
    #    return "patient_id"
    # else:
    return column
