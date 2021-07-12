import os
from argparse import ArgumentParser
from pathlib import Path

from .main import main


parser = ArgumentParser(description="Generate cohorts in OpenSAFELY")
parser.add_argument(
    "--cohort-definition",
    help="The path of the file where the cohort is defined",
    type=Path,
)
parser.add_argument(
    "--output",
    help="The path of the file where the output will be written",
    type=Path,
)

options = parser.parse_args()

main(
    definition_path=options.cohort_definition,
    output_file=options.output,
    db_url=os.environ["TPP_DATABASE_URL"],
    backend_id=os.environ["BACKEND"],
)
