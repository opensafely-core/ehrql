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
        patient_id_expr = self.get_patient_id_expr(
            population_expression, *variable_expressions.values()
        )
        columns = [
            patient_id_expr.label("patient_id"),
            *[expr.label(name) for name, expr in variable_expressions.items()],
        ]
        query = sqlalchemy.select(columns).where(population_expression)
        query = apply_implicit_joins(query)
        return query

    def get_patient_id_expr(self, *expressions):
        # TODO: This logic is still under discussion but this covers us for now: it
        # returns a Common Table Expression contain all patient_ids contained in all
        # tables references in the dataset definition
        tables = get_unique_tables(*expressions)
        assert len(tables) > 0, "No tables found in query"
        id_selects = [
            sqlalchemy.select(table.c.patient_id).distinct() for table in tables
        ]
        return sqlalchemy.union(*id_selects).cte().c.patient_id

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

    # We handle `Filter` and `Sort` operations separately inside the
    # `get_select_query_for_node` method; in this context we just pass through the
    # source expression as if the operation wasn't there. This awkwardness is due to the
    # mismatch between SQL and QueryModel semantics. In SQL, applying a filter or a sort
    # to a table doesn't change the way you reference columns from that table. Instead,
    # these are handled by WHERE/ORDER BY clauses elsewhere. So likewise, here we pass
    # table references unchanged through Filter/Sort and handle them elsewhere.
    @get_sql.register(Sort)
    @get_sql.register(Filter)
    def get_sql_sort_and_filter(self, node):
        return self.get_sql(node.source)

    @get_sql.register(AggregateByPatient.Sum)
    def get_sql_sum(self, node):
        return self.aggregate_by_patient(node.source, sqlalchemy.func.sum)

    @get_sql.register(AggregateByPatient.Exists)
    def get_sql_exists(self, node):
        return self.aggregate_by_patient_non_nullable(
            node.source, sqlalchemy.literal(True), empty_value=False
        )

    @get_sql.register(AggregateByPatient.Count)
    def get_sql_count(self, node):
        return self.aggregate_by_patient_non_nullable(
            node.source, sqlalchemy.func.count("*"), empty_value=0
        )

    @get_sql.register(PickOneRowPerPatient)
    def get_sql_pick_one_row_per_patient(self, node):
        query = self.get_select_query_for_node(node.source)

        # TODO: Really we only want to select the columns from the base table which
        # we're actually going to use. In the old world we did some pre-processing of
        # the graph to make this information available at the point we need it. But for
        # now we just select everything for the base table.
        base_table = query.get_final_froms()[0]
        already_selected = set(query.selected_columns)
        other_columns = [c for c in base_table.c.values() if c not in already_selected]
        query = query.add_columns(*other_columns)

        # Add an extra "row number" column to the query which gives the position of each
        # row within its patient_id group as implied by the order clauses
        desc = node.position == Position.LAST
        order_clauses = [c.desc() if desc else c for c in query.partition_order_clauses]
        query = query.add_columns(
            sqlalchemy.func.row_number().over(
                partition_by=query.selected_columns[0], order_by=order_clauses
            )
        )

        query = apply_implicit_joins(query)

        # Make the above into a subquery and pull out the relevant columns
        subquery = query.alias()
        subquery_columns = list(subquery.columns)
        output_columns = subquery_columns[:-1]
        row_number = subquery_columns[-1]

        # Select the first row for each patient according to the above row numbering
        partitioned_query = sqlalchemy.select(output_columns).where(row_number == 1)

        return partitioned_query.cte()

    def aggregate_by_patient(self, node, aggregation_func):
        expression = self.get_sql(node)
        if has_many_rows_per_patient(node):
            query = self.get_select_query_for_node(node)
        else:
            query = sqlalchemy.select([self.get_patient_id_expr(expression)])
        query = query.add_columns(aggregation_func(expression))
        query = query.group_by(query.selected_columns[0])
        query = apply_implicit_joins(query)
        aggregated_table = query.cte()
        return aggregated_table.c[1]

    def aggregate_by_patient_non_nullable(self, node, aggregation_func, empty_value):
        value = self.aggregate_by_patient(node, lambda _: aggregation_func)
        return sqlalchemy.func.coalesce(value, empty_value)

    def get_select_query_for_node(self, node):
        frame = get_many_rows_per_patient_frame(node)
        root_frame, filters, sorts = get_frame_operations(frame)
        table = self.get_sql(root_frame)
        where_clauses = [self.get_sql(f.condition) for f in filters]
        order_clauses = [self.get_sql(s.sort_by) for s in sorts]

        query = sqlalchemy.select([table.c.patient_id])
        if where_clauses:
            query = query.where(sqlalchemy.and_(*where_clauses))

        query.partition_order_clauses = tuple(order_clauses)

        return query

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


def get_unique_tables(*expressions):
    tables = {}
    for expression in expressions:
        if isinstance(expression, sqlalchemy.sql.ClauseElement):
            for table in expression._from_objects:
                tables[table] = True
    return list(tables.keys())


def apply_implicit_joins(query):
    """
    Find any table references in `query` which aren't part of an explicit JOIN and make
    them part of an explicit LEFT OUTER JOIN using the `patient_id` column (or whatever
    the first column in the SELECT is called — we assume this is always the primary join
    column)
    """
    # We structure our queries so that the column to be joined on is always the first
    join_key = query.selected_columns[0]
    join_column = join_key.name
    # Any tables referenced by clauses in the query which aren't yet explicity joined on
    # will be returned as extra FROM clauses by the `get_final_froms()` method
    implicit_joins = query.get_final_froms()[1:]
    for table in implicit_joins:
        query = query.join(table, table.c[join_column] == join_key, isouter=True)
    return query


def get_many_rows_per_patient_frame(node):
    frames = list(get_many_rows_per_patient_frames(node))
    # By the QueryModel domain constraints, any node of many-rows dimension should have
    # exactly one many-rows frame from which it's derived
    assert len(frames) == 1, f"Expected exactly one frame, got: {frames}"
    return frames[0]


def get_many_rows_per_patient_frames(node):
    """
    Return all ManyRowsPerPatientFrames directly referenced by the suppplied QueryNode
    """
    # Once we've hit a ManyRowsPerPatientFrame we don't dig down further into its
    # children; this is what we mean by "directly reference"
    if isinstance(node, ManyRowsPerPatientFrame):
        return {node}
    # Similarly, we don't dig down through one-row-per-patient nodes
    elif isinstance(node, (OneRowPerPatientSeries, OneRowPerPatientFrame)):
        return set()
    else:
        return set().union(
            *[
                get_many_rows_per_patient_frames(child)
                for child in get_input_nodes(node)
            ]
        )


def get_frame_operations(frame):
    """
    Given a ManyRowsPerPatientFrame, destructure it into a base SelectTable operation,
    plus separate lists of Filter and Sort operations
    """
    filters = []
    sorts = []
    while True:
        type_ = type(frame)
        if type_ is Filter:
            filters.insert(0, frame)
            frame = frame.source
        elif type_ is Sort:
            sorts.insert(0, frame)
            frame = frame.source
        elif type_ is SelectTable:
            return frame, filters, sorts
        else:
            assert False, f"Unexpected type: {frame}"
