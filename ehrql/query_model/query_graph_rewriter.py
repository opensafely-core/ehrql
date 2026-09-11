from types import NoneType

from ehrql.query_model import nodes as qm


class QueryGraphRewriter:
    """
    Query graphs are composed of immutable query model Node objects. This class allows
    us to modify these graphs by building up a set of replacements (node X replaces node
    A; node Y replaces node B etc) and then creating a new graph based on an existing
    one but incorporating these replacements.
    """

    def __init__(self, replacements=None):
        self.replacements = replacements or {}

    def replace(self, target_node, new_node):
        self.replacements[target_node] = new_node

    def rewrite(self, obj):
        self.cache = {}
        return self._rewrite(obj)

    def _rewrite(self, obj):
        # Shortcut when there's no remaining work to be done
        if not self.replacements:
            return obj

        if isinstance(obj, qm.Value):
            # We always return Values unchanged. It doesn't make much sense to, e.g.
            # replace all the occurences of 4 in a query with 5. And by handling these
            # explicitly we don't have to exhaustively list the types of object a Value
            # can contain.
            return obj
        elif isinstance(obj, qm.InlinePatientTable):
            # InlinePatientTables are similar to Values in that they're wrappers around
            # static data supplied by the user and we likewise don't want to recurse
            # into these
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
        elif isinstance(obj, NoneType | int | str | qm.Position | qm.TableSchema):
            # Other expected types we return unchanged
            return obj
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
        # Our replacements are sometimes insertions e.g. given the following graph:
        #
        #     A -> B -> C
        #
        # We might want to replace B with X, where X wraps B:
        #
        #     A -> X -> B -> C
        #
        # To do this we need to make sure that while we're in the process of generating
        # B's replacement we don't attempt to replace B _again_ in any downstream
        # segments of the graph, which would lead to infinite recursion. We avoid this
        # by creating a new rewriter for the sub-graph which has the currently active
        # replacement rule removed.
        other_replacements = self.replacements.copy()
        new_node = other_replacements.pop(node)
        subgraph_rewriter = self.__class__(other_replacements)
        return subgraph_rewriter.rewrite(new_node)

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
