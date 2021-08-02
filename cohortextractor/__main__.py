import os
from argparse import ArgumentParser
from pathlib import Path

from .main import main


def existing_python_file(value):
    path = Path(value)
    if not path.exists():
        raise ValueError(f"{value} does not exit")
    if not path.suffix == ".py":
        raise ValueError(f"{value} is not a Python file")
    return path


parser = ArgumentParser(description="Generate cohorts in OpenSAFELY")
parser.add_argument(
    "--cohort-definition",
    help="The path of the file where the cohort is defined",
    type=existing_python_file,
)
parser.add_argument(
    "--output",
    help="The path of the file where the output will be written",
    type=Path,
)
parser.add_argument(
    "--dummy-data-file",
    help="Use dummy data from file",
    type=Path,
)

options = parser.parse_args()

main(
    definition_path=options.cohort_definition,
    output_file=options.output,
    db_url=os.environ.get("TPP_DATABASE_URL"),
    backend_id=os.environ.get("BACKEND"),
    dummy_data_file=options.dummy_data_file,
)
