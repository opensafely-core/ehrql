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
    Value,
    get_input_nodes,
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
    """
    Sorting rows and then picking the first or last row for each patient is a common
    operation in ehrQL but it's responsible for a slightly weird corner of ehrQL's
    semantics. This is because it's easy to have "under-specified" results e.g. you sort
    some events by date and pick the first but a patient has multiple events recorded on
    that day.

    In that case, there's no one correct answer as to what row should be returned and
    this creates two related problems:

      * Some databases (e.g. MSSQL) pick randomly (or effectively randomly) meaning you
        can run the same query against the same data and get different results each time.
        This is confusing and generally bad for research (and not in a theoretical
        sense: we've seen this actually happen) so we want to avoid it.

      * Even those databases which return consistent results each time don't necessarily
        return the same results as each other. This prevents our automated generative
        testing, which relies on comparing results between databases, from working.

    What we want is to ensure that even in the case of under-specified sorts there is a
    single correct result defined by ehrQL. But we want to do this without imposing a
    significant performance cost on all our sort queries.

    We do this by defining "tiebreaker sorts" for selecting a winning row in the case of
    multiple equal candidates. That is, if the rows are equally positioned when sorting
    by all the things the user has specified then sort by these other conditions as
    well.

    One simple solution to this would be to sort by every column in the table in lexical
    order. That would guarantee a single stable result. Of course there might still be
    completely duplicate rows, but in that case it doesn't matter which you pick because
    the results are necessarily identical.

    The problem with this solution is that we can have very wide tables with many
    columns and now every time we sort we need to specify all of these as tiebreaker
    conditions. So it fails our "don't impose significant performance cost" condition.

    Another solution is to use just the columns we're actually going to select from the
    results as the tiebreaker conditions. Of course, this doesn't guarantee uniqueness
    of rows: if we select columns A and B from a table we might have multiple rows with
    the same values for A and B but a different value for C. But it does guarantee
    uniqueness of _results_: because we're not selecting column C it doesn't matter
    what's in it.

    This does exactly what we need, however it introduces an oddity into ehrQL's
    semantics which is that you can no longer evaluate it in a bottom-up fashion. The
    value of a pick-first-row operation depends on what columns are _going to be_
    selected from that row.

    This means we need to do some pre-processing of the query graph and annotate each
    such operation with the set of columns that are selected from it elsewhere in the
    query. It would be nicer not to have to do this, but given the above constraints I
    think it's the best practical solution.
    """
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
    # What columns are select from this patient frame?
    selected_column_names = {
        c.name for c in reverse_index[node] if isinstance(c, SelectColumn)
    }
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
