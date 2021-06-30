import sqlalchemy
import sqlalchemy.dialects.mssql

from ..query_language import Table
from .base import BaseQueryEngine


def make_table_expression(table_name, columns):
    """
    Return a SQLAlchemy object representing a table with the given name and
    columns
    """
    return sqlalchemy.Table(
        table_name,
        sqlalchemy.MetaData(),
        *[sqlalchemy.Column(column) for column in columns],
    )


def get_joined_tables(query):
    """
    Given a query object return a list of all tables referenced
    """
    tables = []
    from_exprs = list(query.froms)
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


class MssqlQueryEngine(BaseQueryEngine):

    sqlalchemy_dialect = sqlalchemy.dialects.mssql

    def __init__(self, column_definitions, backend):
        super().__init__(column_definitions, backend)
        self.output_group_tables = {}
        self.output_group_tables_queries = {}

    def get_and_populate_output_group_tables(self, output_groups):
        # For each group of output nodes (nodes that produce a single output value),
        # make a table object representing a temporary table into which we will write the required
        # values
        for i, (group, output_nodes) in enumerate(output_groups.items()):
            table_name = f"group_table_{i}"
            columns = {self.get_output_column_name(output) for output in output_nodes}
            self.output_group_tables[group] = make_table_expression(
                table_name, {"patient_id"} | columns
            )

        # For each group of output nodes, build a query expression
        # to populate the associated temporary table
        self.output_group_tables_queries = {
            group: self.get_query_expression(output_nodes)
            for group, output_nodes in output_groups.items()
        }

    def get_select_expression(self, base_table, columns):
        # every table must have a patient_id column; select it and the specified columns
        columns = sorted({"patient_id"}.union(columns))
        table_expr = self.backend.get_table_expression(base_table.name)
        column_objs = [table_expr.c[column] for column in columns]
        query = sqlalchemy.select(column_objs).select_from(table_expr)
        return query

    def get_query_expression(self, output_nodes):
        # output_nodes must all be of the same group so we arbitrarily use the
        # first one
        output_type, query_node = self.get_type_and_source(output_nodes[0])

        # Queries (currently) always have a linear structure so we can
        # decompose them into a list
        node_list = self.get_node_list(query_node)
        # The start of the list should always be an unfiltered Table
        base_table = node_list.pop(0)
        assert isinstance(base_table, Table)

        # TODO For now, we only deal with selecting columns, will need to add filters and aggregates
        selected_columns = {node.column for node in output_nodes}
        query = self.get_select_expression(base_table, selected_columns)

        return query

    def get_population_table_query(self, population_table_name=None):
        # TODO currently just select all patients
        population_table_name = population_table_name or "practice_registrations"
        population_table = make_table_expression(population_table_name, {"PatientId"})
        return sqlalchemy.select(
            [population_table.c.PatientId.label("patient_id")]
        ).select_from(population_table)

    def get_value_expression(self, value):
        # Every value is an output node at the moment
        table = self.output_group_tables[self.get_type_and_source(value)]
        column = self.get_output_column_name(value)
        value_expr = table.c[column]
        return value_expr, table

    @staticmethod
    def include_joined_table(query, table):
        if table.name in [t.name for t in get_joined_tables(query)]:
            return query
        join = sqlalchemy.join(
            query.froms[0],
            table,
            query.selected_columns.patient_id == table.c.patient_id,
            isouter=True,
        )
        return query.select_from(join)

    def generate_results_query(self):
        column_definitions = self.column_definitions.copy()
        # `population` is a special-cased boolean column, it doesn't appear
        # itself in the output but it determines what rows are included
        # TODO Currently just uses a default population table and expression
        # Build the base results table from the population table
        results_query = self.get_population_table_query()

        # Build big JOIN query which selects the results
        for column_name, output_node in column_definitions.items():
            column, table = self.get_value_expression(output_node)
            results_query = self.include_joined_table(results_query, table)
            results_query = results_query.add_columns(column.label(column_name))
        return results_query

    def get_sql(self):
        """Build the SQL"""
        self.get_and_populate_output_group_tables(self.output_groups)
        sql = []
        # Generate each of the interim output group tables and populate them
        for group, table in self.output_group_tables.items():
            query = self.output_group_tables_queries[group]
            query_sql = self.query_expression_to_sql(query)
            sql.append(f"SELECT * INTO {table.name} FROM (\n{query_sql}\n) t")
        # Add the big query that creates the base population table and its columns,
        # selected from the output group tables
        sql.append(self.query_expression_to_sql(self.generate_results_query()))
        return "\n\n\n".join(sql)

    def query_expression_to_sql(self, query):
        return str(
            query.compile(
                dialect=self.sqlalchemy_dialect.dialect(),
                compile_kwargs={"literal_binds": True},
            )
        )
