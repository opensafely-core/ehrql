import dataclasses
import subprocess
import sys
from pprint import pprint
from typing import Mapping

import networkx as nx
import regraph as rg
import structlog
from regraph.utils import normalize_attrs

from databuilder.query_model import Case, all_nodes, get_input_nodes

log = structlog.getLogger()


def positive_hash(node):
    return hash(node) & sys.maxsize


def to_nx_node(node):
    def should_ignore(name, value):
        return (
            value in get_input_nodes(node)
            or (name == "schema" and isinstance(value, Mapping))
            or (isinstance(node, Case) and name == "cases")
        )

    args = [
        value
        for name, value in [
            (name, getattr(node, name))
            for name in [f.name for f in dataclasses.fields(node)]
        ]
        if not should_ignore(name, value)
    ]

    return positive_hash(node), type(node).__name__, tuple(args)


def nx_node_for_variable(name):
    if name == "population":
        return positive_hash(name), "Population", ()
    return positive_hash(name), "Variable", (name,)


def as_nx_graph(variable_definitions):
    # This is currently not an isomorphism because we throw away the attribute names (which would clutter up the
    # visual representation). It would be straightforward to add them to this encoding, though; for subnodes we could
    # decorate the edges with a "type" property and for other attributes we could store them in a dict rather than a
    # tuple. Then we'd have an isomorphism and could freely transform in either direction without losing anything.
    g = nx.DiGraph()
    for name, definition in variable_definitions.items():
        g.add_edge(nx_node_for_variable(name), to_nx_node(definition))
        for node in all_nodes(definition):
            for subnode in get_input_nodes(node):
                g.add_edge(to_nx_node(node), to_nx_node(subnode))
    return g


def is_node_type(node, *types):
    _, type_, _ = node
    return type_ in types


def is_variable_ish(node):
    return is_node_type(node, "Variable", "Population")


def is_table_ish(node):
    return is_node_type(node, "SelectTable", "SelectPatientTable")


def file_for_variable(node):
    _, type_, args = node
    if type_ == "Population":
        name = "population"
    else:
        (name,) = args
    return f"{name}.svg"


def file_for_table(node):
    _, _, args = node
    (name,) = args
    return f"{name}.svg"


def write_svg(graph, output_path):
    def truncate(s, limit):
        if len(s) <= limit:
            return s
        return s[: limit - 3] + "..."

    dot_lines = []

    def write(s, indent=0):
        dot_lines.append("\t" * indent + s + "\n")

    def write_node(node, indent):
        id_, type_, args = node

        if is_variable_ish(node):
            url_fragment = f'URL="{file_for_variable(node)}",'
        elif is_table_ish(node):
            url_fragment = f'URL="{file_for_table(node)}",'
        else:
            url_fragment = ""

        args = [truncate(str(arg), 20) for arg in args]
        style = (
            "filled, rounded"
            if is_variable_ish(node) or is_table_ish(node)
            else "rounded"
        )
        write(
            f'{id_} [label="{type_}({",".join(args)})", {url_fragment} style="{style}", shape=box]',
            indent,
        )

    def write_edge(edge, indent):
        frm, to, virtual = edge
        frm_id, _, _ = frm
        to_id, _, _ = to
        colour = "lightgrey" if virtual else "black"
        write(f"{frm_id} -> {to_id} [color={colour}]", indent)

    def partition(nodes):
        sources_, others_, sinks_ = [], [], []
        for node in nodes:
            if is_variable_ish(node):
                sources_.append(node)
            elif is_table_ish(node):
                sinks_.append(node)
            else:
                others_.append(node)
        return sources_, others_, sinks_

    sources, others, sinks = partition(graph.nodes)

    write("digraph {")

    write("{", indent=1)
    write("rank=source", indent=2)
    for source in sources:
        write_node(source, indent=2)
    write("}", indent=1)

    for other in others:
        write_node(other, indent=1)

    write("{", indent=1)
    write("rank=sink", indent=2)
    for sink in sinks:
        write_node(sink, indent=2)
    write("}", indent=1)

    for e in graph.edges.data("virtual"):
        write_edge(e, indent=1)

    write("}")

    output_file = open(output_path, mode="w")
    dot_process = subprocess.Popen(
        ["dot", "-Tsvg"], stdin=subprocess.PIPE, stdout=output_file
    )
    dot_process.communicate("".join(dot_lines).encode())
    if not dot_process.returncode == 0:
        raise Exception(f"dot failed: {dot_process.returncode}")
    log.info(f"Written {output_path}")


