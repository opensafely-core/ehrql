"""The interface between the DSL and the query language (semantic model)"""
from cohortextractor import query_language


class QueryBuilder:
    def __init__(self, table_name):
        self.table = query_language.table(table_name)

    def filter(self, *args, **kwargs):  # noqa: A003
        self.table = self.table.filter(*args, **kwargs)
        return self

    def select_column(self, column_name):
        return Column(self.table, column_name)


class Column:
    def __init__(self, table, column_name):
        self.table = table
        self.column_name = column_name

    def make_one_row_per_patient(self, reduce_function):
        return Variable(self.table, self.column_name, reduce_function)


class Variable:
    def __init__(self, table, column_name, reduce_function):
        self.table = table
        self.column_name = column_name
        self.reduce_function = reduce_function

    def compile_to_query_language(self):
        """Compile the query language Value"""
        patient = self.reduce_function(self.table)
        column = patient.get(self.column_name)
        return column
