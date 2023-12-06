import sqlalchemy

from ehrql.query_language import get_tables_from_namespace
from ehrql.tables import emis, tpp
from ehrql.tables.raw import emis as emis_raw
from ehrql.tables.raw import tpp as tpp_raw


REGISTERED_TABLES = set()


# This slightly odd way of supplying the table object to the test function makes the
# tests introspectable in such a way that we can confirm that every table in the module
# is covered by a test
def register_test_for(table):
    def annotate_test_function(fn):
        REGISTERED_TABLES.add(table)
        fn._table = table
        return fn

    return annotate_test_function


def assert_types_correct(columns_with_types, database):
    mismatched = [
        f"{table}.{column} expects {column_type!r} but got {column_args!r}"
        for table, column, column_type, column_args in columns_with_types
        if not types_compatible(database, column_type, column_args)
    ]
    nl = "\n"
    assert not mismatched, (
        f"Mismatch between columns returned by backend queries"
        f" queries and those expected:\n{nl.join(mismatched)}\n\n"
    )


def types_compatible(database, column_type, column_args):
    """
    Is this given SQLAlchemy type instance compatible with the supplied dictionary of
    column arguments?
    """
    # It seems we use this sometimes for the patient ID column where we don't care what
    # type it is
    if isinstance(column_type, sqlalchemy.sql.sqltypes.NullType):
        return True
    elif isinstance(column_type, sqlalchemy.Boolean):
        # MSSQL doesn't have a boolean type so we expect an int here
        if database.protocol == "mssql":
            return column_args["type"] == "int"
        # Current no non-mssql backends (i.e. emis) have boolean column types
        return column_args["type"] == "boolean"  # pragma: no cover
    elif isinstance(column_type, sqlalchemy.Integer):
        return column_args["type"] in ("int", "integer", "bigint")
    elif isinstance(column_type, sqlalchemy.Float):
        return column_args["type"] == "real"
    elif isinstance(column_type, sqlalchemy.Date):
        return column_args["type"] == "date"
    elif isinstance(column_type, sqlalchemy.String):
        return (
            column_args["type"].startswith("varchar")
            and column_args.get("collation") == column_type.collation
        )
    else:
        assert False, f"Unhandled type: {column_type}"


def get_all_backend_columns(backend):
    for _, table in get_all_tables(backend):
        qm_table = table._qm_node
        table_expr = backend.get_table_expression(qm_table.name, qm_table.schema)
        yield qm_table.name, table_expr.columns


def get_all_tables(backend):
    table_modules_by_backend = {"emis": [emis, emis_raw], "tpp": [tpp, tpp_raw]}
    modules = table_modules_by_backend[backend.display_name.lower()]
    for module in modules:
        for name, table in get_tables_from_namespace(module):
            yield f"{module.__name__}.{name}", table


def assert_tests_exhaustive(backend):
    missing = [
        name
        for name, table in get_all_tables(backend)
        if table not in REGISTERED_TABLES
    ]
    assert not missing, f"No tests for tables: {', '.join(missing)}"
