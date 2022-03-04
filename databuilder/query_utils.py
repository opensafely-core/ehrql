from . import query_language as ql


def get_column_definitions(dataset):
    return ql.compile(dataset)
