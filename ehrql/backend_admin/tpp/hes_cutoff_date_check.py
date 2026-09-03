import logging
import re
from argparse import ArgumentTypeError

import sqlalchemy

from ehrql.__main__ import add_dsn_argument


log = logging.getLogger(__name__)


HELP = """
    Check that all of the HES tables contain at least one row of data from the expected
    "activity month" (which is a string in YYYYMM format). The HES tables are split into
    live and archived tables, using this column to partition on. If the live/archive
    cutoff date changes such that the live table no longer contains data from the
    expected month we want to know about it.

    To minimise any possibility of data leakage via this method we expose only a single
    boolean result.
    """

MONTH_PATTERN = re.compile(r"^\d{4}(0[1-9]|1[0-2])$")


def valid_month(yearmonth_str):
    if MONTH_PATTERN.match(yearmonth_str):
        return yearmonth_str
    msg = f"Month ({yearmonth_str}) not valid! Expected format, 'YYYYMM"
    raise ArgumentTypeError(msg)


def add_arguments(parser, environ):
    parser.add_argument(
        "--expected-activity-month",
        type=valid_month,
        default=None,
        required=True,
        help="Expected activity month in YYYYMM format.",
    )
    add_dsn_argument(parser, environ)


def run(*, backend_class, dsn, expected_activity_month, environ, user_args):
    backend = backend_class(environ)
    query_engine = backend.get_query_engine(dsn)
    check_ok = True

    with query_engine.engine.connect() as connection:
        for table in ["APCS", "EC", "OPA"]:
            result = connection.execute(
                sqlalchemy.text(
                    f"""
                    SELECT
                    CASE
                        WHEN EXISTS (SELECT 1 FROM {table} WHERE Der_Activity_Month = :activity_month)
                        THEN 1
                        ELSE 0
                    END AS result
                    """
                ),
                {"activity_month": expected_activity_month},
            )
            if next(result)[0] == 0:
                check_ok = False
                break
    # Print true/false so a wrapping `docker run` (i.e. a RAP agent job) can read whether the
    # check succeeded or not from the container's stdout and report the results to the RAP controller.
    print("true" if check_ok else "false")
