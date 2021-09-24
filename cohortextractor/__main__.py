import os
from argparse import ArgumentParser
from pathlib import Path

from .main import generate_cohort, generate_measures


def existing_python_file(value):
    path = Path(value)
    if not path.exists():
        raise ValueError(f"{value} does not exist")
    if not path.suffix == ".py":
        raise ValueError(f"{value} is not a Python file")
    return path


parser = ArgumentParser(description="Generate cohorts in OpenSAFELY")
subparsers = parser.add_subparsers(help="sub-command help")

generate_cohort_parser = subparsers.add_parser(
    "generate_cohort", help="Generate cohort"
)
generate_cohort_parser.set_defaults(which="generate_cohort")
generate_cohort_parser.add_argument(
    "--cohort-definition",
    help="The path of the file where the cohort is defined",
    type=existing_python_file,
)
generate_cohort_parser.add_argument(
    "--output",
    help="Path and filename (or pattern) of the file(s) where the output will be written",
    type=Path,
)
generate_cohort_parser.add_argument(
    "--dummy-data-file",
    help="Provide dummy data from a file to be validated and used as output",
    type=Path,
)

generate_measures_parser = subparsers.add_parser(
    "generate_measures", help="Generate measures from cohort data"
)
generate_measures_parser.set_defaults(which="generate_measures")

# Measure generator parser options
generate_measures_parser.add_argument(
    "--input",
    help="Path and filename (or pattern) of the input file(s)",
    type=Path,
)
generate_measures_parser.add_argument(
    "--output",
    help="Path and filename (or pattern) of the file(s) where the output will be written",
    type=Path,
)
generate_measures_parser.add_argument(
    "--cohort-definition",
    help="The path of the file where the cohort is defined",
    type=existing_python_file,
)

options = parser.parse_args()


if options.which == "generate_cohort":

    if not (options.dummy_data_file or os.environ.get("DATABASE_URL")):
        parser.error(
            "error: either --dummy-data-file or DATABASE_URL environment variable is required"
        )

    generate_cohort(
        definition_path=options.cohort_definition,
        output_file=options.output,
        db_url=os.environ.get("DATABASE_URL"),
        backend_id=os.environ.get("OPENSAFELY_BACKEND"),
        dummy_data_file=options.dummy_data_file,
        temporary_database=os.environ.get("TEMP_DATABASE_NAME"),
    )
elif options.which == "generate_measures":
    generate_measures(
        definition_path=options.cohort_definition,
        input_file=options.input,
        output_file=options.output,
    )
