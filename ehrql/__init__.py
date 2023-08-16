from pathlib import Path

from ehrql.codes import codelist_from_csv
from ehrql.measures import INTERVAL, Measures
from ehrql.query_language import (
    Dataset,
    case,
    days,
    maximum_of,
    minimum_of,
    months,
    weeks,
    when,
    years,
)
from ehrql.utils.log_utils import init_logging


__version__ = Path(__file__).parent.joinpath("VERSION").read_text().strip()


__all__ = [
    "codelist_from_csv",
    "INTERVAL",
    "Measures",
    "Dataset",
    "case",
    "days",
    "maximum_of",
    "minimum_of",
    "months",
    "weeks",
    "when",
    "years",
]

init_logging()
