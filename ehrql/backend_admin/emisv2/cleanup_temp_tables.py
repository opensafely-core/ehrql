import datetime
import logging
import re

import sqlalchemy

from ehrql.__main__ import add_dsn_argument


log = logging.getLogger(__name__)


HELP = (
    "Drop ehrQL temporary tables in the EMIS schema that are older than "
    "--max-age-days. These would normally be dropped by the query "
    "engine's own cleanup queries; this task removes any that were left "
    "behind because the query process was interrupted."
)


def add_arguments(parser, environ):
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=14,
        help="Drop tables older than this many days (default: 14).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List tables that would be dropped, but don't actually drop them.",
    )
    add_dsn_argument(parser, environ)


# Matches the table naming convention used by TrinoQueryEngine.create_inline_table
# and reify_query.
# The timestamp and token part come from `global_unique_id` (BaseSQLQueryEngine).
TABLE_PREFIX = "ehrql_"
TABLE_NAME_PATTERN = pattern = re.compile(
    rf"""
    ^{TABLE_PREFIX}
    (?P<timestamp>
        20\d{{2}}                 # Year: 2000-2099
        (?:0[1-9]|1[0-2])         # Month: 01-12
        (?:0[1-9]|[12]\d|3[01])   # Day: 01-31
    _                             # Separator
        (?:[01]\d|2[0-3])         # Hour: 00-23
        (?:[0-5]\d)               # Minute: 00-59
    )
    _                             # Separator
    [0-9a-f]{{12}}                # hex token
    _
    (?:inline_data|tmp)           # table type
    _\d+                          # Counter
    $
""",
    re.X,
)

TIMESTAMP_FORMAT = "%Y%m%d_%H%M"


def run(*, backend_class, dsn, max_age_days, dry_run, environ, user_args):
    backend = backend_class(environ)
    query_engine = backend.get_query_engine(dsn)
    schema = query_engine.temp_table_schema
    cutoff = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=max_age_days)
    dropped = False
    with query_engine.engine.connect() as connection:
        candidates = list_prefixed_tables(connection, schema)
        old_tables = [name for name in candidates if table_is_older_than(name, cutoff)]
        if not old_tables:
            log.info(
                "No ehrQL temporary tables older than %d days in schema '%s'.",
                max_age_days,
                schema,
            )
        for name in old_tables:
            qualified = f'"{schema}"."{name}"'
            if dry_run:
                log.info("Would drop %s", qualified)
            else:
                log.info("Dropping %s", qualified)
                connection.execute(sqlalchemy.text(f"DROP TABLE IF EXISTS {qualified}"))
                dropped = True
    # Print true/false so a wrapping `docker run` (i.e. a RAP agent job) can read whether anything was
    # actually dropped from the container's stdout and report the results to the RAP controller.
    print("true" if dropped else "false")


def list_prefixed_tables(connection, schema):
    result = connection.execute(
        sqlalchemy.text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = :schema AND table_name LIKE :prefix"
        ),
        {"schema": schema, "prefix": f"{TABLE_PREFIX}%"},
    )
    return [row[0] for row in result]


def table_is_older_than(table_name, cutoff):
    match = TABLE_NAME_PATTERN.match(table_name)
    if not match:
        return False
    timestamp = match.group("timestamp")
    ts = datetime.datetime.strptime(timestamp, TIMESTAMP_FORMAT).replace(
        tzinfo=datetime.UTC
    )
    return ts < cutoff
