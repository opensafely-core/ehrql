import datetime
import secrets
from functools import cached_property

import sqlalchemy
import sqlalchemy.engine.interfaces
import structlog
from sqlalchemy import distinct
from sqlalchemy.sql import operators
from sqlalchemy.sql.elements import BindParameter, ColumnClause
from sqlalchemy.sql.functions import Function as SQLFunction
from sqlalchemy.sql.visitors import replacement_traverse

from ehrql.backends.base import DefaultSQLBackend
from ehrql.query_model.nodes import (
    AggregateByPatient,
    Case,
    Filter,
    Function,
    InlinePatientTable,
    Position,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    Sort,
    Value,
    get_domain,
    get_sorts,
    get_table_and_filters,
    has_many_rows_per_patient,
)
from ehrql.query_model.transforms import (
    PickOneRowPerPatientWithColumns,
    apply_transforms,
)
from ehrql.sqlalchemy_types import type_from_python_type
from ehrql.utils.functools_utils import singledispatchmethod_with_cache
from ehrql.utils.sqlalchemy_query_utils import (
    GeneratedTable,
    InsertMany,
    get_setup_and_cleanup_queries,
    is_predicate,
)

from .base import BaseQueryEngine


log = structlog.getLogger()


class BaseSQLQueryEngine(BaseQueryEngine):
    sqlalchemy_dialect: sqlalchemy.engine.interfaces.Dialect

    global_unique_id: str
    counter = 0
    population_table = None
    # The maximum length of a multi-valued parameter (as used in `x IN (y)` queries)
    # before we restructure the query to use a temporary table to hold the parameters.
    # The default is chosen pretty much arbitrarily: Cohort Extractor _always_ used
    # temporary tables for these kinds of query but that seems a bit unncessary for
    # small lists.
    max_multivalue_param_length = 32

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.backend:
            self.backend = DefaultSQLBackend(self.__class__)
        # Supporting generating globally unique names – the timestamp is not strictly
        # necessary but can help with debugging and manual cleanup
        self.global_unique_id = (
            f"{datetime.datetime.utcnow():%Y%m%d_%H%M}_{secrets.token_hex(6)}"
        )
        if max_length := self.config.get("EHRQL_MAX_MULTIVALUE_PARAM_LENGTH"):
            self.max_multivalue_param_length = int(max_length)

    def get_next_id(self):
        # Support generating names unique within this session
        self.counter += 1
        return self.counter

    def get_query(self, variable_definitions):
        """
        Return the SQL query to fetch the results for `variable_definitions`

        Note that this query might make use of intermediate tables. The SQL queries
        needed to create these tables and clean them up can be retrieved by calling
        `get_setup_and_cleanup_queries` on the query object.
        """
        variable_definitions = self.backend.modify_query_variables(variable_definitions)
        variable_definitions = apply_transforms(variable_definitions)

        # Generate a table containing the IDs all of patients matching the population
        # definition
        population_expression = self.get_predicate(variable_definitions["population"])
        select_patient_id = self.select_patient_id_for_population(population_expression)
        population_query = select_patient_id.where(population_expression)
        population_query = apply_patient_joins(population_query)
        population_table = self.reify_query(population_query)
        # Store a reference to the population table so that we can use it while
        # generating the variable expressions below
        self.population_table = population_table

        variable_expressions = {
            name: self.get_expr(definition)
            for name, definition in variable_definitions.items()
            if name != "population"
        }
        query = sqlalchemy.select(population_table.c.patient_id)
        # Replace any placeholder table references in the population query
        query = self.replace_placeholder_table_references(query)
        query = query.add_columns(
            *[expr.label(name) for name, expr in variable_expressions.items()]
        )
        query = apply_patient_joins(query)

        # We use an instance variable to store the population table in order to avoid
        # having to thread it through all our `get_sql`/`get_table` method calls. But
        # this means that we can't safely re-use cached values across different calls to
        # `get_query()` because the same query node may now generate different SQL
        # depending on the population of the query to which it belongs. So we have to
        # reset the caches and the population table reference.
        self.population_table = None
        self.get_sql.cache_clear()
        self.get_table.cache_clear()

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
            id_selects = [
                sqlalchemy.select(table.c.patient_id.label("patient_id"))
                for table in tables
            ]
            # Create a table which contains the union of all these IDs. (Note UNION
            # rather than UNION ALL so we don't get duplicates.)
            all_ids_table = self.reify_query(sqlalchemy.union(*id_selects))
            return sqlalchemy.select(all_ids_table.c.patient_id)
        elif len(tables) == 1:
            # If there's only one table then use the IDs from that
            return sqlalchemy.select(tables[0].c.patient_id.label("patient_id"))
        else:
            # Gracefully handle the degenerate case where the population expression
            # doesn't reference any tables at all. Our validation rules ensure that such
            # an expression will never evaluate True so the population will always be
            # empty. But we can at least return an empty result, rather than blowing up.
            return sqlalchemy.select(sqlalchemy.literal(0).label("patient_id"))

    # Some databases care about the distinction between "predicates" (expressions which
    # are guaranteed boolean-typed by virtue of their syntax) and other forms of
    # expression. As these are semantically equivalent we can transform from one to the
    # other, we just need to know which one we're expecting in a context.
    def get_expr(self, node):
        sql = self.get_sql(node)
        return self.predicate_to_expression(sql) if is_predicate(sql) else sql

    def get_predicate(self, node):
        sql = self.get_sql(node)
        return self.expression_to_predicate(sql) if not is_predicate(sql) else sql

    def predicate_to_expression(self, sql):
        # Using the expression twice in the CASE statement is a bit inelegant, but I
        # can't immediately think of another way of doing this which preserves the
        # nullability of the expression (which `case((sql, True), else_=False)` doesnt'
        # do).
        return sqlalchemy.case((sql, True), (~sql, False))

    def expression_to_predicate(self, sql):
        return operators.eq(sql, True)

    # Without caching here we emit unnecessarily verbose and duplicative SQL because any
    # nodes which generate CTEs or temporary tables end up generating new ones each time
    # they're referenced — we want to generate them only once and then reuse them
    @singledispatchmethod_with_cache
    def get_sql(self, node):
        assert False, f"Unhandled node: {node}"

    @get_sql.register(Value)
    def get_sql_value(self, node):
        if isinstance(node.value, frozenset):
            value = tuple(self.convert_value(v) for v in node.value)
        else:
            value = self.convert_value(node.value)
        return sqlalchemy.literal(value)

    def convert_value(self, value):
        if hasattr(value, "_to_primitive_type"):
            return value._to_primitive_type()
        else:
            return value

    @get_sql.register(Function.EQ)
    def get_sql_eq(self, node):
        return operators.eq(self.get_expr(node.lhs), self.get_expr(node.rhs))

    @get_sql.register(Function.NE)
    def get_sql_ne(self, node):
        return operators.ne(self.get_expr(node.lhs), self.get_expr(node.rhs))

    @get_sql.register(Function.IsNull)
    def get_sql_is_null(self, node):
        return operators.is_(self.get_expr(node.source), None)

    @get_sql.register(Function.In)
    def get_sql_in(self, node):
        lhs = self.get_expr(node.lhs)
        is_series, rhs = self.get_expr_for_multivalued_param(node.rhs)
        if not is_series:
            # This is a simple is_in, with either a set of Values, or a
            # (large) set of values converted to a temporary table with
            # a single column (i.e. a codelist)
            return lhs.in_(rhs)
        else:
            if self.population_table is not None:
                patient_id = self.population_table.c.patient_id
            else:
                # if we don't know what the population table is, generate
                # a placeholder table for it
                placeholder_name = f"patients_{secrets.token_hex(6)}"
                table = sqlalchemy.Table(
                    placeholder_name,
                    sqlalchemy.MetaData(),
                    sqlalchemy.Column("patient_id"),
                )
                # Add a flag to the user metadata so we can identify these tables later
                table.is_placeholder = True
                table_query = sqlalchemy.select(table.c.patient_id.label("patient_id"))
                patient_id = table_query.c.patient_id
            return self.in_series_exists_query(rhs, lhs, patient_id)

    def in_series_exists_query(self, rhs, lhs, patient_id):
        return (
            sqlalchemy.select(None)
            .where(rhs.c.patient_id == patient_id, rhs.c[1] == lhs)
            .exists()
        )

    def get_expr_for_multivalued_param(self, node):
        is_series = isinstance(node, AggregateByPatient.CombineAsSet)
        if is_series:
            return is_series, self.get_expr(node)
        assert isinstance(node, Value)
        assert isinstance(node.value, frozenset)
        if len(node.value) <= self.max_multivalue_param_length:
            return is_series, self.get_expr(node)
        else:
            table = self.get_table(node.value)
            return is_series, sqlalchemy.select(table.columns[0])

    @get_sql.register(Function.Not)
    def get_sql_not(self, node):
        return sqlalchemy.not_(self.get_predicate(node.source))

    @get_sql.register(Function.And)
    def get_sql_and(self, node):
        return sqlalchemy.and_(
            self.get_predicate(node.lhs), self.get_predicate(node.rhs)
        )

    @get_sql.register(Function.Or)
    def get_sql_or(self, node):
        return sqlalchemy.or_(
            self.get_predicate(node.lhs), self.get_predicate(node.rhs)
        )

    @get_sql.register(Function.LT)
    def get_sql_lt(self, node):
        return operators.lt(self.get_expr(node.lhs), self.get_expr(node.rhs))

    @get_sql.register(Function.LE)
    def get_sql_le(self, node):
        return operators.le(self.get_expr(node.lhs), self.get_expr(node.rhs))

    @get_sql.register(Function.GT)
    def get_sql_gt(self, node):
        return operators.gt(self.get_expr(node.lhs), self.get_expr(node.rhs))

    @get_sql.register(Function.GE)
    def get_sql_ge(self, node):
        return operators.ge(self.get_expr(node.lhs), self.get_expr(node.rhs))

    @get_sql.register(Function.Negate)
    def get_sql_negate(self, node):
        return operators.neg(self.get_expr(node.source))

    @get_sql.register(Function.Add)
    def get_sql_add(self, node):
        return operators.add(self.get_expr(node.lhs), self.get_expr(node.rhs))

    @get_sql.register(Function.Subtract)
    def get_sql_subtract(self, node):
        return operators.sub(self.get_expr(node.lhs), self.get_expr(node.rhs))

    @get_sql.register(Function.Multiply)
    def get_sql_multiply(self, node):
        return operators.mul(self.get_expr(node.lhs), self.get_expr(node.rhs))

    @get_sql.register(Function.TrueDivide)
    def get_sql_truedivide(self, node):
        lhs = self.get_expr(node.lhs)
        rhs = self.get_expr(node.rhs)
        # To ensure TrueDiv behaviour cast one to float if both args are ints
        if not isinstance(lhs.type, sqlalchemy.Float) and not isinstance(
            rhs.type, sqlalchemy.Float
        ):
            lhs = sqlalchemy.cast(lhs, sqlalchemy.Float)
        return self.truedivide(lhs, rhs)

    def truedivide(self, lhs, rhs):
        return lhs / rhs

    @get_sql.register(Function.FloorDivide)
    def get_sql_floordivide(self, node):
        float_result = self.get_sql_truedivide(node)
        return sqlalchemy.cast(SQLFunction("FLOOR", float_result), sqlalchemy.Integer)

    def cast_to_int(self, value):
        return sqlalchemy.cast(value, sqlalchemy.Integer)

    @get_sql.register(Function.CastToInt)
    def get_sql_cast_to_int(self, node):
        return self.cast_to_int(self.get_expr(node.source))

    @get_sql.register(Function.CastToFloat)
    def get_sql_cast_to_float(self, node):
        return sqlalchemy.cast(self.get_expr(node.source), sqlalchemy.Float)

    @get_sql.register(Function.StringContains)
    def get_sql_string_contains(self, node):
        # Note: SQLAlchemy uses forward slash rather than backslash as its default
        # escape character (perhaps to avoid complications with nested escaping?) so we
        # follow its lead here
        haystack = self.get_expr(node.lhs)
        needle = self.get_expr(node.rhs)
        # Where the needle is a string literal (as it most often will be) we can avoid
        # some convoluted SQL by doing the escaping and wildcard wrapping in Python
        if isinstance(needle, BindParameter):
            escaped_needle = (
                needle.value.replace("/", "//").replace("%", "/%").replace("_", "/_")
            )
            return haystack.like(f"%{escaped_needle}%", escape="/")
        else:
            escaped_needle = self.string_replace(needle, "/", "//")
            escaped_needle = self.string_replace(escaped_needle, "%", "/%")
            escaped_needle = self.string_replace(escaped_needle, "_", "/_")
            return haystack.contains(escaped_needle, escape="/")

    def string_replace(self, value, pattern, replacement):
        return SQLFunction(
            "REPLACE", value, pattern, replacement, type_=sqlalchemy.String
        )

    @get_sql.register(Function.YearFromDate)
    def get_sql_year_from_date(self, node):
        return self.get_date_part(self.get_expr(node.source), "YEAR")

    @get_sql.register(Function.MonthFromDate)
    def get_sql_month_from_date(self, node):
        return self.get_date_part(self.get_expr(node.source), "MONTH")

    @get_sql.register(Function.DayFromDate)
    def get_sql_day_from_date(self, node):
        return self.get_date_part(self.get_expr(node.source), "DAY")

    @get_sql.register(Function.DateDifferenceInDays)
    def get_sql_date_difference_in_days(self, node):
        return self.date_difference_in_days(
            self.get_expr(node.lhs), self.get_expr(node.rhs)
        )

    def date_difference_in_days(self, end, start):
        raise NotImplementedError()

    @get_sql.register(Function.DateDifferenceInYears)
    def get_sql_date_difference_in_years(self, node):
        return self.date_difference_in_years(
            self.get_expr(node.lhs), self.get_expr(node.rhs)
        )

    def date_difference_in_years(self, end, start):
        year_diff = self.get_date_part(end, "YEAR") - self.get_date_part(start, "YEAR")
        month_diff = self.get_date_part(end, "MONTH") - self.get_date_part(
            start, "MONTH"
        )
        day_diff = self.get_date_part(end, "DAY") - self.get_date_part(start, "DAY")
        # The CASE condition below detects the situation where the end day-of-year is
        # earlier than the start day-of-year. In such cases we need to subtract one from
        # the year delta to give the number of whole years that has elapsed between the
        # two dates.
        #
        # The most obvious way to determine this duplicates calls to the "get month"
        # function:
        #
        #     end_month < start_month OR (end_month == start_month AND end_day < start_day)
        #
        # or equivalently:
        #
        #     month_diff < 0 OR (month_diff == 0 AND day_diff < 0)
        #
        # However this expression has a simplified form that takes advantage of the fact
        # that `day_diff` has a maximum magnitude of `30`:
        #
        #     month_diff * -31 > day_diff
        #
        # To satisfy yourself that these expressions are equivalent, consider this truth
        # table:
        #
        #      month_diff | day_diff | result
        #     ============|==========|========
        #          +ve    |    any   | false
        #     ------------|----------|--------
        #                 |    +ve   | false
        #                 |----------|--------
        #           0     |     0    | false
        #                 |----------|--------
        #                 |    -ve   | true
        #     ------------|----------|--------
        #          -ve    |    any   | true
        #
        # By inspection, this truth table is correct for both expressions and therefore
        # they are equivalent.
        return year_diff - sqlalchemy.case((month_diff * -31 > day_diff, 1), else_=0)

    @get_sql.register(Function.DateDifferenceInMonths)
    def get_sql_date_difference_in_months(self, node):
        return self.date_difference_in_months(
            self.get_expr(node.lhs), self.get_expr(node.rhs)
        )

    def date_difference_in_months(self, end, start):
        year_diff = self.get_date_part(end, "YEAR") - self.get_date_part(start, "YEAR")
        month_diff = self.get_date_part(end, "MONTH") - self.get_date_part(
            start, "MONTH"
        )
        part_month = self.get_date_part(end, "DAY") < self.get_date_part(start, "DAY")
        return year_diff * 12 + month_diff - sqlalchemy.case((part_month, 1), else_=0)

    def get_date_part(self, date, part):
        raise NotImplementedError()

    @get_sql.register(Function.DateAddDays)
    def get_sql_date_add_days(self, node):
        return self.date_add_days(self.get_expr(node.lhs), self.get_expr(node.rhs))

    def date_add_days(self, date, num_days):
        raise NotImplementedError()

    @get_sql.register(Function.DateAddMonths)
    def get_sql_date_add_months(self, node):
        return self.date_add_months(self.get_expr(node.lhs), self.get_expr(node.rhs))

    def date_add_months(self, date, num_months):
        raise NotImplementedError()

    @get_sql.register(Function.DateAddYears)
    def get_sql_date_add_years(self, node):
        return self.date_add_years(self.get_expr(node.lhs), self.get_expr(node.rhs))

    def date_add_years(self, date, num_years):
        raise NotImplementedError()

    @get_sql.register(Function.ToFirstOfYear)
    def get_sql_to_first_of_year(self, node):
        return self.to_first_of_year(self.get_expr(node.source))

    def to_first_of_year(self, date):
        raise NotImplementedError()

    @get_sql.register(Function.ToFirstOfMonth)
    def get_sql_to_first_of_month(self, node):
        return self.to_first_of_month(self.get_expr(node.source))

    def to_first_of_month(self, date):
        raise NotImplementedError()

    @get_sql.register(Function.MaximumOf)
    def get_sql_maximum_of(self, node):
        aggregate_function = self.aggregate_functions["maximum_of"]
        args = self.get_nary_function_args(node)
        return self.get_aggregate_subquery(aggregate_function, *args).label("greatest")

    @get_sql.register(Function.MinimumOf)
    def get_sql_minimum_of(self, node):
        aggregate_function = self.aggregate_functions["minimum_of"]
        args = self.get_nary_function_args(node)
        return self.get_aggregate_subquery(aggregate_function, *args).label("least")

    @property
    def aggregate_functions(self):
        return {
            "minimum_of": sqlalchemy.func.min,
            "maximum_of": sqlalchemy.func.max,
        }

    def get_aggregate_subquery(self, aggregate_function, columns, return_type):
        raise NotImplementedError()

    def get_nary_function_args(self, node):
        sources = [*node.sources]
        columns = [self.get_expr(s) for s in sources]
        types = {c.type for c in columns}
        return (columns, types.pop())

    @get_sql.register(SelectColumn)
    def get_sql_select_column(self, node):
        table = self.get_table(node.source)
        return table.c[node.name]

    @get_sql.register(Case)
    def get_sql_case(self, node):
        cases = [
            (self.get_predicate(condition), self.get_expr(value))
            for (condition, value) in node.cases.items()
        ]
        if node.default is not None:
            default = self.get_expr(node.default)
        else:
            default = None
        return sqlalchemy.case(*cases, else_=default)

    @get_sql.register(AggregateByPatient.Sum)
    def get_sql_sum(self, node):
        return self.aggregate_series_by_patient(node.source, sqlalchemy.func.sum)

    @get_sql.register(AggregateByPatient.Min)
    def get_sql_min(self, node):
        return self.aggregate_series_by_patient(node.source, sqlalchemy.func.min)

    @get_sql.register(AggregateByPatient.Max)
    def get_sql_max(self, node):
        return self.aggregate_series_by_patient(node.source, sqlalchemy.func.max)

    @get_sql.register(AggregateByPatient.Mean)
    def get_sql_mean(self, node):
        return self.aggregate_series_by_patient(node.source, self.calculate_mean)

    def calculate_mean(self, sql_expr):
        return SQLFunction("AVG", sql_expr, type_=sqlalchemy.Float)

    @get_sql.register(AggregateByPatient.CountDistinct)
    def get_sql_count_distinct(self, node):
        return sqlalchemy.func.coalesce(
            self.aggregate_series_by_patient(node.source, self.count_distinct),
            0,
        )

    @get_sql.register(AggregateByPatient.CountEpisodes)
    def get_sql_count_episodes(self, node):
        query = self.get_select_query_for_node_domain(node.source)
        date_expr = self.get_expr(node.source)
        query = query.where(date_expr.is_not(None))
        # Use a LAG window function to get the previous date to the current one
        previous_date_expr = sqlalchemy.func.lag(date_expr).over(
            partition_by=query.selected_columns.patient_id,
            order_by=date_expr,
        )
        # Get the difference between the two in days
        query = query.add_columns(
            self.date_difference_in_days(date_expr, previous_date_expr).label(
                "date_delta_days"
            )
        )
        query = apply_patient_joins(query)
        subquery = query.alias()
        # Filter the subquery to contain just those deltas which exceed the threshold
        outer_query = sqlalchemy.select(subquery.c.patient_id).where(
            (subquery.c.date_delta_days > node.maximum_gap_days)
            # We also need to include the first row (which has no previous row and hence
            # a delta of NULL) to avoid an off-by-one error
            | subquery.c.date_delta_days.is_(None)
        )
        # Count the number of threshold-exceeding rows for each patient
        return sqlalchemy.func.coalesce(
            self.apply_sql_aggregation(outer_query, sqlalchemy.func.count("*")),
            0,
        )

    def count_distinct(self, sql_expr):
        return SQLFunction("COUNT", distinct(sql_expr), type_=sqlalchemy.Integer)

    # `Exists` and `Count` are Frame-level (rather than Series-level) aggregations and
    # so have a different implementation. They can operate on both many- and
    # one-row-per-patient frames, and they are never NULL valued.
    @get_sql.register(AggregateByPatient.Exists)
    def get_sql_exists(self, node):
        if has_many_rows_per_patient(node.source):
            query = self.get_select_query_for_node_domain(node.source)
            # We don't need an aggregation function here: we just need all distinct
            # patient_ids
            query = query.distinct()
            query = apply_patient_joins(query)
            table = self.reify_query(query)
        else:
            table = self.get_table(node.source)
        return table.c.patient_id.is_not(None)

    @get_sql.register(AggregateByPatient.Count)
    def get_sql_count(self, node):
        if has_many_rows_per_patient(node.source):
            query = self.get_select_query_for_node_domain(node.source)
            count = self.apply_sql_aggregation(query, sqlalchemy.func.count("*"))
            return sqlalchemy.func.coalesce(count, 0)
        else:
            table = self.get_table(node.source)
            has_row = table.c.patient_id.is_not(None)
            return sqlalchemy.case((has_row, 1), else_=0)

    @get_sql.register(AggregateByPatient.CombineAsSet)
    def get_sql_combine_as_set(self, node):
        query = self.get_select_query_for_node_domain(node.source)
        query = query.add_columns(self.get_sql(node.source))
        table = self.reify_query(query)
        return table

    def aggregate_series_by_patient(self, source_node, aggregation_func):
        query = self.get_select_query_for_node_domain(source_node)
        aggregation_expr = aggregation_func(self.get_expr(source_node))
        return self.apply_sql_aggregation(query, aggregation_expr)

    def apply_sql_aggregation(self, query, aggregation_expression):
        query = query.add_columns(aggregation_expression.label("value"))
        query = query.group_by(query.selected_columns[0])
        query = apply_patient_joins(query)
        aggregated_table = self.reify_query(query)
        return aggregated_table.c.value

    # The caching here is required for correctness: without it we can generate distinct
    # objects representing the same table and this confuses SQLAlchemy into generating
    # queries with ambiguous table references
    @singledispatchmethod_with_cache
    def get_table(self, node):
        assert False, f"Unhandled node: {node}"

    @get_table.register(SelectTable)
    @get_table.register(SelectPatientTable)
    def get_table_select_table(self, node):
        return self.backend.get_table_expression(node.name, node.schema)

    # We ignore Filter and Sort operations completely at this point in the code and just
    # pass the underlying table reference through. It's only later, when building the
    # SELECT query for a given Frame, that we make use of these. This is in order to
    # mirror the semantics of SQL whereby columns are selected directly from the
    # underlying table and filters and sorts are handled separately using WHERE/ORDER BY
    # clauses.
    @get_table.register(Sort)
    @get_table.register(Filter)
    def get_table_sort_and_filter(self, node):
        return self.get_table(node.source)

    def apply_order_clauses_modifications(self, node, order_clauses):
        # Hook for subclasses to apply additional modifications to the
        # order clauses if required
        return order_clauses

    @get_table.register(PickOneRowPerPatientWithColumns)
    def get_table_pick_one_row_per_patient(self, node):
        selected_columns = [self.get_expr(c) for c in node.selected_columns]
        order_clauses = [self.get_expr(c) for c in get_sort_conditions(node.source)]
        if node.position == Position.LAST:
            order_clauses = [c.desc() for c in order_clauses]
        order_clauses = self.apply_order_clauses_modifications(node, order_clauses)

        query = self.get_select_query_for_node_domain(node.source)
        query = query.add_columns(*selected_columns)
        # Add an extra "row number" column to the query which gives the position of each
        # row within its patient_id partition as implied by the order clauses
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
        partitioned_query = sqlalchemy.select(*output_columns).where(row_number == 1)

        return self.reify_query(partitioned_query)

    @get_table.register(InlinePatientTable)
    def get_table_inline_patient_table(self, node):
        # All tables have an implied `patient_id` column which is not explicitly
        # included in the schema
        column_types = [("patient_id", int)] + node.schema.column_types
        columns = [
            sqlalchemy.Column(name, **self.column_kwargs_for_type(col_type))
            for name, col_type in column_types
        ]
        return self.create_inline_table(columns, node.rows)

    @get_table.register(frozenset)
    def get_table_from_values(self, values):
        assert values, "`values` should never be empty"
        type_ = type(next(iter(values)))
        rows = [(self.convert_value(value),) for value in values]
        column_kwargs = self.backend.column_kwargs_for_type(type_)
        column_type = column_kwargs.pop("type_")

        # Set the appropriate maximum length for string types (which we know because we
        # have all the values upfront). We have to do this for MSSQL because if we try
        # to create an index on an unbounded VARCHAR we get the error:
        #
        #   Column 'X' in table 'Y' is of a type that is invalid for use as a key
        #   column in an index
        #   https://learn.microsoft.com/en-us/previous-versions/sql/sql-server-2008-r2/ms191241(v=sql.105)
        #
        # But there doesn't seem much harm in doing for all databases.
        if isinstance(column_type, sqlalchemy.String) and column_type.length is None:
            max_length = max(len(row[0]) for row in rows)
            column_type.length = max_length

        column = sqlalchemy.Column("value", type_=column_type, **column_kwargs)
        return self.create_inline_table([column], rows)

    def create_inline_table(self, columns, rows):
        table_name = f"inline_data_{self.get_next_id()}"
        table = GeneratedTable(
            table_name,
            sqlalchemy.MetaData(),
            *columns,
            prefixes=["TEMPORARY"],
        )
        table.setup_queries = [
            sqlalchemy.schema.CreateTable(table),
            InsertMany(table, rows),
            sqlalchemy.schema.CreateIndex(sqlalchemy.Index(None, table.c[0])),
        ]
        return table

    @classmethod
    def column_kwargs_for_type(cls, type_):
        """
        Given a Python type return the arguments needed to configure the corresponding
        SQLAlchemy `Column`

        By default, this is just the `type_` argument but subclasses may need to do
        something more sophisticated here.
        """
        return {"type_": type_from_python_type(type_)()}

    def reify_query(self, query):
        """
        By "reify" we just mean turning a SELECT query into something that can function
        as a table in other SQLAlchemy constructs. There are various ways to do this
        e.g. using `.alias()` to make a sub-query, using `.cte()` to make a Common Table
        Expression, or writing the results of the query to a temporary table.
        """
        return query.cte(name=f"cte_{self.get_next_id()}")

    def get_select_query_for_node_domain(self, node):
        """
        Given a many-rows-per-patient node, return the SELECT query corresponding to
        domain of that node
        """
        frame = get_domain(node).get_node()
        table_node, conditions = get_table_and_filter_conditions(frame)
        table = self.get_table(table_node)
        where_clauses = [self.get_predicate(condition) for condition in conditions]
        query = sqlalchemy.select(table.c.patient_id.label("patient_id"))
        # If we've already defined the population table (which we will have, other than
        # when we're still in the middle of compiling the population query) then we can
        # add an extra condition to our query which restricts it to just those
        # patient_ids present in the population. Where the query population is a small
        # fraction of the total population in the database this can result in some
        # dramatic speedups. As the fraction of the population increases this
        # improvement diminishes and where the population includes all (or almost all)
        # possible patients including this condition will make things slower. Initial
        # testing seems to show that the speedups are so significant, and the slowdowns
        # rare and mild enough, that this is still a net benefit but we'll need to keep
        # this under review.
        if self.population_table is not None:
            where_clauses.append(
                table.c.patient_id.in_(
                    sqlalchemy.select(self.population_table.c.patient_id)
                )
            )
        if where_clauses:
            query = query.where(sqlalchemy.and_(*where_clauses))
        return query

    def get_results(self, variable_definitions):
        results_query = self.get_query(variable_definitions)
        setup_queries, cleanup_queries = get_setup_and_cleanup_queries(results_query)
        with self.engine.connect() as connection:
            for i, setup_query in enumerate(setup_queries, start=1):
                log.info(f"Running setup query {i:03} / {len(setup_queries):03}")
                connection.execute(setup_query)

            log.info("Fetching results")
            cursor_result = connection.execute(results_query)
            try:
                yield from cursor_result
            except Exception:  # pragma: no cover
                # If we hit an error part way through fetching results then we should
                # close the cursor to make it clear we're not going to be fetching any
                # more (only really relevant for the in-memory SQLite tests, but good
                # hygiene in any case)
                cursor_result.close()
                # Make sure the cleanup happens before raising the error
                raise

            for i, cleanup_query in enumerate(cleanup_queries, start=1):
                log.info(f"Running cleanup query {i:03} / {len(cleanup_queries):03}")
                connection.execute(cleanup_query)

    @cached_property
    def engine(self):
        # Insert the specific SQLAlchemy dialect we want to use into the dialect
        # registry: this is the dialect the query engine will have been written for and
        # tested with and we don't want to allow global config changes to alter this
        dialect_name = self.sqlalchemy_dialect.__name__
        sqlalchemy.dialects.registry.impls[dialect_name] = self.sqlalchemy_dialect
        engine_url = sqlalchemy.engine.make_url(self.dsn).set(drivername=dialect_name)
        engine = sqlalchemy.create_engine(engine_url)
        # The above relies on abusing SQLAlchemy internals so it's possible it will
        # break in future — we want to know immediately if it does
        assert isinstance(engine.dialect, self.sqlalchemy_dialect)
        return engine

    def replace_placeholder_table_references(self, query):
        pop_table_id_column = self.population_table.c["patient_id"]
        return replacement_traverse(
            query,
            {},
            replace=lambda obj: pop_table_id_column
            if isinstance(obj, ColumnClause)
            and obj.name == "patient_id"
            and getattr(obj.table, "is_placeholder", False)
            else None,
        )


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
    join_key_name = join_key.key
    # The table referenced by `join_key`, and any tables already explicitly joined with
    # it, will be returned as the first value from the `get_final_froms()` method
    # (because `join_key` is the first column). Any remaining tables which aren't yet
    # explicitly joined on will be returned as additional clauses in the list. The best
    # explanation of SQLAlchemy's behaviour here is probably this:
    # https://docs.sqlalchemy.org/en/14/changelog/migration_14.html#change-4737
    implicit_joins = query.get_final_froms()[1:]
    for table in implicit_joins:
        query = query.join(table, table.c[join_key_name] == join_key, isouter=True)
    return query