def render_graph(output_dir, variable_definitions):
    graph = as_nx_graph(variable_definitions)
    variables = {n for n in graph.nodes if is_variable_ish(n)}
    tables = {n for n in graph.nodes if is_table_ish(n)}

    for variable in variables:
        descendants = nx.descendants(graph, variable)
        types = mk_types(
            graph, variable=variables, source={variable}, descendant=descendants
        )
        collapsed = transform(graph, types, collapse_other_parents_of_descendants())
        marked_virtual = transform(collapsed, types, mark_other_variables_virtual())
        cleaned = remove_isolates(
            transform(marked_virtual, types, remove_unrelated_edges())
        )

        write_svg(cleaned, output_dir / file_for_variable(variable))

    for table in tables:
        ancestors = nx.ancestors(graph, table)
        table_subgraph = graph.subgraph(ancestors | {table})
        write_svg(table_subgraph, output_dir / file_for_table(table))

    types = mk_types(graph, variable=variables, table=tables)
    summary = transform(
        graph,
        types,
        link_variables_to_transitive_dependencies(),
        remove_superseded_dependency_links(),
    ).subgraph(variables | tables)
    pprint(len(summary.edges))
    for e in summary.edges:
        print(e)
    write_svg(summary, output_dir / "summary.svg")


# def test_foo():
#     g = mk_graph(
#         ("var-1", "op-1"),
#         ("op-1", "tbl-1"),
#         ("var-2", "op-2"),
#         ("op-2", "op-3"),
#         ("op-3", "op-1"),
#         ("var-3", "op-1"),
#         ("var-3", "op-4"),
#         ("op-4", "tbl-2"),
#     )
#     variables = {"var-1", "var-2", "var-3"}
#     tables = {"tbl-1", "tbl-2"}
#
#     variable_graphs = {}
#     for variable in variables:
#         descendants = nx.descendants(g, variable)
#         types = mk_types(
#             g, variable=variables, source={variable}, descendant=descendants
#         )
#         collapsed = transform(g, types, collapse_other_parents_of_descendants())
#         marked_virtual = transform(collapsed, types, mark_other_variables_virtual())
#         cleaned = removed_isolates(
#             transform(marked_virtual, types, remove_unrelated_edges())
#         )
#
#         variable_graphs[variable] = cleaned
#
#     print()
#     for v, vg in variable_graphs.items():
#         print(f"{v}: {vg.edges(data=True)}")
#         print(vg.nodes())
#
#     table_graphs = {}
#     for table in tables:
#         ancestors = nx.ancestors(g, table)
#         table_graphs[table] = g.subgraph(ancestors | {table})
#
#     for t, tg in table_graphs.items():
#         print(f"{t}: {tg.edges(data=True)}")
#         print(tg.nodes())
#
#     types = mk_types(g, variable=variables, table=tables)
#     direct = transform(g, types, link_variables_to_tables())
#     summary = direct.subgraph(variables | tables)
#     print(summary.edges())
#     print(summary.nodes())


def remove_isolates(g):
    g = g.copy()
    g.remove_nodes_from(list(nx.isolates(g)))
    return g


def collapse_other_parents_of_descendants():
    return mk_transformation(
        mk_graph(("a", "b"), ("b", "c")),
        dict(a={"variable", "none"}, b="none", c="descendant"),
        add_edge("a", "c"),
        remove_node("b"),
    )


def mark_other_variables_virtual():
    return mk_transformation(
        mk_graph(("a", "b")),
        dict(a="variable", b="descendant"),
        add_edge_attrs("a", "b", virtual=True),
    )


