import contextlib
from functools import cache, cached_property, singledispatchmethod

import sqlalchemy
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite
from sqlalchemy.sql import operators

from databuilder.query_model import (
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
        return self.get_results_query(population_expression, variable_expressions)

    def get_results_query(self, population_expression, variable_expressions):
        query = self.get_patient_select_query(
            population_expression, *variable_expressions.values()
        )
        query = query.add_columns(
            *[expr.label(name) for name, expr in variable_expressions.items()]
        )
        query = query.where(population_expression)
        query = apply_patient_joins(query)
        return query

    def get_patient_select_query(self, *clauses):
        tables = set()
        for clause in clauses:
            tables.update(get_tables(clause))
        assert len(tables) > 0, "No tables found in query"
        # TODO: This logic is still under discussion but this covers us for now: it
        # returns a Common Table Expression contain all patient_ids contained in all
        # tables references in the dataset definition
        id_selects = [
            sqlalchemy.select(table.c.patient_id).distinct() for table in tables
        ]
        patient_table = sqlalchemy.union(*id_selects).cte()
        return sqlalchemy.select([patient_table.c.patient_id])

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

    # We ignore Filter and Sort operations completely at this point in the code and just
    # pass the underlying table reference through. It's only later, when building the
    # SELECT query for a given Frame, that we make use of these. This is in order to
    # mirror the semantics of SQL whereby columns are selected directly from the
    # underlying table and filters and sorts are handled separately using WHERE/ORDER BY
    # clauses.
    @get_sql.register(Sort)
    @get_sql.register(Filter)
    def get_sql_sort_and_filter(self, node):
        return self.get_sql(node.source)

    @get_sql.register(PickOneRowPerPatient)
    def get_sql_pick_one_row_per_patient(self, node):
        query = self.get_select_query_from_frame(node.source)

        # TODO: Really we only want to select the columns from the base table which
        # we're actually going to use. In the old world we did some pre-processing of
        # the graph to make this information available at the point we need it and we
        # should probably reinstate that. But for now we just select all columns from
        # the base table.
        query = select_all_columns_from_base_table(query)

        # Add an extra "row number" column to the query which gives the position of each
        # row within its patient_id partition as implied by the order clauses
        order_clauses = self.get_order_clauses_from_frame(node.source)
        if node.position == Position.LAST:
            order_clauses = [c.desc() for c in order_clauses]
        query = query.add_columns(
            sqlalchemy.func.row_number().over(
                partition_by=query.selected_columns[0], order_by=order_clauses
            )
        )

        query = apply_patient_joins(query)

        # Make the above into a subquery and pull out the relevant columns. Note, we're
        # deliberately using a subquery rather than `reify_query()` here as we want the
        # database to have the chance to spot that we're just fetching the first row
        # from each partition and optimise the query.
        subquery = query.alias()
        subquery_columns = list(subquery.columns)
        output_columns = subquery_columns[:-1]
        row_number = subquery_columns[-1]

        # Select the first row for each patient according to the above row numbering
        partitioned_query = sqlalchemy.select(output_columns).where(row_number == 1)

        return self.reify_query(partitioned_query)

    def reify_query(self, query):
        """
        By "reify" we just mean turning a SELECT query into something that can function
        as a table in other SQLAlchemy constructs. There are various ways to do this
        e.g. using `.alias()` to make a sub-query, using `.cte()` to make a Common Table
        Expression, or writing the results of the query to a temporary table.
        """
        return query.cte()

    def get_select_query_from_frame(self, frame):
        """
        Given a ManyRowsPerPatientFrame return the corresponding SELECT query with the
        appropriate filter operations applied
        """
        root_frame, filters, _ = get_frame_operations(frame)
        table = self.get_sql(root_frame)
        where_clauses = [self.get_sql(f.condition) for f in filters]
        query = sqlalchemy.select([table.c.patient_id])
        if where_clauses:
            query = query.where(sqlalchemy.and_(*where_clauses))
        return query

    def get_order_clauses_from_frame(self, frame):
        """
        Given a ManyRowsPerPatientFrame return the order_by clauses created by any Sort
        operations which have been applied
        """
        _, _, sorts = get_frame_operations(frame)
        return [self.get_sql(s.sort_by) for s in sorts]

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


def apply_patient_joins(query):
    """
    Find any table references in `query` which aren't yet part of an explicit JOIN and
    LEFT OUTER JOIN them into the query using the first selected column as the join key

    A core feature of the Query Model/Engine is that we can arbitrarily include data
    from patient-level tables in a query because, in effect, there is always an implicit
    join on `patient_id`. This function makes those implicit joins explicit.
    """
    # We use the convention that the column to be joined on is always the first selected
    # column. This avoids having to hardcode, or pass around, the name of the column.
    join_key = query.selected_columns[0]
    join_column = join_key.name
    # The table referenced by `join_key`, and any tables already explicitly joined with
    # it, will be returned as the first value from the `get_final_froms()` method
    # (because `join_key` is the first column). Any remaining tables which aren't yet
    # explicitly joined on will be returned as additional clauses in the list. The best
    # explanation of SQLAlchemy's behaviour here is probably this:
    # https://docs.sqlalchemy.org/en/14/changelog/migration_14.html#change-4737
    implicit_joins = query.get_final_froms()[1:]
    for table in implicit_joins:
        query = query.join(table, table.c[join_column] == join_key, isouter=True)
    return query


# TODO: This is hopefully a temporary workaround. See the comment at this function's one
# call site for more detail.
def select_all_columns_from_base_table(query):
    base_table = query.get_final_froms()[0]
    already_selected = {c.name for c in query.selected_columns}
    other_columns = [c for c in base_table.c.values() if c.name not in already_selected]
    return query.add_columns(*other_columns)


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
