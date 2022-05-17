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
    get_domain,
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
        query = self.select_patient_id_for_population(population_expression)
        query = query.add_columns(
            *[expr.label(name) for name, expr in variable_expressions.items()]
        )
        query = query.where(population_expression)
        query = apply_patient_joins(query)
        return query

    def select_patient_id_for_population(self, population_expression):
        """
        Return a SELECT query which selects all the patient_ids that _might_ be included
        in the population (the WHERE clause later will filter this down to just those which
        should actually be included)

        This needs to cover, at a minimum, all patient_ids included in all tables
        referenced in the population expression. But including more won't affect the
        correctness of the result, so the only consideration here is performance.

        TODO: Give backends a mechanism for marking certain tables as containing all
        available patient_ids. We could then use such tables if available rather than
        messing aroud with UNIONS.
        """
        # Get all the tables needed to evaluate the population expression
        tables = sqlalchemy.select(population_expression).get_final_froms()
        if len(tables) > 1:
            # Select all patient IDs from all tables referenced in the expression
            id_selects = [sqlalchemy.select(table.c.patient_id) for table in tables]
            # Create a table which contains the union of all these IDs. (Note UNION
            # rather than UNION ALL so we don't get duplicates.)
            population_table = self.reify_query(sqlalchemy.union(*id_selects))
            return sqlalchemy.select(population_table.c.patient_id)
        elif len(tables) == 1:
            # If there's only one table then use the IDs from that
            return sqlalchemy.select(tables[0].c.patient_id)
        else:
            # Gracefully handle the degenerate case where the population expression
            # doesn't reference any tables at all. Our validation rules ensure that such
            # an expression will never evaluate True so the population will always be
            # empty. But we can at least return an empty result, rather than blowing up.
            return sqlalchemy.select(sqlalchemy.literal(None).label("patient_id"))

    @singledispatchmethod
    def get_sql(self, node):
        assert False, f"Unhandled node: {node}"

    @get_sql.register(Value)
    def get_sql_value(self, node):
        return sqlalchemy.literal(node.value)

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
        return sqlalchemy.and_(self.get_sql(node.lhs), self.get_sql(node.rhs))

    @get_sql.register(Function.Or)
    def get_sql_or(self, node):
        return sqlalchemy.or_(self.get_sql(node.lhs), self.get_sql(node.rhs))

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

    @get_sql.register(AggregateByPatient.Sum)
    def get_sql_sum(self, node):
        return self.aggregate_series_by_patient(node.source, sqlalchemy.func.sum)

    @get_sql.register(AggregateByPatient.Exists)
    def get_sql_exists(self, node):
        return self.aggregate_frame_by_patient(
            node.source,
            aggregation_func=sqlalchemy.literal(True),
            empty_value=False,
            single_row_value=True,
        )

    @get_sql.register(AggregateByPatient.Count)
    def get_sql_count(self, node):
        return self.aggregate_frame_by_patient(
            node.source,
            aggregation_func=sqlalchemy.func.count("*"),
            empty_value=0,
            single_row_value=1,
        )

    def aggregate_series_by_patient(self, source_node, aggregation_func):
        query = self.get_select_query_for_node_domain(source_node)
        expression = self.get_sql(source_node)
        query = query.add_columns(aggregation_func(expression).label("value"))
        query = query.group_by(query.selected_columns[0])
        query = apply_patient_joins(query)
        aggregated_table = self.reify_query(query)
        return aggregated_table.c.value

    def aggregate_frame_by_patient(
        self, source_node, aggregation_func, empty_value, single_row_value
    ):
        # Frame aggregations can operate on both one- and many-rows-per-patient frames
        # and these cases require different handling.
        if has_many_rows_per_patient(source_node):
            # For many-rows-per-patient frames we use the series aggregation code but
            # wrapped in some extra logic: these aggregation functions don't take an
            # argument as they operate over the entire query, so we wrap them in a
            # lambda which swallows the argument
            value = self.aggregate_series_by_patient(
                source_node, lambda _: aggregation_func
            )
            # We also want to guarantee that our frame level aggregations are never
            # null-valued, even when combined with data involving patient_ids for which
            # they're not defined
            return sqlalchemy.func.coalesce(value, empty_value)
        else:
            # Given that we have a one-row-per-patient frame here, we can get a
            # reference to the table
            table = self.get_sql(source_node)
            # Create an expression which is True if there's a matching row for this
            # patient and False otherwise (this differs from the SQL for event frame
            # aggregations because there's no need for a GROUP BY)
            has_row = table.c.patient_id.is_not(None)
            # If True and False are the values we're looking for then just return that
            # expression
            if single_row_value is True and empty_value is False:
                return has_row
            else:
                # Otherwise convert to the appropriate values
                return sqlalchemy.case((has_row, single_row_value), else_=empty_value)

    @get_sql.register(PickOneRowPerPatient)
    def get_sql_pick_one_row_per_patient(self, node):
        query = self.get_select_query_for_node_domain(node.source)

        # TODO: Really we only want to select the columns from the base table which
        # we're actually going to use. In the old world we did some pre-processing of
        # the graph to make this information available at the point we need it and we
        # should probably reinstate that. But for now we just select all columns from
        # the base table.
        query = select_all_columns_from_base_table(query)

        # Add an extra "row number" column to the query which gives the position of each
        # row within its patient_id partition as implied by the order clauses
        order_clauses = self.get_order_clauses(node.source)
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

    def get_order_clauses(self, frame):
        """
        Given a ManyRowsPerPatientFrame return the order_by clauses created by any Sort
        operations which have been applied
        """
        _, _, sorts = get_frame_operations(frame)
        # Sort operations are given to us in order of application which is the reverse
        # of order of priority (i.e. the most recently applied sort gives us the primary
        # sort condition)
        return [self.get_sql(s.sort_by) for s in reversed(sorts)]

    def reify_query(self, query):
        """
        By "reify" we just mean turning a SELECT query into something that can function
        as a table in other SQLAlchemy constructs. There are various ways to do this
        e.g. using `.alias()` to make a sub-query, using `.cte()` to make a Common Table
        Expression, or writing the results of the query to a temporary table.
        """
        return query.cte()

    def get_select_query_for_node_domain(self, node):
        """
        Given a many-rows-per-patient node, return the SELECT query corresponding to
        domain of that node
        """
        frame = get_domain(node).get_node()
        root_frame, filters, _ = get_frame_operations(frame)
        table = self.get_sql(root_frame)
        where_clauses = [self.get_sql(f.condition) for f in filters]
        query = sqlalchemy.select([table.c.patient_id])
        if where_clauses:
            query = query.where(sqlalchemy.and_(*where_clauses))
        return query

    @contextlib.contextmanager
    def execute_query(self, variable_definitions):
        results_query = self.get_query(variable_definitions)
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
