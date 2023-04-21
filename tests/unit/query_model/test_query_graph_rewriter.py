from ehrql.query_model.nodes import (
    Case,
    Column,
    Filter,
    Function,
    SelectColumn,
    SelectTable,
    TableSchema,
    Value,
)
from ehrql.query_model.query_graph_rewriter import QueryGraphRewriter


def test_query_graph_rewriter():
    # Construct a query graph with a chain of filters
    events = SelectTable("events", schema=TableSchema(i=Column(int)))
    col_i = SelectColumn(events, "i")
    filter_10 = Filter(events, condition=Function.GT(col_i, Value(10)))
    filter_20 = Filter(filter_10, condition=Function.GT(col_i, Value(20)))
    filter_30 = Filter(filter_20, condition=Function.GT(col_i, Value(30)))

    graph = {"value": filter_30}

    # Inject a new filter between 20 and 30
    filter_25 = Filter(filter_20, condition=Function.GT(col_i, Value(25)))
    rewriter = QueryGraphRewriter()
    rewriter.replace(filter_20, filter_25)

    # Rewrite the graph
    new_graph = rewriter.rewrite(graph)
    assert new_graph == {
        "value": Filter(filter_25, condition=Function.GT(col_i, Value(30)))
    }


def test_query_graph_rewriter_handles_nodes_in_frozensets():
    events = SelectTable("events", schema=TableSchema(i=Column(int)))
    col_i = SelectColumn(events, "i")
    filter_1 = Filter(events, condition=Function.GT(col_i, Value(1)))
    filter_2 = Filter(events, condition=Function.GT(col_i, Value(2)))
    graph = {"filters": frozenset([filter_1, filter_2])}

    filter_3 = Filter(events, condition=Function.GT(col_i, Value(3)))
    rewriter = QueryGraphRewriter()
    rewriter.replace(filter_1, filter_3)

    new_graph = rewriter.rewrite(graph)
    assert new_graph == {"filters": frozenset([filter_3, filter_2])}


def test_query_graph_rewriter_handles_case_without_default():
    events = SelectTable("events", schema=TableSchema(i=Column(int)))
    col_i = SelectColumn(events, "i")
    is_positive = Function.GE(col_i, Value(0))
    is_negative = Function.LT(col_i, Value(0))

    graph = {
        "case": Case({is_positive: Value("valid")}, default=None),
    }

    rewriter = QueryGraphRewriter()
    rewriter.replace(is_positive, is_negative)

    new_graph = rewriter.rewrite(graph)
    assert new_graph == {
        "case": Case({is_negative: Value("valid")}, default=None),
    }


def test_query_graph_rewriter_handles_replacing_node_with_value():
    # The bug this exposes was only triggered when we had more than one replacement, so
    # we need two columns
    events = SelectTable("events", schema=TableSchema(i=Column(int), s=Column(str)))
    col_i = SelectColumn(events, "i")
    col_s = SelectColumn(events, "s")
    graph = {"i": col_i, "s": col_s}

    rewriter = QueryGraphRewriter()
    rewriter.replace(col_i, Value(10))
    rewriter.replace(col_s, Value("a"))
    new_graph = rewriter.rewrite(graph)

    assert new_graph == {"i": Value(10), "s": Value("a")}
