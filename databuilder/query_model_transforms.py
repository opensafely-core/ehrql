"""
Apply modifications to the query graph which make it easier to work with or allow us to
generate more efficient SQL.

This involes adding new kinds of nodes to the query model. However we deliberately
define these nodes outside of the core query_model module because we're trying to
maintain separation of three types of concern:

    1. capturing the semantics of the query (which is the query model's job);
    2. worrying about expressiveness and ease of use (which is ehrQL's job);
    3. worrying about efficient execution (which is the query engines' job).

The transformations applied here are all about efficient execution, and therefore we
want to keep them separate from the core query model classes.
"""
import copy
from typing import Any

from databuilder.query_model import PickOneRowPerPatient, SelectColumn, get_input_nodes


class PickOneRowPerPatientWithColumns(PickOneRowPerPatient):
    # The actual type here is `frozenset[Series]` but our type-checking code can't
    # currently handle the mixed type sets we get here (e.g. `Series[bool]` and
    # `Series[int]`). We've decided that, as this is an internal class not part of the
    # public API, it's not worth complicating the type-checking code for this use case.
    selected_columns: Any


def apply_transforms(variables):
    # For algorithmic ease we're going to be mutating the query objects, so we make a
    # copy first to avoid side-effects
    variables = copy.deepcopy(variables)
    reverse_index = get_reverse_index(variables.values())
    add_selected_columns_to_pick_row(reverse_index)
    return variables


def get_reverse_index(nodes):
    """
    Return a dict mapping every node in the query to the (possibly empty) set of nodes
    which reference it

    This allows walking "backwards" along the graph which makes certain kinds of
    transformation easier.
    """
    index = {}
    for node in nodes:
        populate_reverse_index(index, node)
    return index


def populate_reverse_index(index, node):
    index.setdefault(node, set())
    for subnode in get_input_nodes(node):
        index.setdefault(subnode, set()).add(node)
        populate_reverse_index(index, subnode)


def add_selected_columns_to_pick_row(reverse_index):
    """
    Replace instances of `PickOneRowPerPatient` with `PickOneRowPerPatientWithColumns`
    which track the columns that are going to be selected and allow us to generate the
    appropriate query
    """
    for node, references in reverse_index.items():
        if not isinstance(node, PickOneRowPerPatient):
            continue
        # Get the name of any columns selected from this node
        column_names = {c.name for c in references if isinstance(c, SelectColumn)}
        # Build a new set of SelectColumn operations which reference this node's source
        # instead
        selected_columns = frozenset(
            SelectColumn(node.source, name) for name in column_names
        )
        # Create a new node which has the original attributes, plus the tuple of selected
        # columns
        new_node = PickOneRowPerPatientWithColumns(
            source=node.source,
            position=node.position,
            selected_columns=selected_columns,
        )
        # Update any references to the old node to point to the new one
        for ref_node in references:
            update_references(ref_node, node, new_node)


def update_references(target, old_ref, new_ref):
    """
    Replace references to `old_ref` with `new_ref` on `target`
    """
    # We're only expecting nodes with a source attribute here
    assert target.source == old_ref
    force_setattr(target, "source", new_ref)
    # We're only expecting nodes which reference a single input
    assert get_input_nodes(target) == [new_ref]


# We can't modify attributes on frozen dataclass instances in the normal way, so we have
# to use this
force_setattr = object.__setattr__
