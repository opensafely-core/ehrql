import contextlib
import secrets
from functools import cache, cached_property, singledispatchmethod

import sqlalchemy
from sqlalchemy.sql import operators
from sqlalchemy.sql.visitors import replacement_traverse

from databuilder.query_model import (
    AggregateByPatient,
    Categorise,
    Code,
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
)

from .base import BaseQueryEngine
from .sqlite_dialect import SQLiteDialect


class SQLiteQueryEngine(BaseQueryEngine):

    sqlalchemy_dialect = SQLiteDialect

    def get_query(self, variable_definitions):
        variable_expressions = {
            name: self.get_sql(definition)
            for name, definition in variable_definitions.items()
        }
        population_expression = variable_expressions.pop("population")
        query = self.get_select_query_for_patient_domain()
        query = query.add_columns(
            *[expr.label(name) for name, expr in variable_expressions.items()]
        )
        query = query.where(population_expression)
        query = prepare_query(query)
        return query

    def get_select_query_for_domain(self, domain):
        """
        Given a Domain object return the SELECT statement that forms the basis of any
        queries using this domain
        """
        if domain != domain.PATIENT:
            # By construction query nodes of many-rows-per-patient dimension always have
            # a single ManyRowsPerPatientFrame which defines its domain. We fetch this
            # and then use it to generate the corresponding query.
            frame = domain.get_node()
            return self.get_select_query_for_frame(frame)
        else:
            # TODO: This branch is only present to support aggregations over data which
            # is already patient-level. Our query model currently allows this (simply
            # because (simply because it's tricky to forbid it statically using the
            # machinery we have) and previously the spec tests made (inadvertent) use of
            # it. We need to either forbid this in the query model, or decide that we do
            # want to support it and write some tests for it.
            return self.get_select_query_for_patient_domain()  # pragma: no cover

    def get_select_query_for_patient_domain(self):
        """
        Return a SELECT query which is to form the basis of a one-row-per-patient query
        """
        # Eventually we may allow, or require, backends to specify a table which defines
        # the "universe" of patients over which we operate. For now, we pretend we
        # already have such a table by creating a "placeholder" table. Later in the
        # query construction process we can generate a CTE which defines this table. But
        # we don't know exactly what this CTE should contain until we've finished
        # constructing the query. So using this placeholder trick allows us to follow a
        # more natural ordering when constructing the query.

        # Make the name unique to avoid clashes where we have more than one nested
        # patient-level query.
        placeholder_name = f"patients_{secrets.token_hex(6)}"
        table = sqlalchemy.Table(
            placeholder_name, sqlalchemy.MetaData(), sqlalchemy.Column("patient_id")
        )
        # Add a flag to the user metadata so we can identify these tables later
        table.is_placeholder = True
        return sqlalchemy.select([table.c.patient_id])

    def get_select_query_for_frame(self, frame):
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

    @singledispatchmethod
    def get_sql(self, node):
        assert False, f"Unhandled node: {node}"

    @get_sql.register(Value)
    def get_sql_value(self, node):
        return convert_types(node.value)

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


    @get_sql.register(Categorise)
    def get_sql_categorise(self, node):
        cases = [
            (self.get_sql(condition), self.get_sql(value))
            for (value, condition) in node.categories.items()
        ]
        if node.default is not None:
            default = self.get_sql(node.default)
        else:
            default = None
        return sqlalchemy.case(*cases, else_=default)

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

    def aggregate_by_patient(self, source_node, aggregation_func):
        domain = get_domain(source_node)
        query = self.get_select_query_for_domain(domain)
        expression = self.get_sql(source_node)
        query = query.add_columns(aggregation_func(expression).label("value"))
        query = query.group_by(query.selected_columns[0])
        query = prepare_query(query)
        aggregated_table = self.reify_query(query)
        return aggregated_table.c.value

    def aggregate_by_patient_non_nullable(self, node, aggregation_func, empty_value):
        # These aggregation functions don't take an argument as they operate over the
        # entire query, so we wrap them in a lambda which swallows the argument
        value = self.aggregate_by_patient(node, lambda _: aggregation_func)
        # These aggregations are also guaranteed not to be null-valued, even when
        # combined with data involving patient_ids for which they're not defined
        return sqlalchemy.func.coalesce(value, empty_value)

    @get_sql.register(PickOneRowPerPatient)
    def get_sql_pick_one_row_per_patient(self, node):
        domain = get_domain(node.source)
        query = self.get_select_query_for_domain(domain)

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

        query = prepare_query(query)

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
        return [self.get_sql(s.sort_by) for s in sorts]

    def reify_query(self, query):
        """
        By "reify" we just mean turning a SELECT query into something that can function
        as a table in other SQLAlchemy constructs. There are various ways to do this
        e.g. using `.alias()` to make a sub-query, using `.cte()` to make a Common Table
        Expression, or writing the results of the query to a temporary table.
        """
        return query.cte()

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


def convert_types(value):
    """
    Convert static values to the types needed by SQLAlchemy
    """
    if isinstance(value, frozenset):
        return tuple(convert_types(v) for v in value)
    elif isinstance(value, Code):
        # Unwrap Code instances to their inner values
        return value.value
    else:
        return value


def prepare_query(query):
    query = replace_placeholder_table_references(query)
    query = apply_patient_joins(query)
    return query


def replace_placeholder_table_references(query):
    """
    Where a backend doesn't provide us with a single "patient universe" table guaranteed
    to contain all patients, we instead generate a "placeholder" table to use instead.

    This function identifies such placeholder tables, generates an appropriate Common
    Table Expression (CTE) which defines what the contents of this table should be, and
    attaches it to the query which means that references to the placeholder will then
    point to the CTE.
    """
    # By convention, the first column in all our queries is always the patient_id column
    id_column = query.selected_columns[0]
    placeholder_table = id_column.table
    if not getattr(placeholder_table, "is_placeholder", False):
        return query

    other_tables = [t for t in query.get_final_froms() if t is not placeholder_table]
    if len(other_tables) > 1:
        # Select all patient IDs from all tables used in the query
        id_selects = [
            sqlalchemy.select(table.c[id_column.name]) for table in other_tables
        ]
        # Create a CTE which is the union of all these IDs. (Note UNION rather than
        # UNION ALL so we don't get duplicates. The tables themselves are necessarily
        # one-row-per-patient tables and so don't require de-duplicating.)
        placeholder_definition = sqlalchemy.union(*id_selects).cte(
            placeholder_table.name
        )
        # Include the CTE definition in the query
        return query.add_cte(placeholder_definition)
    elif len(other_tables) == 1:
        # If there's only one table then, rather than define a CTE for it, just replace
        # references to the placeholder table with references to this table. Using a CTE
        # wouldn't be wrong — just pointless; and they can act as optimisation fences in
        # some DBMSs.
        new_id_column = other_tables[0].c[id_column.name]
        # SQLAlchemy provides some handy "query surgery" functions, see:
        # https://docs.sqlalchemy.org/en/14/core/visitors.html#sqlalchemy.sql.visitors.replacement_traverse
        return replacement_traverse(
            query, {}, replace=lambda obj: new_id_column if obj is id_column else None
        )
    else:
        assert False, "No tables found in query"


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
