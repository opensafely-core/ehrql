import structlog
from ehrql.query_engines.base_sql import BaseSQLQueryEngine
from ehrql.query_engines.trino_dialect import TrinoDialect


log = structlog.getLogger()


class TrinoQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = TrinoDialect
