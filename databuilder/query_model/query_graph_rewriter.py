from databuilder.query_model import nodes as qm


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
        if isinstance(obj, qm.Node):
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
