# This is throwaway code, but it may be useful in future and keeping it in the repo
# ensures that it is tested and will continue to run as the project evolves.  However,
# if maintaining it proves burdensome, it should be removed.

import dataclasses

import networkx as nx
import pydot

from ehrql.query_model import nodes


def graph_to_svg(variable_definitions, output_path):  # pragma: no cover
    graph = build_graph(variable_definitions)
    graph.write_svg(output_path)


def build_graph(variable_definitions):
    G = nx.DiGraph()
    for name, node in variable_definitions.items():
        G.add_node(name)
        G.add_node(get_id(node), label=get_label(node))
        G.add_edge(name, get_id(node))
        for src, type_, dst in find_edges(node):
            G.add_node(get_id(src), label=get_label(src))
            G.add_node(get_id(dst), label=get_label(dst))
            G.add_edge(get_id(src), get_id(dst), label=type_)

    # Ensure that all variables line up at the top of the graph
    P = nx.nx_pydot.to_pydot(G)
    cluster = pydot.Cluster(rank="min", style="invis")
    for name in variable_definitions:
        cluster.add_node(pydot.Node(get_id(name)))
    P.add_subgraph(cluster)

    return P


def find_edges(src):
    for f in dataclasses.fields(src):
        dst = getattr(src, f.name)
        if isinstance(dst, nodes.TableSchema):
            continue
        yield (src, f.name, dst)
        if isinstance(dst, nodes.Value):
            continue
        if not dataclasses.is_dataclass(dst):
            continue
        yield from find_edges(dst)


def get_id(node):
    if dataclasses.is_dataclass(node):
        return id(node)
    else:
        # Sometimes primitive values are not interned, which means eg two strings with
        # the same content can have different ids
        return node


def get_label(node):
    if isinstance(node, nodes.Value):
        return node.value
    elif dataclasses.is_dataclass(node):
        return f"{type(node).__qualname__}"
    else:
        return node