def remove_unrelated_edges():
    return mk_transformation(
        mk_graph(("a", "b")),
        dict(a={"variable", "none"}, b="none"),
        remove_edge("a", "b"),
    )


def link_variables_to_transitive_dependencies():
    return mk_transformation(
        mk_graph(("a", "b"), ("b", "c")),
        dict(a="variable", b="none", c={"none", "table"}),
        add_edge("a", "c"),
    )


def remove_superseded_dependency_links():
    return mk_transformation(
        mk_graph(("a", "b"), ("b", "c"), ("a", "c")),
        dict(a="variable", b="none", c={"none", "table"}),
        remove_edge("a", "b"),
    )


def mk_transformation(pattern, types, *operations):
    pattern = ng_to_rg(pattern)

    rule = rg.Rule.from_transform(pattern)
    for operation in operations:
        operation(rule)

    return pattern, types, rule


def mk_graph(*edges):
    g = nx.DiGraph()
    g.add_edges_from(edges)
    return g


def mk_types(g, **mapping):
    # Note: nodes without types match anything in the pattern; so we provide a null type, none, for nodes without types
    return {n: "none" for n in g.nodes} | {
        node: type_ for type_, nodes in mapping.items() for node in nodes
    }


def remove_node(node):
    return lambda rule: rule.inject_remove_node(node)


def add_edge(from_, to_):
    return lambda rule: rule.inject_add_edge(from_, to_)


def remove_edge(from_, to_):
    return lambda rule: rule.inject_remove_edge(from_, to_)


def add_edge_attrs(from_, to_, **attrs):
    return lambda rule: rule.inject_add_edge_attrs(from_, to_, attrs)


# def transform(graph, graph_types, transformation):
#     pattern, pattern_types, operations = transformation
#     pattern = ng_to_rg(pattern)
#
#     rule = rg.Rule.from_transform(pattern)
#     for operation in operations:
#         operation(rule)
#
#     rg_graph = ng_to_rg(graph)
#     making_changes = True
#     while making_changes:
#         making_changes = False
#         instances = rg_graph.find_matching(
#             pattern,
#             graph_typing={"g": graph_types},
#             pattern_typing={"g": pattern_types},
#         )
#
#         for instance in instances:
#             before = rg.NXGraph.copy(rg_graph)
#             rg_graph.rewrite(rule, instance)
#             if rg_graph != before:
#                 making_changes = True
#                 break  # if we've changed something other instances may be invalid, so search again
#     return rg_to_ng(rg_graph)


def transform(graph, graph_types, *transformations):
    rg_graph = ng_to_rg(graph)
    worth_retrying = True
    while worth_retrying:
        made_changes = [
            transform_all_matches(t, rg_graph, graph_types) for t in transformations
        ]
        worth_retrying = any(made_changes)
    return rg_to_ng(rg_graph)


change_counter = 0


def transform_all_matches(transformation, rg_graph, graph_types):
    made_changes = False
    for match in matches_for(transformation, rg_graph, graph_types):
        before = rg.NXGraph.copy(rg_graph)
        try:
            do_rewrite(transformation, rg_graph, match)
            changed = rg_graph != before
            if changed:
                global change_counter
                change_counter += 1
            made_changes = made_changes or changed
        except rg.GraphError:
            # Rewrites of previous instances may have invalidated this one
            pass
    return made_changes


def matches_for(transformation, rg_graph, graph_types):
    pattern, pattern_types, _ = transformation
    return rg_graph.find_matching(
        pattern,
        graph_typing={"g": graph_types},
        pattern_typing={"g": pattern_types},
    )


def do_rewrite(transformation, rg_graph, match):
    _, _, rule = transformation
    rg_graph.rewrite(rule, match)


def ng_to_rg(g):
    g = g.copy()
    for _, attrs in g.nodes(data=True):
        normalize_attrs(attrs)
    return rg.NXGraph(g)


def rg_to_ng(g):
    return g._graph.copy()
