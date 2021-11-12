"""The interface between the DSL and the query language (semantic model)"""
import copy

from cohortextractor import query_language


class QueryBuilder:
    def __init__(self, table_name):
        self.table_name = table_name
        self.filter_details = []

    def filter(self, *args, **kwargs):  # noqa: A003
        filtered = copy.deepcopy(self)
        filtered.filter_details.append((args, kwargs))
        return filtered

    def select_column(self, column_name):
        return Column(self.table_name, self.filter_details, column_name)


class Column:
    def __init__(self, table_name, filter, column_name):  # noqa: A002
        self.table_name = table_name
        self.filter = filter
        self.column_name = column_name

    def make_one_row_per_patient(self, reduce_function):
        return Variable(self.table_name, self.filter, self.column_name, reduce_function)


class Variable:
    def __init__(self, table_name, filter, column_name, reduce_function):  # noqa: A002
        self.table_name = table_name
        self.filter = filter
        self.column_name = column_name
        self.reduce_function = reduce_function

    def compile_to_query_language(self):
        """Compile the query language Value"""
        table = query_language.table(self.table_name)
        if self.filter:
            for filter_args, filter_kwargs in self.filter:
                table = table.filter(*filter_args, **filter_kwargs)
        patient = self.reduce_function(table)
        column = patient.get(self.column_name)
        return column
