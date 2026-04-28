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
from collections.abc import Mapping, Set
from typing import Any, TypeVar

from ehrql.query_model.introspection import all_unique_nodes
from ehrql.query_model.nodes import (
    Case,
    Function,
    Parameter,
    PickOneRowPerPatient,
    SelectColumn,
    Series,
    Sort,
    Value,
    get_input_nodes,
    get_series_type,
    get_sorts,
    has_one_row_per_patient,
)
from ehrql.query_model.query_graph_rewriter import QueryGraphRewriter


T = TypeVar("T")
U = TypeVar("U")


# Records all the columns which get selected from a PickOneRowPerPatient node during a
# particular query. This allows us to generate more efficient SQL queries in a couple of
# different ways:
#
# 1. We end up materializing these sort-and-pick queries into temporary tables and we
#    don't want to do this for more columns than we actually need.
#
# 2. In order to achieve stable, database-independent sort behaviour we inject extra
#    sort conditions alongside the user-supplied ones and we don't want to do this for
#    more columns that we actually need.
#
class PickOneRowPerPatientWithColumns(PickOneRowPerPatient):
    selected_columns: Set[Series[Any]]


# This is a variant of the Case operation which maps one set of fixed values to another.
# There are often more efficient ways to handle this in SQL than a naive CASE
# expression, so we add an explicit operation for them.
class FixedValueMap(Series[U]):
    source: Series[T]
    mapping: Mapping[Series[T], Series[U] | None]
    default: Series[U] | None


# Another variant of the Case operation where we're choosing the first non-NULL value
# from several series. There are more efficient and less duplicative ways of
# representing this in SQL than a CASE expression.
class Coalesce(Series[T]):
    sources: tuple[Series[T]]


def apply_transforms(root_node, skip_optimizations=False):
    root_node = apply_sort_rewrites(root_node)
    if not skip_optimizations:
        root_node = apply_optimizations(root_node)
    return root_node


def apply_sort_rewrites(root_node):
    # This transform is required for ehrQL's sorting semantics to be respected
    nodes = all_unique_nodes(root_node)
    reverse_index = build_reverse_index(nodes)
    rewriter = QueryGraphRewriter()
    for node in nodes:
        if isinstance(node, PickOneRowPerPatient):
            rewrite_sorts(rewriter, node, reverse_index)
    return rewriter.rewrite(root_node)


def apply_optimizations(root_node):
    # These transforms should not affect behaviour but are just performance
    # improvements
    transforms = [
        rewrite_case_to_fixed_value_map,
        rewrite_case_to_coalesce,
    ]

    rewriter = QueryGraphRewriter()

    for node in all_unique_nodes(root_node):
        original = node
        for transform in transforms:
            if result := transform(node):
                node = result
        if node is not original:
            rewriter.replace(original, node)

    return rewriter.rewrite(root_node)


def replace_nodes(root_node, replacements):
    """
    Takes a root_node and a dict of nodes that exist within the root, and
    replacements for them.
    Replaces the nodes in the root and returns the modified root node.
    """
    rewriter = QueryGraphRewriter()
    for node, replacement in replacements.items():
        rewriter.replace(node, replacement)
    return rewriter.rewrite(root_node)


