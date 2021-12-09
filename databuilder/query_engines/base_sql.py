import contextlib
from typing import Optional, Union

import sqlalchemy
import sqlalchemy.dialects.mssql
import sqlalchemy.schema
import sqlalchemy.sql
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.sql.expression import type_coerce

from .. import sqlalchemy_types
from ..functools_utils import singledispatchmethod_with_unions
from ..query_language import (
    Codelist,
    Column,
    Comparator,
    DateDifferenceInYears,
    FilteredTable,
    QueryNode,
    RoundToFirstOfMonth,
    RoundToFirstOfYear,
    Row,
    RowFromAggregate,
    Table,
    Value,
    ValueFromAggregate,
    ValueFromCategory,
    ValueFromFunction,
    ValueFromRow,
)
from .base import BaseQueryEngine


def get_joined_tables(query):
    """
    Given a query object return a list of all tables referenced
    """
    tables = []
    from_exprs = list(query.get_final_froms())
    while from_exprs:
        next_expr = from_exprs.pop()
        if isinstance(next_expr, sqlalchemy.sql.selectable.Join):
            from_exprs.extend([next_expr.left, next_expr.right])
        else:
            tables.append(next_expr)
    # The above algorithm produces tables in right to left order, but it makes
    # more sense to return them as left to right
    tables.reverse()
    return tables


def get_primary_table(query):
    """
    Return the left-most table referenced in the query
    """
    return get_joined_tables(query)[0]


def get_referenced_tables(clause):
    """
    Given an aribtrary SQLAlchemy clause determine what tables it references
    """
    if isinstance(clause, sqlalchemy.Table):
        return (clause,)
    if hasattr(clause, "table"):
        return (clause.table,)
    else:
        tables = set()
        for child in clause.get_children():
            tables.update(get_referenced_tables(child))
        return tuple(tables)


class MissingString(str):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        raise NotImplementedError(self.message)


