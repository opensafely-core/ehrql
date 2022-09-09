from importlib.metadata import PackageNotFoundError, version

from .date_utils import dataset_date_range
from .log_utils import init_logging
from .measure import Measure

init_logging()

try:
    __version__ = version("opensafely-databuilder")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "dev"

__all__ = [
    "dataset_date_range",
    "Measure",
]
