"""
You can run this file as follows:

    DB_NAME=mssql SCHEMA_FILE=ehrql/tables/core.py \
      pytest -o python_functions=create tests/lib/create_tables.py

Or use:

    just create-tables mssql ehrql/tables/core.py

"""

# pragma: no cover file
import importlib
import os

from ehrql.query_language import get_tables_from_namespace
from tests.lib.orm_utils import orm_classes_from_tables


# This is not a test, but we can get pytest to run it as a test so we can re-use all the
# fixture machinery. Because neither this file not this function are named appropriately
# they avoid being discovered and executed during the normal test run. But we can run it
# by passing the path and function name directly to pytest
def create(request):
    ALLOWED_DB_NAMES = ["mssql", "trino"]
    db_name = os.environ.get("DB_NAME")
    schema_file = os.environ.get("SCHEMA_FILE")
    errors = []

    if db_name not in ALLOWED_DB_NAMES:
        errors.append(f"DB_NAME env var must be one of: {', '.join(ALLOWED_DB_NAMES)}")

    if not schema_file or not os.path.exists(schema_file):
        errors.append(
            "SCHEMA_FILE env var must point to a Python file which defines either:\n"
            "\n"
            " * an ehrQL schema e.g. one of the files from `ehrql/tables/`; or\n"
            " * a collection of SQLAlchemy ORM modules e.g. one of the \n"
            "   `schema.py` files from `tests/backend_schemas/`.\n"
        )

    if errors:
        raise RuntimeError("\n" + "\n\n".join(errors))

    # Load the supplied schema file
    spec = importlib.util.spec_from_file_location("schema", schema_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Extract the interesting stuff from it
    ehrql_tables = [t for _, t in get_tables_from_namespace(module)]
    Base = getattr(module, "Base", None)

    # Get a reference to the SQLAlchemy MetaData object
    if ehrql_tables:
        orm_classes = list(orm_classes_from_tables(ehrql_tables).values())
        metadata = orm_classes[0].metadata
    elif Base is not None:
        metadata = Base.metadata
    else:
        raise RuntimeError(
            f"Could not find any ehrQL tables or a SQLAlchemy ORM `Base` class in: {schema_file}"
        )

    # Create the database and create the specified tables in it
    db_fixture = f"{db_name}_database_with_session_scope"
    db = request.getfixturevalue(db_fixture)
    db.setup(metadata=metadata)

    # Report on what we've just done
    capturemanager = request.config.pluginmanager.getplugin("capturemanager")
    with capturemanager.global_and_fixture_disabled():
        print(f"\n\n=> Created tables in `{db_name}` test database from: {schema_file}")
        print()
        print("DSN for ehrQL:")
        print(f"  DATABASE_URL='{db.host_url()}'")
        print()
        print("Connection string for VSCode MSSQL Extension:")
        # Note to security scanners: these are local test credentials which are being
        # supplied to the user. Logging these does not represent a security issue.
        print(
            f"  Server={db.host_from_host},{db.port_from_host};Database={db.db_name};"
            f"User Id={db.username};Password={db.password};"
        )
        print()