class BaseSQLQueryEngine(BaseQueryEngine):

    sqlalchemy_dialect: type[Dialect]

    # No limit by default although some DBMSs may impose one
    max_rows_per_insert: Optional[int] = None

    # Per-instance cache for SQLAlchemy Engine
    _engine: Optional[sqlalchemy.engine.Engine] = None

    # Force subclasses to define this
    temp_table_prefix: str = MissingString("'temp_table_prefix' is undefined")

    temp_table_count: int = 0

    def get_queries(self):
        """Build the list of SQL queries to execute"""
        # Record all the temporary tables we need to create as a mapping from Table
        # object to the list of queries needed to create and populate it. This will get
        # populated inside the calls to `get_value_expression` below.
        self.temp_tables: dict[sqlalchemy.Table, list[sqlalchemy.sql.Executable]] = {}
        # Reset the cache. See the docstring on `get_value_expression` for more details
        self.value_expression_cache: dict[QueryNode, sqlalchemy.sql.ClauseElement] = {}

        # `population` is a special-cased boolean column, it doesn't appear
        # itself in the output but it determines what rows are included
        # Build the base results table from the population table
        column_definitions = self.column_definitions.copy()
        population = column_definitions.pop("population")
        results_query = self.get_population_table_query(population)

        # Build big JOIN query which selects the results
        for column_name, output_node in column_definitions.items():
            # For each output column, generate the query that selects it from its interim table(s)
            # For most outputs there will just be a single interim table.  Category outputs
            # may require more than one.
            column = self.get_value_expression(output_node)
            # Then generate the query to join on it
            for table in get_referenced_tables(column):
                results_query = self.include_joined_table(results_query, table)

            # Add this column to the final selected results
            results_query = results_query.add_columns(column.label(column_name))

        # Get all the queries needed to populate the various temporary tables we need
        temp_table_queries = sum(self.temp_tables.values(), start=[])

        return temp_table_queries + [results_query]

    @contextlib.contextmanager
    def execute_query(self):
        queries = self.get_queries()
        with self.engine.connect() as cursor:
            for query in queries:
                result = cursor.execute(query)
            # We're only interested in the results from the final query
            yield result
            self.post_execute_cleanup(cursor)

    def post_execute_cleanup(self, cursor):
        """
        Called after results have been fetched
        """
        for table in self.temp_tables.keys():
            self.drop_temp_table(cursor, table)

    def drop_temp_table(self, cursor, table):
        """
        Drop the specified temporary table
        """
        query = sqlalchemy.schema.DropTable(table, if_exists=True)
        cursor.execute(query)

    #
    # DATABASE CONNECTION
    #
    @property
    def engine(self):
        if self._engine is None:
            engine_url = sqlalchemy.engine.make_url(self.backend.database_url)
            # Hardcode the specific SQLAlchemy dialect we want to use: this is the
            # dialect the query engine will have been written for and tested with and we
            # don't want to allow global config changes to alter this
            engine_url._get_entrypoint = lambda: self.sqlalchemy_dialect
            self._engine = sqlalchemy.create_engine(engine_url, future=True)
            # The above relies on abusing SQLAlchemy internals so it's possible it will
            # break in future -- we want to know immediately if it does
            assert isinstance(self._engine.dialect, self.sqlalchemy_dialect)
        return self._engine

    def create_codelist_table(self, codelist):
        """
        Given a codelist, build a SQLAlchemy representation of the temporary table
        needed to store that codelist and then generate the queries necessary to create
        and populate that tables
        """
        codes = codelist.codes
        max_code_len = max(map(len, codes))
        collation = "Latin1_General_BIN"
        table_name = self.get_temp_table_name("codelist")
        table = sqlalchemy.Table(
            table_name,
            sqlalchemy.MetaData(),
            sqlalchemy.Column(
                "code",
                sqlalchemy.types.String(max_code_len, collation=collation),
                nullable=False,
            ),
            sqlalchemy.Column(
                "system",
                sqlalchemy.types.String(6),
                nullable=False,
            ),
            # If this backend has a temp db, we use it to store codelists
            # tables. This helps with permissions management, as we can have
            # write acces to the temp db but not the main db
            schema=self.get_temp_database(),
        )
        # Constuct the queries needed to create and populate this table
        queries = [sqlalchemy.schema.CreateTable(table)]
        for codes_batch in split_list_into_batches(
            codes, size=self.max_rows_per_insert
        ):
            insert_query = table.insert().values(
                [(code, codelist.system) for code in codes_batch]
            )
            queries.append(insert_query)
        return table, queries

    def get_temp_table_name(self, name_hint):
        """
        Return a table name based on `name_hint` suitable for use as a temporary table.

        `name_hint` is arbitrary and is only present to make the resulting SQL slightly
        more comprehensible when debugging.
        """
        self.temp_table_count += 1
        return f"{self.temp_table_prefix}{name_hint}_{self.temp_table_count}"

    def get_temp_database(self):
        """Which schema/database should we write temporary tables to."""
        return None

    def get_population_table_query(self, population):
        """Build the query that selects the patient population we're interested in"""
        is_included = self.get_value_expression(population)
        tables = get_referenced_tables(is_included)
        assert len(tables) == 1
        population_table = tables[0]
        return (
            sqlalchemy.select([population_table.c.patient_id.label("patient_id")])
            .select_from(population_table)
            .where(is_included == True)  # noqa: E712
        )

    def build_condition_statement(self, comparator):
        """
        Traverse a comparator's left and right hand sides in order and build the nested
        condition statement along with a tuple of the tables referenced
        """
        if comparator.connector is not None:
            assert isinstance(comparator.lhs, Comparator) and isinstance(
                comparator.rhs, Comparator
            )
            left_conditions = self.build_condition_statement(comparator.lhs)
            right_conditions = self.build_condition_statement(comparator.rhs)
            connector = getattr(sqlalchemy, comparator.connector)
            condition_statement = connector(left_conditions, right_conditions)
        else:
            lhs = self.get_value_expression(comparator.lhs)
            method = getattr(lhs, comparator.operator)
            condition_statement = method(comparator.rhs)

        if comparator.negated:
            condition_statement = sqlalchemy.not_(condition_statement)

        return condition_statement

    def get_value_expression(self, value):
        """
        Caching wrapper around `get_value_expression_no_cache()` below

        This is a peformance enhancement, not for the Python code, but rather for the
        SQL we generate. It ensures that we don't get needlessly complex (though
        correct) SQL by generating duplicated temporary tables or table clauses.
        """
        # Plain values don't require cached responses and as they may be mutable types
        # like lists we can't easily cache them in any case. It's only QueryNodes that
        # we want to cache.
        if not isinstance(value, QueryNode):
            return self.get_value_expression_no_cache(value)
        elif value in self.value_expression_cache:
            return self.value_expression_cache[value]
        else:
            result = self.get_value_expression_no_cache(value)
            self.value_expression_cache[value] = result
            return result

    @singledispatchmethod_with_unions
    def get_value_expression_no_cache(self, value):
        """
        Given a "value" from the Query Model, convert it to a SQLAlchemy expression, or
        at least something usable by SQLAlchemy.

        `value` can be anything that can be represented in our Query Model e.g. a table, a
        table with some filters applied, a codelist, a column from a table, and so on.
        It could also be simple static value like a date or an integer. Whatever it is,
        we need to return its appropriate SQLAlchemy representation.

        Most of the interesting logic happens when `value` is a subclass of QueryNode
        i.e. not just a plain old integer or date or whatever. These are handled in the
        methods below which dispatch on the type of node.
        """
        # This method is the fallback for types not explicitly handled below, which
        # means "plain value" types like integers and dates which we just return
        # unchanged because SQLAlchemy knows how to handle them. Ideally, we'd have a
        # fat union type covering all of these and an explicit method to handle them
        # (leaving the fallback to just raise a TypeError). But given that we handle not
        # only numbers, strings, dates etc but also list and tuples of these values it
        # gets messy quite fast so for now we just make sure that whatever we've been
        # passed *isn't* a QueryNode.
        assert not isinstance(value, QueryNode)
        return value

    @get_value_expression_no_cache.register
    def get_expression_for_category_node(self, value: ValueFromCategory):
        category_mapping = {}
        for label, category_definition in value.definitions.items():
            # A category definition is always a single Comparator, which may contain
            # nested Comparators
            condition_statement = self.build_condition_statement(category_definition)
            category_mapping[label] = condition_statement
        return self.get_case_expression(category_mapping, value.default)

    @get_value_expression_no_cache.register
    def get_expression_for_base_table(self, node: Table):
        table = self.backend.get_table_expression(node.name)
        return table.select()

    @get_value_expression_no_cache.register
    def get_expression_for_filtered_table(self, node: FilteredTable):
        query = self.get_value_expression(node.source)
        return self.apply_filter(query, node)

    @get_value_expression_no_cache.register
    def get_expression_for_row_selector(self, node: Row):
        query = self.get_value_expression(node.source)
        query = self.apply_row_selector(
            query,
            sort_columns=node.sort_columns,
            descending=node.descending,
        )
        return self.reify_query(query)

    @get_value_expression_no_cache.register
    def get_expression_for_row_from_aggregate(self, node: RowFromAggregate):
        query = self.get_value_expression(node.source)
        query = self.apply_aggregates(query, [node])
        return self.reify_query(query)

    def reify_query(self, query):
        """
        Take a SQLAlchemy query and return something table-like which contains the
        results of this query.

        At present, we do this via creating a temporary table and writing the results of
        the query to that table. But this is an implementation detail, chosen for its
        performance characteristics. It's possible to replace the below with either of:

            return query.cte()
            return query.subquery()

        and the tests will still pass.
        """
        columns = [sqlalchemy.Column(c.name, c.type) for c in query.selected_columns]
        table_name = self.get_temp_table_name("group_table")
        table = sqlalchemy.Table(
            table_name,
            sqlalchemy.MetaData(),
            *columns,
        )
        populate_table_query = self.write_query_to_table(table, query)
        self.temp_tables[table] = [populate_table_query]
        return table

    @get_value_expression_no_cache.register
    def get_expression_for_output_node(
        self, node: Union[ValueFromRow, ValueFromAggregate, Column]
    ):
        table = self.get_value_expression(node.source)
        return table.c[node.column]

    @get_value_expression_no_cache.register
    def get_expression_for_codelist(self, codelist: Codelist):
        table, queries = self.create_codelist_table(codelist)
        self.temp_tables[table] = queries
        return sqlalchemy.select(table.c.code).scalar_subquery()

    @get_value_expression_no_cache.register
    def get_expression_for_value_from_function(self, value: ValueFromFunction):
        # TODO: I'd quite like to build this map by decorating the methods e.g.
        #
        #   @handler_for(DateDifferenceInYears)
        #   def my_handle_fun(...)
        #
        # but the simple thing will do for now.
        class_method_map = {
            DateDifferenceInYears: self.date_difference_in_years,
            RoundToFirstOfMonth: self.round_to_first_of_month,
            RoundToFirstOfYear: self.round_to_first_of_year,
        }

        assert value.__class__ in class_method_map, f"Unsupported function: {value}"

        method = class_method_map[value.__class__]
        argument_expressions = [
            self.get_value_expression(arg) for arg in value.arguments
        ]
        return method(*argument_expressions)

    def date_difference_in_years(self, start_date, end_date):
        start_date = type_coerce(start_date, sqlalchemy_types.Date())
        end_date = type_coerce(end_date, sqlalchemy_types.Date())

        # We do the arithmetic ourselves, to be portable across dbs.
        start_year = sqlalchemy.func.year(start_date)
        start_month = sqlalchemy.func.month(start_date)
        start_day = sqlalchemy.func.day(start_date)

        end_year = sqlalchemy.func.year(end_date)
        end_month = sqlalchemy.func.month(end_date)
        end_day = sqlalchemy.func.day(end_date)

        year_diff = end_year - start_year

        date_diff = sqlalchemy.case(
            (end_month > start_month, year_diff),
            (
                sqlalchemy.and_(end_month == start_month, end_day >= start_day),
                year_diff,
            ),
            else_=year_diff - 1,
        )
        return type_coerce(date_diff, sqlalchemy_types.Integer())

    def round_to_first_of_month(self, date):
        raise NotImplementedError

    def round_to_first_of_year(self, date):
        raise NotImplementedError

    def get_case_expression(self, mapping, default):
        return sqlalchemy.case(
            [(expression, label) for label, expression in mapping.items()],
            else_=default,
        )

    def apply_aggregates(self, query, aggregate_nodes):
        """
        For each aggregate node, get the query that will select it with its generated
        column label, plus the patient id column, and then group by the patient id.
        """
        columns = [
            self.get_aggregate_column(query, aggregate_node)
            for aggregate_node in aggregate_nodes
        ]
        query = query.with_only_columns([query.selected_columns.patient_id] + columns)
        query = query.group_by(query.selected_columns.patient_id)

        return query

    def get_aggregate_column(self, query, aggregate_node):
        """
        For an aggregate node, build the column to hold its value
        Aggregate column names are a combination of column and aggregate function,
        e.g. "patient_id_exists"
        """
        output_column = aggregate_node.output_column
        if aggregate_node.function == "exists":
            return sqlalchemy.literal(True).label(output_column)
        else:
            # The aggregate node function is a string corresponding to an available
            # sqlalchemy function (e.g. "exists", "count")
            function = getattr(sqlalchemy.func, aggregate_node.function)
            source_column = query.selected_columns[aggregate_node.input_column]
            return function(source_column).label(output_column)

    def apply_filter(self, query, filter_node):
        # Get the base table
        table_expr = get_primary_table(query)

        column_name = filter_node.column
        operator_name = filter_node.operator
        value_expr = self.get_value_expression(filter_node.value)

        # If the filter value itself potentially drawn from another table?
        if isinstance(filter_node.value, (Value, Column)):
            # Find the tables to which it refers
            other_tables = get_referenced_tables(value_expr)
            # If we have a "Value" (i.e. a single value per patient) then we
            # include the other tables in the join
            if isinstance(filter_node.value, Value):
                for other_table in other_tables:
                    query = self.include_joined_table(query, other_table)
            # If we have a "Column" (i.e. multiple values per patient) then we
            # can't directly join this with our single-value-per-patient query,
            # so we have to use a correlated subquery
            elif isinstance(filter_node.value, Column):
                # I actually think this check is wrong and we'll eventually need to
                # support e.g. a column which is a boolean expression over multiple
                # source columns. But I'll leave it in place for now.
                assert len(other_tables) == 1
                other_table = other_tables[0]
                value_expr = (
                    sqlalchemy.select(value_expr)
                    .select_from(other_table)
                    .where(other_table.c.patient_id == table_expr.c.patient_id)
                )
            else:
                assert False

        if isinstance(filter_node.value, Codelist) and "system" in table_expr.c:
            # Codelist queries must also match on `system` column if it's present
            system_column = table_expr.c["system"]
            value_expr = value_expr.where(system_column == filter_node.value.system)

        column = table_expr.c[column_name]
        method = getattr(column, operator_name)
        query_expr = method(value_expr)

        if filter_node.or_null:
            null_expr = column.__eq__(None)
            query_expr = sqlalchemy.or_(query_expr, null_expr)
        return query.where(query_expr)

    @staticmethod
    def apply_row_selector(query, sort_columns, descending):
        """
        Generate query to apply a row selector by sorting by sort_columns in
        specified direction, and then selecting the first row
        """
        # Get the base table - the first in the FROM clauses
        table_expr = get_primary_table(query)

        # Find all the selected column names
        column_names = [column.name for column in query.selected_columns]

        # Query to select the columns that we need to sort on
        order_columns = [table_expr.c[column] for column in sort_columns]
        # change ordering to descending on all order columns if necessary
        if descending:
            order_columns = [c.desc() for c in order_columns]

        # Number rows sequentially over the order by columns for each patient id
        row_num = (
            sqlalchemy.func.row_number()
            .over(order_by=order_columns, partition_by=table_expr.c.patient_id)
            .label("_row_num")
        )
        # Add the _row_num column and select just the first row
        query = query.add_columns(row_num)
        subquery = query.alias()
        query = sqlalchemy.select([subquery.c[column] for column in column_names])
        query = query.select_from(subquery).where(subquery.c._row_num == 1)
        return query

    @staticmethod
    def include_joined_table(query, table):
        tables = get_joined_tables(query)
        if table in tables:
            return query
        join = sqlalchemy.join(
            query.get_final_froms()[0],
            table,
            query.selected_columns.patient_id == table.c.patient_id,
            isouter=True,
        )
        return query.select_from(join)

    def write_query_to_table(self, table, query):
        """
        Returns a new query which, when executed, writes the results of `query`
        into `table`
        """
        raise NotImplementedError()


def split_list_into_batches(lst, size=None):
    # If no size limit specified yield the whole list in one batch
    if size is None:
        yield lst
    else:
        for i in range(0, len(lst), size):
            yield lst[i : i + size]
