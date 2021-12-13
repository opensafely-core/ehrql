import contextlib
from typing import Optional, Union

import sqlalchemy
import sqlalchemy.dialects.mssql
import sqlalchemy.schema
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.sql import ClauseElement, Executable
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
from ..sqlalchemy_utils import (
    TemporaryTable,
    get_primary_table,
    get_referenced_tables,
    get_setup_and_cleanup_queries,
    include_joined_tables,
)
from .base import BaseQueryEngine


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

    # Use a simple counter to generate unique (per session) temporary table names
    temp_table_count: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # See docstring on `get_sql_element` for details on this
        self.sql_element_cache: dict[QueryNode, ClauseElement] = {}

    def get_queries(self) -> tuple[list[Executable], Executable, list[Executable]]:
        """
        Build the list of SQL queries to execute

        This is returned as a triple:

            list_of_setup_queries, query_to_fetch_results, list_of_cleanup_queries
        """
        # Convert each column definition to SQL
        column_queries = {
            column: self.get_sql_element(definition)
            for column, definition in self.column_definitions.items()
        }

        # `population` is a special-cased boolean column, it doesn't appear
        # itself in the output but it determines what rows are included
        population_query = column_queries.pop("population")

        # TODO: Why do we require just a single table here for the population?
        tables = get_referenced_tables(population_query)
        assert len(tables) == 1
        population_table = tables[0]

        # Start the query by selecting the "patint_id" column from all rows where the
        # "population" condition evaluates true
        results_query = (
            sqlalchemy.select([population_table.c.patient_id.label("patient_id")])
            .select_from(population_table)
            .where(population_query == True)  # noqa: E712
        )

        # For each column to be included in the output ...
        for column_name, column_query in column_queries.items():
            # Ensure the results_query JOINs on all the tables it needs to be able to
            # include this column in the output
            results_query = include_joined_tables(
                results_query, get_referenced_tables(column_query), "patient_id"
            )
            # Add this column to the final selected results using the supplied name
            results_query = results_query.add_columns(column_query.label(column_name))

        # Get all the setup queries needed to populate the various temporary tables used
        # by the results_query, and the queries needed to clean them up afterwards
        setup_queries, cleanup_queries = get_setup_and_cleanup_queries(results_query)

        return setup_queries, results_query, cleanup_queries

    @contextlib.contextmanager
    def execute_query(self):
        setup_queries, results_query, cleanup_queries = self.get_queries()
        with self.engine.connect() as cursor:
            for query in setup_queries:
                cursor.execute(query)

            yield cursor.execute(results_query)

            for query in cleanup_queries:
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
        and populate that table
        """
        codes = codelist.codes
        max_code_len = max(map(len, codes))
        collation = "Latin1_General_BIN"
        table_name = self.get_temp_table_name("codelist")
        table = TemporaryTable(
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
        create_query = sqlalchemy.schema.CreateTable(table)
        insert_queries = []
        for codes_batch in split_list_into_batches(
            codes, size=self.max_rows_per_insert
        ):
            insert_query = table.insert().values(
                [(code, codelist.system) for code in codes_batch]
            )
            insert_queries.append(insert_query)

        # Construct the queries needed to clean it up
        cleanup_queries = (
            [sqlalchemy.schema.DropTable(table, if_exists=True)]
            if self.temp_table_needs_dropping(create_query)
            else []
        )

        table.setup_queries = [create_query] + insert_queries
        table.cleanup_queries = cleanup_queries
        return table

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
            lhs = self.get_sql_element_or_value(comparator.lhs)
            method = getattr(lhs, comparator.operator)
            condition_statement = method(comparator.rhs)

        if comparator.negated:
            condition_statement = sqlalchemy.not_(condition_statement)

        return condition_statement

    def get_sql_element(self, node: QueryNode) -> ClauseElement:
        """
        Caching wrapper around `get_sql_element_no_cache()` below

        This is a peformance enhancement, not for the Python code, but rather for the
        SQL we generate. It ensures that we don't get needlessly complex (though
        correct) SQL by generating duplicated temporary tables or table clauses.
        """
        if node in self.sql_element_cache:
            return self.sql_element_cache[node]
        else:
            element = self.get_sql_element_no_cache(node)
            self.sql_element_cache[node] = element
            return element

    @singledispatchmethod_with_unions
    def get_sql_element_no_cache(self, node: QueryNode) -> ClauseElement:
        """
        Given a QueryNode object from the Query Model return the SQLAlchemy
        ClauseElement which represents it.

        This uses single dispatch to handle each type of QueryNode via the appropriate
        method below.
        """
        raise TypeError(f"Unhandled query node type: {node!r}")

    def get_sql_element_or_value(self, value):
        """
        Certain places in our Query Model support values which can either be QueryNodes
        themselves (which require resolving to SQL) or plain static values (booleans,
        integers, dates, list of dates etc) which we can return unchanged to SQLAlchemy.
        """
        if isinstance(value, QueryNode):
            return self.get_sql_element(value)
        else:
            return value

    @get_sql_element_no_cache.register
    def get_element_from_category_node(self, value: ValueFromCategory):
        category_mapping = {}
        for label, category_definition in value.definitions.items():
            # A category definition is always a single Comparator, which may contain
            # nested Comparators
            condition_statement = self.build_condition_statement(category_definition)
            category_mapping[label] = condition_statement
        return self.get_case_expression(category_mapping, value.default)

    @get_sql_element_no_cache.register
    def get_element_from_table(self, node: Table):
        table = self.backend.get_table_expression(node.name)
        return table.select()

    @get_sql_element_no_cache.register
    def get_element_from_filtered_table(self, node: FilteredTable):
        query = self.get_sql_element(node.source)
        filter_value = self.get_sql_element_or_value(node.value)
        return apply_filter(
            query,
            column=node.column,
            operator=node.operator,
            value=filter_value,
            # Ideally we wouldn't be passing these through, but we need to until we can
            # rewrite the `apply_filter` function
            value_query_node=node.value,
            or_null=node.or_null,
        )

    @get_sql_element_no_cache.register
    def get_element_from_row(self, node: Row):
        query = self.get_sql_element(node.source)
        query = self.select_first_row_per_partition(
            query,
            partition_column="patient_id",
            sort_columns=node.sort_columns,
            descending=node.descending,
        )
        return self.reify_query(query)

    @get_sql_element_no_cache.register
    def get_element_from_row_from_aggregate(self, node: RowFromAggregate):
        query = self.get_sql_element(node.source)
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
        table = TemporaryTable(
            table_name,
            sqlalchemy.MetaData(),
            *columns,
        )
        create_query = self.query_to_create_temp_table_from_select_query(table, query)
        cleanup_queries = (
            [sqlalchemy.schema.DropTable(table, if_exists=True)]
            if self.temp_table_needs_dropping(create_query)
            else []
        )
        table.setup_queries = [create_query]
        table.cleanup_queries = cleanup_queries
        return table

    @get_sql_element_no_cache.register
    def get_element_from_output_node(
        self, node: Union[ValueFromRow, ValueFromAggregate, Column]
    ):
        table = self.get_sql_element(node.source)
        return table.c[node.column]

    @get_sql_element_no_cache.register
    def get_element_from_codelist(self, codelist: Codelist):
        return self.create_codelist_table(codelist)

    @get_sql_element_no_cache.register
    def get_element_from_value_from_function(self, value: ValueFromFunction):
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
            self.get_sql_element_or_value(arg) for arg in value.arguments
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

    @staticmethod
    def select_first_row_per_partition(
        query, partition_column, sort_columns, descending
    ):
        """
        Given a SQLAlchemy SELECT query, partition it by the specified column, sort
        within each partition by `sort_columns` and then return a query containing just
        the first row for each partition.
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
            .over(order_by=order_columns, partition_by=table_expr.c[partition_column])
            .label("_row_num")
        )
        # Add the _row_num column and select just the first row
        query = query.add_columns(row_num)
        subquery = query.alias()
        query = sqlalchemy.select([subquery.c[column] for column in column_names])
        query = query.select_from(subquery).where(subquery.c._row_num == 1)
        return query

    def query_to_create_temp_table_from_select_query(
        self, table: TemporaryTable, select_query: Executable
    ) -> Executable:
        """
        Return a query to create `table` and populate it with the results of
        `select_query`
        """
        raise NotImplementedError()

    def temp_table_needs_dropping(self, create_table_query: Executable) -> bool:
        """
        Given the query used to create a temporary table, return whether the table needs
        to be explicitly dropped or whether the database will discard it automatically
        when the session terminates
        """
        raise NotImplementedError()


