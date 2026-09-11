import enum
from types import NoneType

from ehrql.query_model import nodes as qm


class ReplacementType(enum.Enum):
    NON_WRAPPING = enum.auto()
    WRAPPING = enum.auto()


class QueryGraphRewriter:
    """
    Query graphs are composed of immutable query model Node objects. This class allows
    us to modify these graphs by building up a set of replacements (node X replaces node
    A; node Y replaces node B etc) and then creating a new graph based on an existing
    one but incorporating these replacements.
    """

    # These are types which we don't attempt to recurse into and rewrite
    PASS_THROUGH_TYPES = (
        # We always return Values unchanged. It doesn't make much sense to, e.g. replace
        # all the occurences of 4 in a query with 5. And by handling these explicitly we
        # don't have to exhaustively list the types of object a Value can contain.
        qm.Value
        # InlinePatientTables are similar to Values in that they're wrappers around
        # static data supplied by the user and we likewise don't want to recurse into
        # these
        | qm.InlinePatientTable
        # Some non-Node types which appear in the query model
        | qm.Position
        | qm.TableSchema
        # The few primitive types which appear in the query model and are not always
        # wrapped in a `Value`
        | NoneType
        | int
        | str
    )

    def __init__(self, replacements=None):
        self.replacements = replacements or {}

    def replace(self, target_node, new_node):
        """
        Specify that `target_node` should be replaced by `new_node` wherever it appears.

        Note that if you to use this to "wrap" a node by replacing it with something
        that has the original target node as a child (e.g. replacing `A` with `X -> A`)
        then you will encounter an infinite recursion error when attempting to rewrite a
        graph.

        For replacements of this sort you should use the `wrap()` method below, which is
        less performant but handles this case correctly.
        """
        self.replacements[target_node] = new_node, ReplacementType.NON_WRAPPING

    def wrap(self, target_node, new_node):
        """
        Specify that `target_node` should be replaced by `new_node` wherever it appears.

        This method should be used whenever `new_node` contains `target_node`.
        Attempting to use the default `replace()` method will lead to an infinite
        recursion error. However as the replacement algorithm used here is much less
        performant it should only be used when actually needed.
        """
        self.replacements[target_node] = new_node, ReplacementType.WRAPPING

    def rewrite(self, obj):
        # Shortcut when there's no work to be done
        if not self.replacements:
            return obj

        self.cache = {}
        try:
            return self._rewrite(obj)
        except RecursionError as exc:
            exc.add_note(
                "\nYou may need to use `wrap()` instead of `replace()`. "
                "See docstrings on `QueryGraphRewriter`"
            )
            raise

    def _rewrite(self, obj):
        if isinstance(obj, self.PASS_THROUGH_TYPES):
            # Certain types we don't attempt to unpack and just pass through unmodified
            return obj
        elif isinstance(obj, qm.Node):
            # This is where most the work gets done
            return self._rewrite_node_with_cache(obj)
        elif isinstance(obj, dict):
            # Dicts need rewriting because they may contain references to other nodes
            return {self._rewrite(k): self._rewrite(v) for k, v in obj.items()}
        elif isinstance(obj, frozenset | tuple):
            # As do frozensets and tuples
            return obj.__class__(self._rewrite(v) for v in obj)
        else:
            assert False, f"Unhandled value: {obj}"

    def _rewrite_node_with_cache(self, node):
        # Avoid rewriting identical sections of the graph multiple times
        new_node = self.cache.get(node)
        if new_node is None:
            new_node = self._rewrite_node(node)
            self.cache[node] = new_node
        return new_node

    def _rewrite_node(self, node):
        if node in self.replacements:
            return self._replace_node(node)
        else:
            return self._rewrite_node_attributes(node)

    def _replace_node(self, node):
        new_node, replacement_type = self.replacements[node]
        if replacement_type is ReplacementType.WRAPPING:
            # Our replacements are sometimes insertions e.g. given the following graph:
            #
            #     A -> B -> C
            #
            # We might want to replace B with X, where X wraps B:
            #
            #     A -> X -> B -> C
            #
            # To do this we need to make sure that while we're in the process of
            # generating B's replacement we don't attempt to replace B _again_ in any
            # downstream segments of the graph, which would lead to infinite recursion.
            # We avoid this by creating a new rewriter for the sub-graph which has the
            # currently active replacement rule removed.
            other_replacements = self.replacements.copy()
            other_replacements.pop(node)
            subgraph_rewriter = self.__class__(other_replacements)
            return subgraph_rewriter.rewrite(new_node)
        elif replacement_type is ReplacementType.NON_WRAPPING:
            # If our replacement is not of this kind then we can skip this additional work
            return self._rewrite(new_node)
        else:
            assert False, f"unhandled: {replacement_type}"

    def _rewrite_node_attributes(self, node):
        attrs = {k: v for k, v in node.__dict__.items() if not k.startswith("_")}
        new_attrs = self._rewrite(attrs)
        # If nothing about the node has changed then return the original rather than
        # constructing an identical replacement. This avoids unnecessarily revalidating
        # the node.
        if attrs == new_attrs:
            return node
        else:
            return type(node)(**new_attrs)
