import os
import sys
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path

from .backends import BACKENDS
from .docs import generate_docs
from .main import (
    generate_dataset,
    generate_measures,
    pass_dummy_data,
    test_connection,
    validate_dataset,
)


def main(args=None):
    parser = build_parser()

    if args is None:
        # allow the passing in of args, for testing, but otherwise look them
        # up.  This saves a lot of laborious mocking in tests.
        args = sys.argv[1:]  # pragma: no cover

    options = parser.parse_args(args)

    if options.which == "generate_dataset":
        database_url = os.environ.get("DATABASE_URL")
        dummy_data_file = options.dummy_data_file

        if database_url:
            generate_dataset(
                definition_file=options.dataset_definition,
                dataset_file=options.dataset,
                db_url=database_url,
                backend_id=os.environ.get("OPENSAFELY_BACKEND"),
                temporary_database=os.environ.get("TEMP_DATABASE_NAME"),
            )
        elif dummy_data_file:
            pass_dummy_data(
                options.dataset_definition, options.dataset, dummy_data_file
            )
        else:
            parser.error(
                "error: either --dummy-data-file or DATABASE_URL environment variable is required"
            )
    elif options.which == "validate_dataset_definition":
        validate_dataset(
            options.dataset_definition,
            options.output,
            backend_id=options.backend,
        )
    elif options.which == "generate_measures":
        generate_measures(
            definition_path=options.dataset_definition,
            input_file=options.input,
            dataset_file=options.dataset,
        )
    elif options.which == "test_connection":
        test_connection(
            backend=options.backend,
            url=options.url,
        )
    elif options.which == "generate_docs":
        generate_docs(location=options.location)
    elif options.which == "print_help":
        parser.print_help()
    else:
        assert False, f"Unhandler subcommand: {options.which}"


def build_parser():
    parser = ArgumentParser(
        prog="databuilder", description="Generate datasets in OpenSAFELY"
    )
    parser.set_defaults(which="print_help")
    subparsers = parser.add_subparsers(help="sub-command help")

    generate_dataset_parser = subparsers.add_parser(
        "generate_dataset", help="Generate a dataset"
    )
    generate_dataset_parser.set_defaults(which="generate_dataset")
    generate_dataset_parser.add_argument(
        "--dataset-definition",
        help="The path of the file where the dataset is defined",
        type=existing_python_file,
    )
    generate_dataset_parser.add_argument(
        "--dataset",
        help="Path and filename (or pattern) of the file(s) where the dataset will be written",
        type=Path,
    )
    generate_dataset_parser.add_argument(
        "--dummy-data-file",
        help="Provide dummy data from a file to be validated and used as the dataset",
        type=Path,
    )

    validate_dataset_definition_parser = subparsers.add_parser(
        "validate_dataset_definition",
        help="Validate the dataset definition against the specified backend",
    )
    validate_dataset_definition_parser.set_defaults(which="validate_dataset_definition")

    validate_dataset_definition_parser.add_argument(
        "backend",
        type=str,
        choices=BACKENDS,  # allow all registered backend subclasses
    )
    validate_dataset_definition_parser.add_argument(
        "--dataset-definition",
        help="The path of the file where the dataset is defined",
        type=existing_python_file,
        required=True,
    )
    validate_dataset_definition_parser.add_argument(
        "--output",
        help="Path and filename (or pattern) of the file(s) where the output will be written",
        type=Path,
    )

    generate_measures_parser = subparsers.add_parser(
        "generate_measures", help="Generate measures from a dataset"
    )
    generate_measures_parser.set_defaults(which="generate_measures")

    # Measure generator parser options
    generate_measures_parser.add_argument(
        "--input",
        help="Path and filename (or pattern) of the input file(s)",
        type=Path,
    )
    generate_measures_parser.add_argument(
        "--dataset",
        help="Path and filename (or pattern) of the file(s) where the dataset will be written",
        type=Path,
    )
    generate_measures_parser.add_argument(
        "--dataset-definition",
        help="The path of the file where the dataset is defined",
        type=existing_python_file,
    )

    test_connection_parser = subparsers.add_parser(
        "test_connection", help="test the database connection configuration"
    )
    test_connection_parser.set_defaults(which="test_connection")

    test_connection_parser.add_argument(
        "--backend",
        "-b",
        help="backend type to test",
        default=os.environ.get("BACKEND", os.environ.get("OPENSAFELY_BACKEND")),
    )

    test_connection_parser.add_argument(
        "--url",
        "-u",
        help="db url",
        default=os.environ.get("DATABASE_URL"),
    )

    generate_docs = subparsers.add_parser(
        "generate_docs",
        help="Generate a JSON representation of the data needed for the public documentation of Backends and Contracts",
    )
    generate_docs.set_defaults(which="generate_docs")
    generate_docs.add_argument(
        "--location",
        type=Path,
        help="Optional location to write documentation data to.  Uses current working directory otherwise.",
    )

    return parser


def existing_python_file(value):
    path = Path(value)
    if not path.exists():
        raise ArgumentTypeError(f"{value} does not exist")
    if not path.suffix == ".py":
        raise ArgumentTypeError(f"{value} is not a Python file")
    return path


if __name__ == "__main__":
    main()
