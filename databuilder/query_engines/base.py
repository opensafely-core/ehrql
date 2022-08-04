class BaseQueryEngine:
    """
    A base QueryEngine to hold methods that are agnostic to how the specific queries are built.
    Inheriting classes must implement translating the query model into their particular flavour of tables and query
    language (SQL, pandas dataframes etc).
    """

    def __init__(self, dsn, backend=None, config=None):
        """
        `dsn` is  Data Source Name — a string (usually a URL) which provides connection
            details to a data source (usually a RDBMS)
        `backend` is an optional Backend instance
        `config` is an optional dictionary of config values
        """
        self.dsn = dsn
        self.backend = backend
        self.config = config or {}

    def get_results(self, variable_definitions):
        """
        `variable_definitions` is a dictionary mapping output column names to
        query model graphs which specify the queries used to populate them

        Override this method to do the things necessary to generate query code and execute
        it against a particular backend
        """
        raise NotImplementedError
