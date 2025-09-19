from pathlib import Path

from ehrql.codes import codelist_from_csv
from ehrql.debugger import show
from ehrql.measures import INTERVAL, Measures, create_measures
from ehrql.permissions import claim_permissions
from ehrql.query_language import (
    Dataset,
    Error,
    case,
    create_dataset,
    days,
    maximum_of,
    minimum_of,
    months,
    weeks,
    when,
    years,
)
from ehrql.user_parameters import get_parameter
from ehrql.utils.log_utils import init_logging


__version__ = Path(__file__).parent.joinpath("VERSION").read_text().strip()


__all__ = [
    "claim_permissions",
    "codelist_from_csv",
    "INTERVAL",
    "Measures",
    "Dataset",
    "Error",
    "case",
    "create_dataset",
    "create_measures",
    "days",
    "get_parameter",
    "show",
    "maximum_of",
    "minimum_of",
    "months",
    "weeks",
    "when",
    "years",
]

init_logging()
