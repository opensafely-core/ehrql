class BaseQueryEngine:
    """
    A base QueryEngine to hold methods that are agnostic to how the specific queries are built.
    Inheriting classes must implement translating the query model into their particular flavour of tables and query
    language (SQL, pandas dataframes etc).
    """

    def __init__(self, backend):
        """
        `backend` is a Backend instance
        """
        self.backend = backend

    def execute_query(self, column_definitions):
        """
        `column_definitions` is a dictionary mapping output column names to
        query model graphs which specify the queries used to populate them

        Override this method to do the things necessary to generate query code and execute
        it against a particular backend
        """
        raise NotImplementedError