def apply_filter(query, column, operator, value, value_query_node, or_null=False):
    # TODO: This function needs work

    # Get the base table
    table_expr = get_primary_table(query)

    # Is the filter value itself potentially drawn from another table?
    if isinstance(value_query_node, (Value, Column)):
        # Find the tables to which it refers
        other_tables = get_referenced_tables(value)
        # If we have a "Value" (i.e. a single value per patient) then we
        # include the other tables in the join
        if isinstance(value_query_node, Value):
            query = include_joined_tables(query, other_tables, "patient_id")
        # If we have a "Column" (i.e. multiple values per patient) then we
        # can't directly join this with our single-value-per-patient query,
        # so we have to use a correlated subquery
        elif isinstance(value_query_node, Column):
            # I actually think this check is wrong and we'll eventually need to
            # support e.g. a column which is a boolean expression over multiple
            # source columns. But I'll leave it in place for now.
            assert len(other_tables) == 1
            other_table = other_tables[0]
            value = (
                sqlalchemy.select(value)
                .select_from(other_table)
                .where(other_table.c.patient_id == table_expr.c.patient_id)
            )
        else:
            assert False

    if isinstance(value_query_node, Codelist):
        value = sqlalchemy.select(value.c.code).scalar_subquery()
        if "system" in table_expr.c:
            # Codelist queries must also match on `system` column if it's present
            system_column = table_expr.c["system"]
            value = value.where(system_column == value_query_node.system)

    column_expr = table_expr.c[column]
    method = getattr(column_expr, operator)
    filter_expr = method(value)

    if or_null:
        null_expr = column_expr.__eq__(None)
        filter_expr = sqlalchemy.or_(filter_expr, null_expr)
    return query.where(filter_expr)


def split_list_into_batches(lst, size=None):
    # If no size limit specified yield the whole list in one batch
    if size is None:
        yield lst
    else:
        for i in range(0, len(lst), size):
            yield lst[i : i + size]
