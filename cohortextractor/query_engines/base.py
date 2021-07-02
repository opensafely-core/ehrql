class BaseQueryEngine:
    """
    A base QueryEngine to hold methods that are agnostic to how the specific queries are built.
    Inheriting classes must implement translating the AST and groups
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

    def execute_query(self):
        """
        Override this method to do the things necessary to generate query code and execute
        it against a particular backend
        """
        raise NotImplementedError
