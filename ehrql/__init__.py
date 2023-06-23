import os
from pathlib import Path

from ehrql.codes import codelist_from_csv
from ehrql.measures import INTERVAL, Measures
from ehrql.query_language import Dataset, case, days, months, weeks, when, years
from ehrql.utils.log_utils import init_logging


if os.getenv("LOG_SQL"):  # pragma: no cover
    # Logging is very verbose in tests, so we disable it  unless specifically requested
    # with the use of the `LOG_SQL` environment variable.
    # By defalt, logging is initiated in __main__.py, so it's only enabled when running
    # ehrql from the command line.
    init_logging()

__version__ = Path(__file__).parent.joinpath("VERSION").read_text().strip()


__all__ = [
    "codelist_from_csv",
    "INTERVAL",
    "Measures",
    "Dataset",
    "case",
    "days",
    "months",
    "weeks",
    "when",
    "years",
]