def rewrite_sorts(rewriter, node, reverse_index):
    """
    Frames are sorted in order to then pick the first or last row for a patient. Multiple sorts
    may be applied to give the desired results. Once a single row has been picked, one or more
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
        sort
        for sort in all_sorts
        if isinstance(sort.sort_by, SelectColumn)
        # SelectColumn operations only count as direct sorts if they're selected from
        # the frame we're sorting, not from some other patient frame
        and not has_one_row_per_patient(sort.sort_by.source)
    ]
    existing_sorted_column_names = {sort.sort_by.name for sort in direct_sorts}
    sorts_to_add = selected_column_names - existing_sorted_column_names

    # Arbitrary canonical ordering
    return sorted(sorts_to_add)


def make_sortable(col):
    if get_series_type(col) is bool:
        # Some databases can't sort booleans (including SQL Server), so we cast them to
        # integers
        return Function.CastToInt(col)
    return col


def rewrite_case_to_fixed_value_map(node):
    """
    If the supplied Case operation can be represented as a FixedValueMap then return
    that representation, otherwise return None
    """
    if not isinstance(node, Case):
        return

    source = MISSING = object()
    mapping = {}

    # We're looking for Case operations with a particular structure, comparing a single
    # series to a list of fixed values and returning an alternative fixed value in its
    # place e.g.
    #
    #     case(
    #         when(some_series == "value_1").then("value_A"),
    #         when(some_series == "value_2").then("value_B"),
    #         when(some_series == "value_3").then("value_C"),
    #         ...
    #         otherwise=="value_X"
    #     )
    #
    # If at any point we don't find the structure we're looking for we bail out
    for when, then in node.cases.items():
        if not isinstance(when, Function.EQ):
            return
        if isinstance(when.rhs, Value):
            lhs, rhs = when.lhs, when.rhs
        else:
            # Accept the backwards construction `"value_1" == some_series` by flipping
            # the arguments if the RHS isn't a value
            lhs, rhs = when.rhs, when.lhs

        if source is MISSING:
            source = lhs

        if lhs != source:
            return
        if not isinstance(rhs, Value):
            return
        if not isinstance(then, Value | None):
            return

        # Case expressions have "first match wins" semantics so we need to preserve that
        # here
        if rhs not in mapping:
            mapping[rhs] = then

    if not isinstance(node.default, Value | None):
        return

    return FixedValueMap(
        source=source,
        mapping=mapping,
        default=node.default,
    )


def rewrite_case_to_coalesce(node):
    """
    If the supplied Case operation can be represented as a Coalesce then return
    that representation, otherwise return None
    """
    if not isinstance(node, Case):
        return

    sources = []

    # We're looking for Case operations where every case is of the form:
    #
    #   when(some_series.is_not_null()).then(some_series)
    #
    for when, then in node.cases.items():
        # Attempt to remove any redundant clauses from the condition which might
        # otherwise prevent it from being optimized
        when = simplify_potential_coalesce_condition(when, sources)
        if then is None or when != Function.Not(Function.IsNull(then)):
            return
        sources.append(then)
    if node.default is not None:
        sources.append(node.default)

    if len(sources) > 1:
        return Coalesce(sources=tuple(sources))
    elif len(sources) == 1:
        # If there's only one argument then remove the operation entirely as it is not
        # doing anything. Some databases reject single-argument COALESCE so it's better
        # not to have them at all.
        return sources[0]
    else:
        assert False, "Empty Case expression should be impossible to build"


def simplify_potential_coalesce_condition(condition, previous_sources):
    """
    Users sometimes add redundant null checks into case expressions which would
    otherwise have the exact form of a coalesece expression. For example:

        case(
            when(s1.is_not_null()).then(s1),
            when(s1.is_null() & s2.is_not_null()).then(s2),
            when(s1.is_null() & s2.is_null() & s3.is_not_null()).then(s3),
        )

    These are redundant because cases are evaluated sequentially and so it's impossible
    to get to e.g. the second clause above unless `s1` is null.

    We should teach our users not to do this, but it's still better if we can handle
    these constructions efficiently and so we attempt to do so here.
    """
    # If the condition is a conjunction (or a set of nested conjunctions) then unpack it
    # into its component clauses
    if isinstance(condition, Function.And):
        clauses = unpack_conjunction(condition)
        # Any checks that previous source series are null are redundant here because,
        # given the structure of these case operations, we couldn't have got to the
        # current source if the previous ones weren't null
        redundant_clauses = {Function.IsNull(source) for source in previous_sources}
        # If after removing any redundant clauses we're left with just a single clause
        # then return it
        filtered_clauses = clauses - redundant_clauses
        if len(filtered_clauses) == 1:
            return list(filtered_clauses)[0]

    # Otherwise just return the original unchanged
    return condition


def unpack_conjunction(node):
    clauses = set()
    for clause in (node.lhs, node.rhs):
        if isinstance(clause, Function.And):
            clauses.update(unpack_conjunction(clause))
        else:
            clauses.add(clause)
    return clauses


def build_reverse_index(nodes):
    reverse_index = defaultdict(set)
    for n in nodes:
        for i in get_input_nodes(n):
            reverse_index[i].add(n)
    return reverse_index


def substitute_parameters(node, **parameter_values):
    rewriter = QueryGraphRewriter()
    for name, value in parameter_values.items():
        value_type = type(value)
        parameter = Parameter(name, value_type)
        rewriter.replace(parameter, Value(value))
    return rewriter.rewrite(node)
