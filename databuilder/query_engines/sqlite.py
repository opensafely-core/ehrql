import contextlib
from functools import cache, cached_property, singledispatchmethod

import sqlalchemy
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite
from sqlalchemy.sql import operators

from databuilder.query_model import Function, SelectColumn, SelectPatientTable, Value
from databuilder.sqlalchemy_utils import get_referenced_tables

from .base import BaseQueryEngine


class SQLiteQueryEngine(BaseQueryEngine):

    sqlalchemy_dialect = SQLiteDialect_pysqlite

    def get_query(self, variable_definitions):
        variable_expressions = {
            name: self.get_sql(definition)
            for name, definition in variable_definitions.items()
        }
        population_expression = variable_expressions.pop("population")
        return self.get_results_query(population_expression, variable_expressions)

    def get_results_query(self, population_expression, variable_expressions):
        # Get all referenced tables
        tables = set(get_tables(population_expression))
        for expression in variable_expressions.values():
            tables.update(get_tables(expression))

        assert len(tables) > 0, "No tables found in query"

        patient_table = self.get_patient_table(tables)
        other_tables = tables - {patient_table}

        joins = patient_table
        for table in other_tables:
            joins = joins.join(
                table, table.c.patient_id == patient_table.c.patient_id, isouter=True
            )

        columns = [
            patient_table.c.patient_id.label("patient_id"),
            *[expr.label(name) for name, expr in variable_expressions.items()],
        ]

        return (
            sqlalchemy.select(columns).select_from(joins).where(population_expression)
        )

    def get_patient_table(self, tables):
        # TODO: This logic is still under discussion but this covers us for now: it
        # returns a Common Table Expression contain all patient_ids contained in all
        # tables references in the dataset definition
        id_selects = [
            sqlalchemy.select(table.c.patient_id).distinct() for table in tables
        ]
        return sqlalchemy.union(*id_selects).cte()

    @singledispatchmethod
    def get_sql(self, node):
        assert False, f"Unhandled node: {node}"

    @get_sql.register(Value)
    def get_sql_value(self, node):
        return node.value

    @get_sql.register(Function.EQ)
    def get_sql_eq(self, node):
        return operators.eq(self.get_sql(node.lhs), self.get_sql(node.rhs))

    @get_sql.register(Function.NE)
    def get_sql_ne(self, node):
        return operators.ne(self.get_sql(node.lhs), self.get_sql(node.rhs))

    @get_sql.register(Function.IsNull)
    def get_sql_is_null(self, node):
        return operators.is_(self.get_sql(node.source), None)

    @get_sql.register(Function.Not)
    def get_sql_not(self, node):
        return sqlalchemy.not_(self.get_sql(node.source))

    @get_sql.register(Function.And)
    def get_sql_and(self, node):
        return operators.and_(self.get_sql(node.lhs), self.get_sql(node.rhs))

    @get_sql.register(Function.Or)
    def get_sql_or(self, node):
        return operators.or_(self.get_sql(node.lhs), self.get_sql(node.rhs))

    @get_sql.register(Function.LT)
    def get_sql_lt(self, node):
        return operators.lt(self.get_sql(node.lhs), self.get_sql(node.rhs))

    @get_sql.register(Function.LE)
    def get_sql_le(self, node):
        return operators.le(self.get_sql(node.lhs), self.get_sql(node.rhs))

    @get_sql.register(Function.GT)
    def get_sql_gt(self, node):
        return operators.gt(self.get_sql(node.lhs), self.get_sql(node.rhs))

    @get_sql.register(Function.GE)
    def get_sql_ge(self, node):
        return operators.ge(self.get_sql(node.lhs), self.get_sql(node.rhs))

    @get_sql.register(Function.Negate)
    def get_sql_negate(self, node):
        return operators.neg(self.get_sql(node.source))

    @get_sql.register(Function.Add)
    def get_sql_add(self, node):
        return operators.add(self.get_sql(node.lhs), self.get_sql(node.rhs))

    @get_sql.register(Function.Subtract)
    def get_sql_subtract(self, node):
        return operators.sub(self.get_sql(node.lhs), self.get_sql(node.rhs))

    @get_sql.register(SelectColumn)
    def get_sql_select_column(self, node):
        source = self.get_sql(node.source)
        return source.c[node.name]

    # We have to apply caching here otherwise we generate disinct objects representing
    # the same table and this confuses SQLAlchemy into generating queries with ambiguous
    # table references
    @get_sql.register(SelectPatientTable)
    @cache
    def get_sql_select_table(self, node):
        return self.backend.get_table_expression(node.name)

    @contextlib.contextmanager
    def execute_query(self):
        results_query = self.get_query(self.column_definitions)
        with self.engine.connect() as cursor:
            yield cursor.execute(results_query)

    @cached_property
    def engine(self):
        engine_url = sqlalchemy.engine.make_url(self.backend.database_url)
        # Hardcode the specific SQLAlchemy dialect we want to use: this is the
        # dialect the query engine will have been written for and tested with and we
        # don't want to allow global config changes to alter this
        engine_url._get_entrypoint = lambda: self.sqlalchemy_dialect
        engine = sqlalchemy.create_engine(engine_url, future=True)
        # The above relies on abusing SQLAlchemy internals so it's possible it will
        # break in future -- we want to know immediately if it does
        assert isinstance(engine.dialect, self.sqlalchemy_dialect)
        return engine


def get_tables(obj):
    if isinstance(obj, sqlalchemy.sql.ClauseElement):
        return get_referenced_tables(obj)
    else:
        # Handle literal values (e.g. True) which contain no table references
        return ()
