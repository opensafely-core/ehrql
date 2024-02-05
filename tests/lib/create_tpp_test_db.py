"""
Run this using:

    pytest -o python_functions=create tests/lib/create_tpp_test_db.py

It will start an MSSQL Docker container, create all the tables in the TPP schema, and
output the connection string needed to talk to this database.
"""

from .tpp_schema import Base  # pragma: no cover


# This is not a test, but we can get pytest to run it as a test so we can re-use all the
# fixture machinery. Because neither this file not this function are named appropriately
# they avoid being discovered and executed during the normal test run. But we can run it
# by passing the path and function name directly to pytest
def create(request, mssql_database_with_session_scope):  # pragma: no cover
    db = mssql_database_with_session_scope
    db.setup(metadata=Base.metadata)
    capturemanager = request.config.pluginmanager.getplugin("capturemanager")
    with capturemanager.global_and_fixture_disabled():
        print("\n\n=> Created TPP tables in test database")
        print()
        print("DSN for ehrQL:")
        print(f"  DATABASE_URL='{db.host_url()}'")
        print()
        print("Connection string for VSCode MSSQL Extension:")
        print(
            f"  Server={db.host_from_host},{db.port_from_host};Database={db.db_name};"
            f"User Id={db.username};Password={db.password};"
        )
        print()
