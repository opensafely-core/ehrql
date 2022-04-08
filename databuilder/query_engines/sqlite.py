import contextlib
from functools import cache, cached_property, singledispatchmethod

import sqlalchemy
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite
from sqlalchemy.sql import operators

from databuilder.query_model import (
    AggregateByPatient,
    Filter,
    Function,
    PickOneRowPerPatient,
    Position,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    Sort,
    Value,
)
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
        return self.get_results_query(variable_expressions, population_expression)

    def get_results_query(self, variable_expressions, population_expression):
        patient_id_col, joins = self.get_joins_for_expressions(
            population_expression, *variable_expressions.values()
        )
        columns = [
            patient_id_col.label("patient_id"),
            *[expr.label(name) for name, expr in variable_expressions.items()],
        ]
        return (
            sqlalchemy.select(columns).select_from(joins).where(population_expression)
        )

    def get_joins_for_expressions(self, *expressions):
        tables = set()
        for expression in expressions:
            tables.update(get_tables(expression))

        assert len(tables) > 0, "No tables found in expressions"

        patient_table = self.get_patient_table(tables)
        other_tables = tables - {patient_table}
        patient_id_col = patient_table.c.patient_id

        joins = patient_table
        for table in other_tables:
            joins = joins.join(
                table, table.c.patient_id == patient_id_col, isouter=True
            )

        filters = set()
        for table in tables:
            filters.update(table._annotations.get("filters", ()))
        if filters:
            joins = joins._annotate({"filters": tuple(filters)})

        return patient_id_col, joins

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
        column = source.c[node.name]
        column.table = source
        return column

    # We have to apply caching here otherwise we generate disinct objects representing
    # the same table and this confuses SQLAlchemy into generating queries with ambiguous
    # table references
    @get_sql.register(SelectTable)
    @get_sql.register(SelectPatientTable)
    @cache
    def get_sql_select_table(self, node):
        return self.backend.get_table_expression(node.name)

    @get_sql.register(AggregateByPatient.Exists)
    def get_sql_exists(self, node):
        return self.apply_non_nullable_aggregation(
            node.source, sqlalchemy.literal(True), False
        )

    @get_sql.register(AggregateByPatient.Count)
    def get_sql_count(self, node):
        return self.apply_non_nullable_aggregation(
            node.source, sqlalchemy.func.count("*"), 0
        )

    def apply_non_nullable_aggregation(self, source, aggregation, empty_value):
        table = self.get_sql(source)
        query = sqlalchemy.select([table.c.patient_id, aggregation])
        query = apply_filter_condition(query, table)
        query = query.group_by(table.c.patient_id)
        aggregated_value = query.cte().c[1]
        return sqlalchemy.func.coalesce(aggregated_value, empty_value)

    @get_sql.register(AggregateByPatient.Sum)
    def get_sql_sum(self, node):
        expression = self.get_sql(node.source)
        patient_id_col, joins = self.get_joins_for_expressions(expression)
        query = sqlalchemy.select([patient_id_col, sqlalchemy.func.sum(expression)])
        query = query.select_from(joins)
        query = apply_filter_condition(query, joins)
        query = query.group_by(patient_id_col)
        return query.cte().c[1]

    @get_sql.register(Sort)
    def get_sql_sort(self, node):
        table = self.get_sql(node.source)
        column = self.get_sql(node.sort_by)
        return add_sort_column(table, column)

    @get_sql.register(PickOneRowPerPatient)
    def get_sql_pick_one_row_per_patient(self, node):
        table = self.get_sql(node.source)
        all_columns = table.columns.values()
        sort_columns = get_sort_columns(table)
        if node.position == Position.LAST:
            sort_columns = [column.desc() for column in sort_columns]
        # Number rows sequentially over the order by columns for each patient id
        row_num = (
            sqlalchemy.func.row_number()
            .over(order_by=sort_columns, partition_by=table.c.patient_id)
            .label("_row_num")
        )
        subquery = sqlalchemy.select(all_columns + [row_num]).alias()
        query = sqlalchemy.select([subquery.c[col.name] for col in all_columns]).where(
            subquery.c._row_num == 1
        )
        return query.cte()

    @get_sql.register(Filter)
    def get_sql_filter(self, node):
        source = self.get_sql(node.source)
        condition = self.get_sql(node.condition)
        return add_filter_condition(source, condition)

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


# https://docs.sqlalchemy.org/en/14/glossary.html#term-annotations
def apply_filter_condition(query, table):
    conditions = table._annotations.get("filters")
    if conditions:
        query = query.where(sqlalchemy.and_(*conditions))
    return query


def add_filter_condition(table, condition):
    conditions = table._annotations.get("filters", ()) + (condition,)
    return table._annotate({"filters": conditions})


def get_sort_columns(table):
    return table._annotations.get("sort_columns", ())


def add_sort_column(table, column):
    columns = get_sort_columns(table) + (column,)
    return table._annotate({"sort_columns": columns})
