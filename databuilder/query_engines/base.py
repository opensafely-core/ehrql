class BaseQueryEngine:
    """
    A base QueryEngine to hold methods that are agnostic to how the specific queries are built.
    Inheriting classes must implement translating the query model into their particular flavour of tables and query
    language (SQL, pandas dataframes etc).
    """

    def __init__(self, dsn, backend=None, temporary_database=None):
        """
        `dsn` is  Data Source Name — a string (usually a URL) which provides connection
            details to a data source (usually a RDBMS)
        `backend` is an optional Backend instance
        """
        self.dsn = dsn
        self.backend = backend
        # TODO: Not sure this belongs here but let's worry about that later
        self.temporary_database = temporary_database

    def execute_query(self, variable_definitions):
        """
        `variable_definitions` is a dictionary mapping output column names to
        query model graphs which specify the queries used to populate them

        Override this method to do the things necessary to generate query code and execute
        it against a particular backend
        """
        raise NotImplementedError
