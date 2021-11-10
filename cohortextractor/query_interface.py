"""The interface between the DSL and the query language (semantic model)"""
from cohortextractor import query_language


class QueryBuilder:
    def __init__(self, table_name):
        self.table_name = table_name

    def select_column(self, column_name):
        return Column(self.table_name, column_name)


class Column:
    def __init__(self, table_name, column_name):
        self.table_name = table_name
        self.column_name = column_name

    def make_one_row_per_patient(self, reduce_function):
        return Variable(self.table_name, self.column_name, reduce_function)


class Variable:
    def __init__(self, table_name, column_name, reduce_function):
        self.table_name = table_name
        self.column_name = column_name
        self.reduce_function = reduce_function

    def compile_to_query_language(self):
        """Compile the query language Value"""
        table = query_language.table(self.table_name)
        patient = self.reduce_function(table)
        column = patient.get(self.column_name)
        return column
