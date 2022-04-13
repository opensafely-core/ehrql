import contextlib
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
        query = add_implicit_joins(query)
        return query

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
        return source.c[node.name]

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
        return self.aggregate_by_patient_non_nullable(
            node.source, sqlalchemy.literal(True), False
        )

    @get_sql.register(AggregateByPatient.Count)
    def get_sql_count(self, node):
        return self.aggregate_by_patient_non_nullable(
            node.source, sqlalchemy.func.count("*"), 0
        )

    def aggregate_by_patient(self, source, aggregation_func):
        expression = self.get_sql(source)
        if has_many_rows_per_patient(source):
            query = self.get_select_query_for_node(source)
        else:
            query = sqlalchemy.select([self.get_patient_table(expression).c.patient_id])
        query = query.add_columns(aggregation_func(expression))
        query = query.group_by(query.selected_columns[0])
        query = add_implicit_joins(query)
        aggregated_table = query.cte()
        return aggregated_table.c[1]

    def aggregate_by_patient_non_nullable(self, source, aggregation_func, empty_value):
        value = self.aggregate_by_patient(source, lambda _: aggregation_func)
        return sqlalchemy.func.coalesce(value, empty_value)

    @get_sql.register(AggregateByPatient.Sum)
    def get_sql_sum(self, node):
        return self.aggregate_by_patient(node.source, sqlalchemy.func.sum)

    @get_sql.register(Sort)
    def get_sql_sort(self, node):
        return self.get_sql(node.source)

    @get_sql.register(PickOneRowPerPatient)
    def get_sql_pick_one_row_per_patient(self, node):
        query = self.get_select_query_for_node(node.source)

        base_table = query.get_final_froms()[0]
        already_selected = set(query.selected_columns)
        other_columns = [c for c in base_table.c.values() if c not in already_selected]

        sort_columns = query.partition_order_clauses
        if node.position == Position.LAST:
            sort_columns = [column.desc() for column in sort_columns]

        # Number rows sequentially over the order by columns for each patient id
        row_num = (
            sqlalchemy.func.row_number()
            .over(partition_by=query.selected_columns[0], order_by=sort_columns)
            .label("_row_num")
        )
        query = query.add_columns(*other_columns, row_num)
        query = add_implicit_joins(query)
        subquery = query.alias()
        subquery_columns = list(subquery.columns)

        partitioned_query = sqlalchemy.select(subquery_columns[:-1]).where(
            subquery_columns[-1] == 1
        )
        return partitioned_query.cte()

    def get_select_query_for_node(self, node):
        frame = get_many_rows_per_patient_frame(node)
        root_frame, filters, sorts = get_frame_operations(frame)
        table = self.get_sql(root_frame)
        where_clauses = [self.get_sql(f) for f in filters]
        order_clauses = [self.get_sql(s) for s in sorts]

        query = sqlalchemy.select([table.c.patient_id])
        if where_clauses:
            query = query.where(sqlalchemy.and_(*where_clauses))

        query.partition_order_clauses = tuple(order_clauses)

        return query

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
    # Given the constraints on the query model this can only happen if we're passed a
    # one-row-per-patient node, which we should never be
    assert children, "No ManyRowsPerPatientFrame found"
    return get_many_rows_per_patient_frame(*children)


def get_frame_operations(frame):
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
            return frame, filters, sorts
        else:
            assert False, f"Unhandled type: {frame}"


def add_implicit_joins(query):
    join_key = query.selected_columns[0]
    join_column = join_key.name
    joined_tables = {query.get_final_froms()[0]}
    for table in get_referenced_tables(query):
        if table not in joined_tables:
            joined_tables.add(table)
            query = query.join(table, table.c[join_column] == join_key, isouter=True)
    return query
