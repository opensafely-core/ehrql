import structlog
from trino.sqlalchemy.dialect import TrinoDialect

from ehrql.query_engines.base_sql import BaseSQLQueryEngine


log = structlog.getLogger()


class TrinoQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = TrinoDialect
