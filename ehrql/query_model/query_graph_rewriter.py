from types import NoneType

from ehrql.query_model import nodes as qm


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

    def rewrite(self, obj):
        return self._rewrite(obj, self.replacements)

    def _rewrite(self, obj, replacements):
        # Shortcut when there's no remaining work to be done
        if not replacements:
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
            return self._rewrite_node_with_cache(obj, replacements)
        elif isinstance(obj, dict):
            # Dicts need rewriting because they may contain references to other nodes
            return {
                self._rewrite(k, replacements): self._rewrite(v, replacements)
                for k, v in obj.items()
            }
        elif isinstance(obj, frozenset | tuple):
            # As do frozensets and tuples
            return obj.__class__(self._rewrite(v, replacements) for v in obj)
        elif isinstance(obj, NoneType | int | str | qm.Position | qm.TableSchema):
            # Other expected types we return unchanged
            return obj
        else:
            assert False, f"Unhandled value: {obj}"

    def _rewrite_node_with_cache(self, node, replacements):
        # Avoid rewriting identical sections of the graph multiple times
        new_node = self.cache.get(node)
        if new_node is None:
            new_node = self._rewrite_node(node, replacements)
            self.cache[node] = new_node
        return new_node

    def _rewrite_node(self, node, replacements):
        if node in replacements:
            return self._replace_node(node, replacements)
        else:
            return self._rewrite_node_attributes(node, replacements)

    def _replace_node(self, node, replacements):
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
        # downstream segments of the graph. We avoid this by removing any nodes
        # we're in the process of replacing from the copy of the replacements dict
        # which we pass down.
        replacements = replacements.copy()
        node = replacements.pop(node)
        return self._rewrite(node, replacements)

    def _rewrite_node_attributes(self, node, replacements):
        attrs = {k: v for k, v in node.__dict__.items() if not k.startswith("_")}
        new_attrs = self._rewrite(attrs, replacements)
        # If nothing about the node has changed then return the original rather than
        # constructing an identical replacement. This avoids unnecessarily revalidating
        # the node.
        if attrs == new_attrs:
            return node
        else:
            return type(node)(**new_attrs)
