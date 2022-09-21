from pathlib import Path

from .date_utils import dataset_date_range
from .log_utils import init_logging
from .measure import Measure

init_logging()

__version__ = Path(__file__).parent.joinpath("VERSION").read_text().strip()

__all__ = [
    "dataset_date_range",
    "Measure",
]