def get_table_and_filter_conditions(frame):
    """
    Given a ManyRowsPerPatientFrame, return a base SelectTable operation and a list of
    filter conditions (or predicates) to be applied
    """
    filters, root_frame = get_table_and_filters(frame)
    return root_frame, [f.condition for f in filters]


def get_sort_conditions(frame):
    """
    Given a sorted frame, return a tuple of Series which gives the sort order
    """
    # Sort operations are given to us in order of application which is the reverse of
    # order of priority (i.e. the most recently applied sort gives us the primary sort
    # condition) so we reverse them here
    return tuple(s.sort_by for s in reversed(get_sorts(frame)))


def get_cyclic_coalescence(columns):
    """
    Given a list of columns, this produces a list of coalescences of all columns with the
    first input to coalesce at each index being the column at the index in the input columns
    """
    # Some SQL engines (sqlite, trino), aggregate functions return NULL if any of the
    # inputs are NULL. This cyclic coalescence allows us to get rid of any null values, but
    # retain valid empty strings.
    # Coalesce returns the first non-null value in a list; by cycling through the list and
    # calling coalesce with each item as the first value, we end up calling the aggregate
    # function only on the non-null values
    # e.g.
    # cols = ["a", "b", None, ""]
    # column_cycles = [
    #   ["a", "b", None, ""],
    #   ["b", None, "", "a"],
    #   [None, "", "a", "b"]
    #   ["", "a", "b", None]
    # ]
    # Calling coalesce on each of these returns ["a", "b", "a", "a"] to be used in the
    # aggregate function
    len_cols = len(columns)
    # if there is only one column in the list, just return it. Coalesce requires at least two
    # arguments
    if len_cols == 1:
        return columns
    column_cycles = [[*columns[i:], *columns[:i]] for i in range(len_cols)]
    return [sqlalchemy.func.coalesce(*c) for c in column_cycles]
