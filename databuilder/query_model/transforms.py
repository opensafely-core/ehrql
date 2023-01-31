"""
Apply modifications to the query graph which make it easier to work with or allow us to
generate more efficient SQL.

This involves adding new kinds of nodes to the query model. However we deliberately
define these nodes outside of the core query_model module because we're trying to
maintain separation of three types of concern:

    1. capturing the semantics of the query (which is the query model's job);
    2. worrying about expressiveness and ease of use (which is ehrQL's job);
    3. worrying about efficient execution (which is the query engines' job).

The transformations applied here are all about efficient execution, and therefore we
want to keep them separate from the core query model classes.
"""
from collections import defaultdict
from typing import Any

from databuilder.query_model.nodes import (
    Case,
    Function,
    Node,
    PickOneRowPerPatient,
    SelectColumn,
    Sort,
    Value,
    all_nodes,
    get_input_nodes,
    get_series_type,
    get_sorts,
)


class QueryGraphRewriter:
    """
    Query graphs are composed of immutable query model Node objects. This class allows
    us to modify these graphs by building up a set of replacements (node X replaces node
    A; node Y replaces node B etc) and then creating a new graph based on an existing
    one but incorporating these replacements.
    """

    def __init__(self):
        self.replacements = {}
        self.cache = {}

    def replace(self, target_node, new_node):
        self.replacements[target_node] = new_node

    def rewrite(self, obj, replacing=frozenset()):
        if isinstance(obj, Node):
            return self.rewrite_node_with_cache(obj, replacing)
        elif isinstance(obj, dict):
            # Dicts need rewriting because they may contain references to other nodes
            return {
                self.rewrite(k, replacing): self.rewrite(v, replacing)
                for k, v in obj.items()
            }
        elif isinstance(obj, frozenset):
            # As do frozensets
            return frozenset(self.rewrite(v, replacing) for v in obj)
        else:
            # Any other values in the query graph we return unchanged
            return obj

    def rewrite_node_with_cache(self, node, replacing):
        # Avoid rewriting identical sections of the graph multiple times
        new_node = self.cache.get(node)
        if new_node is None:
            new_node = self.rewrite_node(node, replacing)
            self.cache[node] = new_node
        return new_node

    def rewrite_node(self, node, replacing):
        if node in self.replacements and node not in replacing:
            # Our replacments are often insertions e.g. given the following graph:
            #
            #     A -> B -> C
            #
            # We might want to replace B with X, where X wraps B:
            #
            #     A -> X -> B -> C
            #
            # To do this we need to make sure that while we're in the process of
            # generating B's replacement we don't attempt to replace B _again_ in any
            # downstream segments of the graph. We avoid this by keeping track of which
            # nodes we're replacing at any point.
            replacing = replacing | {node}
            node = self.replacements[node]
        attrs = {k: v for k, v in node.__dict__.items() if not k.startswith("_")}
        new_attrs = self.rewrite(attrs, replacing)
        # If nothing about the node has changed then return the original rather than
        # constructing an identical replacement. This avoids unnecessarily revalidating
        # the node.
        if attrs == new_attrs:
            return node
        else:
            return type(node)(**new_attrs)


class PickOneRowPerPatientWithColumns(PickOneRowPerPatient):
    # The actual type here is `frozenset[Series]` but our type-checking code can't
    # currently handle the mixed type sets we get here (e.g. `Series[bool]` and
    # `Series[int]`). We've decided that, as this is an internal class not part of the
    # public API, it's not worth complicating the type-checking code for this use case.
    selected_columns: Any


def apply_transforms(variables):
    # Note that we're currently sharing `rewriter`, `nodes` and `reverse_index` across
    # transforms. While we only have one this is obviously fine! It _might_ be OK as we
    # add more depending on whether they're commutative but we should be careful here
    # and might decide we want to restructure things to keep the transforms independent.
    nodes = all_nodes_from_variables(variables)
    reverse_index = build_reverse_index(nodes)

    transforms = [
        (PickOneRowPerPatient, rewrite_sorts),
    ]

    rewriter = QueryGraphRewriter()
    for type_, transform in transforms:
        apply_transform(rewriter, type_, transform, nodes, reverse_index)

    return rewriter.rewrite(variables)


def apply_transform(rewriter, type_, transform, nodes, reverse_index):
    for node in nodes:
        if isinstance(node, type_):
            transform(rewriter, node, reverse_index)


