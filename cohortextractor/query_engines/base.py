from collections import defaultdict

from ..query_language import Column, QueryNode, Table, Value, ValueFromRow


class BaseQueryEngine:
    """
    A base QueryEngine to hold methods that deal with walking the AST are agnostic to how
    the specific queries are built.  Inheriting classes must implement translating the groups
    of linear node paths into their particular flavour of tables (SQL, pandas dataframes etc)
    """

    def __init__(self, column_definitions, backend):
        """
        `column_definitions` is a dictionary mapping output column names to
        Values, which are leaf nodes in DAG of QueryNodes

        `backend` is a Backend instance
        """
        self.column_definitions = column_definitions
        self.backend = backend
        # Walk over all nodes in the query DAG looking for output nodes (leaf
        # nodes which represent a value or a column of values) and group them
        # together by "type" and "source" (source being the parent node from
        # which they are derived). Each such group of outputs can be generated
        # by a single query so we want them grouped together.
        self.output_groups = defaultdict(list)
        for node in self.walk_query_dag(column_definitions.values()):
            if self.is_output_node(node):
                self.output_groups[self.get_type_and_source(node)].append(node)

    def walk_query_dag(self, nodes):
        parents = []
        for node in nodes:
            yield node
            for attr in ("source", "value"):
                reference = getattr(node, attr, None)
                if isinstance(reference, QueryNode):
                    parents.append(reference)
        if parents:
            yield from self.walk_query_dag(parents)

    @staticmethod
    def is_output_node(node):
        return isinstance(node, (Value, Column))

    def get_type_and_source(self, node):
        assert self.is_output_node(node)
        return type(node), node.source

    @staticmethod
    def get_output_column_name(node):
        # TODO deal with ValueFromAggregate
        if isinstance(node, (ValueFromRow, Column)):
            return node.column
        else:
            raise TypeError(f"Unhandled type: {node}")

    @staticmethod
    def get_node_list(node):
        node_list = []
        while True:
            node_list.append(node)
            if type(node) is Table:
                break
            else:
                node = node.source
        node_list.reverse()
        return node_list

    def execute_query(self):
        """
        Override this method to do the things necessary to generate query code and execute
        it against a particular backend
        """
        raise NotImplementedError
