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
import copy
from abc import ABC
from collections.abc import Mapping, MutableMapping, MutableSet
from typing import Any

from databuilder.query_model import (
    Case,
    Function,
    PickOneRowPerPatient,
    SelectColumn,
    Sort,
    Value,
    all_nodes,
    get_input_nodes,
    get_series_type,
    get_sorts,
)


class PickOneRowPerPatientWithColumns(PickOneRowPerPatient):
    # The actual type here is `frozenset[Series]` but our type-checking code can't
    # currently handle the mixed type sets we get here (e.g. `Series[bool]` and
    # `Series[int]`). We've decided that, as this is an internal class not part of the
    # public API, it's not worth complicating the type-checking code for this use case.
    selected_columns: Any


def apply_transforms(variables):
    # For algorithmic ease we're going to be mutating the query objects. Since the QM
    # graph is a notionally immutable structure consisting of "frozen" dataclasses, we need
    # to do that carefully. In particular:
    #
    # 1. We copy the data that is passed in so that callers don't observe side-effects.
    # 2. We copy the results on the way out to rectify the state of containers that depend
    #    on object hashes which may have changed unexpectedly (specifically the frozenset used
    #    to hold selected columns).
    # 3. When we store QM nodes in equality/hash-sensitive containers during this manipulation
    #    we use customized versions of those containers which ignore the __eq__() and
    #    __hash__() implementations provided by dataclasses.
    variables = copy.deepcopy(variables)

    nodes = all_nodes_from_variables(variables)
    reverse_index = build_reverse_index(nodes)

    rewrite_sorts(nodes, reverse_index)

    variables = copy.deepcopy(variables)  # see comment above

    return variables


def rewrite_sorts(nodes, reverse_index):
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
    for node in nodes:
        if not isinstance(node, PickOneRowPerPatient):
            continue

        # What columns are select from this patient frame?
        selected_column_names = {
            c.name for c in reverse_index[node] if isinstance(c, SelectColumn)
        }

        add_columns_to_pick(node, selected_column_names)
        add_extra_sorts(node, selected_column_names)


def add_columns_to_pick(node, selected_column_names):
    selected_columns = frozenset(
        SelectColumn(node.source, c) for c in selected_column_names
    )
    force_setattr(node, "__class__", PickOneRowPerPatientWithColumns)
    force_setattr(node, "selected_columns", selected_columns)


def add_extra_sorts(node, selected_column_names):
    all_sorts = get_sorts(node.source)
    # Add at the bottom of the stack
    lowest_sort = all_sorts[0]

    for column in calculate_sorts_to_add(all_sorts, selected_column_names):
        new_sort = Sort(
            source=lowest_sort.source,
            sort_by=make_sortable(SelectColumn(lowest_sort.source, column)),
        )
        force_setattr(lowest_sort, "source", new_sort)
        force_setattr(lowest_sort.sort_by, "source", new_sort)
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
    nodes = IdentitySet()  # see comment in apply_transforms()
    for query in variables.values():
        query_nodes = all_nodes(query)
        for query_node in query_nodes:
            nodes.add(query_node)
    return nodes


def build_reverse_index(nodes):
    reverse_index = DefaultIdentityDict(IdentitySet)
    for n in nodes:
        for i in get_input_nodes(n):
            reverse_index[i].add(n)
    return reverse_index


class IdentitySet(MutableSet):
    """
    This set considers objects equal if and only if they are identical, even if they
    have overridden __eq__() and __hash__().

    Adapted with gratitude from https://stackoverflow.com/a/17039643/400467.
    """

    def __init__(self, seq=()):
        self._set = {Ref(v) for v in seq}

    def add(self, value):
        self._set.add(Ref(value))

    def discard(self, value):
        self._set.discard(Ref(value))

    def __contains__(self, value):
        return Ref(value) in self._set

    def __len__(self):
        return len(self._set)

    def __iter__(self):
        return (ref.referent for ref in self._set)

    def __repr__(self):
        return f"{type(self).__name__}({list(self)})"


class IdentityDict(MutableMapping):
    """
    This map considers keys equal if and only if they are identical, even if they
    have overridden __eq__() and __hash__().
    """

    def __init__(self, seq=(), **kwargs):
        self._dict = {Ref(k): v for k, v in seq}

    def __setitem__(self, key, value):
        self._dict[Ref(key)] = value

    def __delitem__(self, key):
        del self._dict[Ref(key)]

    def __getitem__(self, key):
        return self._dict[Ref(key)]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return (ref.referent for ref in self._dict)

    def __repr__(self):
        return f"{type(self).__name__}({list(self.items())})"


class DefaultDict(Mapping, ABC):
    """
    Mixin to provide defaultdict-like behaviour for custom Mapping classes.

    Must be the first base class of a derived class. Must be mixed in with
    another base class that provides Mapping methods.
    """

    def __init__(self, default_factory=None, **kwargs):
        super().__init__(**kwargs)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        value = self.default_factory()
        self[key] = value
        return value


class DefaultIdentityDict(DefaultDict, IdentityDict):
    pass


class Ref:
    def __init__(self, referent):
        self.referent = referent

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.referent is other.referent

    def __hash__(self):
        return id(self.referent)


# We can't modify attributes on frozen dataclass instances in the normal way, so we have
# to use this
force_setattr = object.__setattr__
