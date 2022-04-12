import contextlib
import dataclasses
from functools import cache, cached_property, singledispatchmethod

import sqlalchemy
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite
from sqlalchemy.sql import operators

from databuilder.query_model import (
    AggregateByPatient,
    Filter,
    Function,
    ManyRowsPerPatientFrame,
    OneRowPerPatientFrame,
    OneRowPerPatientSeries,
    PickOneRowPerPatient,
    Position,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    Sort,
    Value,
    get_input_nodes,
    has_many_rows_per_patient,
)

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
        patient_table = self.get_patient_table(
            population_expression, *variable_expressions.values()
        )
        columns = [
            patient_table.c.patient_id.label("patient_id"),
            *[expr.label(name) for name, expr in variable_expressions.items()],
        ]
        query = sqlalchemy.select(columns).where(population_expression)
        return apply_joins(query, "patient_id")

    def get_patient_table(self, *expressions):
        # TODO: This logic is still under discussion but this covers us for now: it
        # returns a Common Table Expression contain all patient_ids contained in all
        # tables references in the dataset definition
        tables = get_unique_tables(*expressions)
        assert len(tables) > 0, "No tables found in query"
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

    # We have to apply caching here otherwise we generate distinct objects representing
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
        frame = get_filtered_sorted_frame(source)
        table = self.get_sql(frame.root_frame)
        conditions = sqlalchemy.and_(*(self.get_sql(c) for c in frame.filters))
        query = sqlalchemy.select([table.c.patient_id, aggregation]).where(conditions)
        query = apply_joins(query, "patient_id")
        query = query.group_by(table.c.patient_id)
        aggregated_value = query.cte().c[1]
        return sqlalchemy.func.coalesce(aggregated_value, empty_value)

    @get_sql.register(AggregateByPatient.Sum)
    def get_sql_sum(self, node):
        expression = self.get_sql(node.source)
        if has_many_rows_per_patient(node.source):
            frame = get_filtered_sorted_frame(node.source)
            table = self.get_sql(frame.root_frame)
            conditions = sqlalchemy.and_(*(self.get_sql(c) for c in frame.filters))
        else:
            table = self.get_patient_table(expression)
            conditions = True
        query = sqlalchemy.select(
            [table.c.patient_id, sqlalchemy.func.sum(expression)]
        ).where(conditions)
        query = apply_joins(query, "patient_id")
        query = query.group_by(table.c.patient_id)
        return query.cte().c[1]

    @get_sql.register(Sort)
    def get_sql_sort(self, node):
        return self.get_sql(node.source)

    @get_sql.register(PickOneRowPerPatient)
    def get_sql_pick_one_row_per_patient(self, node):
        frame = get_filtered_sorted_frame(node.source)
        table = self.get_sql(frame.root_frame)
        conditions = sqlalchemy.and_(*(self.get_sql(c) for c in frame.filters))
        table = self.get_sql(node.source)
        all_columns = table.columns.values()
        sort_columns = [self.get_sql(c) for c in frame.sorts]
        if node.position == Position.LAST:
            sort_columns = [column.desc() for column in sort_columns]
        # Number rows sequentially over the order by columns for each patient id
        row_num = (
            sqlalchemy.func.row_number()
            .over(order_by=sort_columns, partition_by=table.c.patient_id)
            .label("_row_num")
        )
        base_query = sqlalchemy.select(all_columns + [row_num]).where(conditions)
        base_query = apply_joins(base_query, "patient_id")
        subquery = base_query.alias()
        query = sqlalchemy.select([subquery.c[col.name] for col in all_columns]).where(
            subquery.c._row_num == 1
        )
        return query.cte()

    @get_sql.register(Filter)
    def get_sql_filter(self, node):
        return self.get_sql(node.source)

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


def get_referenced_tables(clause):
    """
    Given an arbitrary SQLAlchemy clause determine what tables it references
    """
    if isinstance(clause, sqlalchemy.Table):
        return (clause,)
    if hasattr(clause, "table") and clause.table is not None:
        return (clause.table,)
    else:
        tables = ()
        for child in clause.get_children():
            tables += get_referenced_tables(child)
        return tables


def get_unique_tables(*expressions):
    tables = {}
    for expression in expressions:
        if isinstance(expression, sqlalchemy.sql.ClauseElement):
            for table in get_referenced_tables(expression):
                tables[table] = True
    return list(tables.keys())


def get_filtered_sorted_frame(node):
    frame = get_many_rows_per_patient_frame(node)
    return combine_filter_and_sort_operations(frame)


def get_many_rows_per_patient_frame(*nodes):
    children = []
    for node in nodes:
        if isinstance(node, ManyRowsPerPatientFrame):
            return node
        else:
            for child in get_input_nodes(node):
                if not isinstance(
                    child, (OneRowPerPatientSeries, OneRowPerPatientFrame)
                ):
                    children.append(child)
    assert children, (
        "No ManyRowsPerPatientFrame found: original node must not have been of "
        "many-rows-per-patient dimension"
    )
    return get_many_rows_per_patient_frame(*children)


def combine_filter_and_sort_operations(frame):
    filters = []
    sorts = []
    while True:
        type_ = type(frame)
        if type_ is Filter:
            filters.insert(0, frame.condition)
            frame = frame.source
        elif type_ is Sort:
            sorts.insert(0, frame.sort_by)
            frame = frame.source
        elif type_ is SelectTable:
            return FilteredSortedFrame(
                root_frame=frame, filters=tuple(filters), sorts=tuple(sorts)
            )
        else:
            assert False, f"Unhandled type: {frame}"


@dataclasses.dataclass
class FilteredSortedFrame:
    root_frame: SelectTable
    filters: tuple
    sorts: tuple


def apply_joins(query, join_column):
    base_table = query.get_final_froms()[0]
    joins = base_table
    joined_tables = {base_table}
    for table in get_referenced_tables(query):
        if table not in joined_tables:
            joined_tables.add(table)
            joins = joins.join(
                table, table.c[join_column] == base_table.c[join_column], isouter=True
            )
    return query.select_from(joins)
