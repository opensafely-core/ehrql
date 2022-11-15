from pathlib import Path

from .log_utils import init_logging

init_logging()

__version__ = Path(__file__).parent.joinpath("VERSION").read_text().strip()