def rewrite_sorts(rewriter, node, reverse_index):
    """
    Frames are sorted in order to then pick the first or last row for a patient. Multiple sorts
    may be applied to give the desired results. Once a single row has been picked, one ore more
    columns are then selected.

    This results in a subgraph of QM objects like this:

    SelectColumn(A) -+
                     |
    SelectColumn(B) -+-> PickOneRowPerPatient -> Sort(A) -> Sort(B) -> SelectTable
                     |
    SelectColumn(C) -+

    There are two transformations that we need to carry out on this stack.

    1. We annotate PickOneRowPerPatient with the columns that are going to be selected from it, in
       order to allow us to generate the appropriate query more easily.
    2. Add sorts so that we have one for each column that will be selected, in order to ensure that
       the sort order (and hence the values of the selected columns) is deterministic.

    For the example above the resulting subgraph would be:

    SelectColumn(A) -+
                     |
    SelectColumn(B) -+-> PickOneRowPerPatientWithColumns -> Sort(A) -> Sort(B) -> Sort(C) -> SelectTable
                     |
    SelectColumn(C) -+

    Some notes on the additional sorts are in order.

    * A potential lack of determinism in sort order creeps in when a patient has multiple rows with
      the same value of the column(s) being sorted on. In this case some databases may give different
      orders on different runs of the same query against the same data.
    * When this lack of determinism exists, and we select a column that has not been sorted on, the
      value returned may change between runs.
    * We add sorts only for columns that don't already have them. Duplicate sorts wouldn't cause a
      problem, but are conceptually messy and might have a small performance impact.
    * We add the sorts below the existing ones so that they have lower priority and are only used to
      break any ties in the user-specified sorts.
    * When considering the existing sorts we only attend to those that sort directly on selected
      columns, not on expressions derived from a column. Such expressions may not be injective and so
      may not be sufficient to fully determine the order. As above, duplicates are not a problem.
    * We introduce an arbitrary order for the additional sorts (lexically by column name) to ensure
      that their order itself is deterministic.
    """
    # What columns are select from this patient frame?
    selected_column_names = {
        c.name for c in reverse_index[node] if isinstance(c, SelectColumn)
    }

    add_columns_to_pick(rewriter, node, selected_column_names)
    add_extra_sorts(rewriter, node, selected_column_names)


def add_columns_to_pick(rewriter, node, selected_column_names):
    selected_columns = frozenset(
        SelectColumn(node.source, c) for c in selected_column_names
    )
    rewriter.replace(
        node,
        PickOneRowPerPatientWithColumns(
            source=node.source,
            position=node.position,
            selected_columns=selected_columns,
        ),
    )


def add_extra_sorts(rewriter, node, selected_column_names):
    all_sorts = get_sorts(node.source)
    # Add at the bottom of the stack
    lowest_sort = all_sorts[0]

    for column in calculate_sorts_to_add(all_sorts, selected_column_names):
        new_sort = Sort(
            source=lowest_sort.source,
            sort_by=make_sortable(SelectColumn(lowest_sort.source, column)),
        )
        rewriter.replace(
            lowest_sort,
            Sort(
                source=new_sort,
                sort_by=lowest_sort.sort_by,
            ),
        )
        lowest_sort = new_sort


def calculate_sorts_to_add(all_sorts, selected_column_names):
    # Don't duplicate existing direct sorts
    direct_sorts = [
        sort for sort in all_sorts if isinstance(sort.sort_by, SelectColumn)
    ]
    existing_sorted_column_names = {sort.sort_by.name for sort in direct_sorts}
    sorts_to_add = selected_column_names - existing_sorted_column_names

    # Arbitrary canonical ordering
    return sorted(sorts_to_add)


def make_sortable(col):
    if get_series_type(col) == bool:
        # Some databases can't sort booleans (including SQL Server), so we map them to integers
        return Case(
            cases={col: Value(2), Function.Not(col): Value(1)}, default=Value(0)
        )
    return col


def all_nodes_from_variables(variables):
    nodes = set()
    for query in variables.values():
        query_nodes = all_nodes(query)
        for query_node in query_nodes:
            nodes.add(query_node)
    return nodes


def build_reverse_index(nodes):
    reverse_index = defaultdict(set)
    for n in nodes:
        for i in get_input_nodes(n):
            reverse_index[i].add(n)
    return reverse_index
