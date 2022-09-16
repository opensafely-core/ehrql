import importlib
import os
import sys
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path

from databuilder.file_formats import FILE_FORMATS, get_file_extension

from . import __version__
from .main import (
    dump_dataset_sql,
    generate_dataset,
    generate_measures,
    pass_dummy_data,
    test_connection,
)

QUERY_ENGINE_ALIASES = {
    "mssql": "databuilder.query_engines.mssql.MSSQLQueryEngine",
    "spark": "databuilder.query_engines.spark.SparkQueryEngine",
    "sqlite": "databuilder.query_engines.sqlite.SQLiteQueryEngine",
    "csv": "databuilder.query_engines.csv.CSVQueryEngine",
}


BACKEND_ALIASES = {
    "databricks": "databuilder.backends.databricks.DatabricksBackend",
    "graphnet": "databuilder.backends.graphnet.GraphnetBackend",
    "tpp": "databuilder.backends.tpp.TPPBackend",
}

EXPECTATIONS_BACKEND_PLACEHOLDER = object()


def entrypoint():
    # This is covered by the Docker tests but they're not recorded for coverage
    return main(sys.argv[1:], environ=os.environ)  # pragma: no cover


def main(args, environ=None):
    environ = environ or {}

    parser = build_parser(environ)
    options = parser.parse_args(args)

    if options.which == "generate-dataset":
        if options.dsn:
            assert options.backend != EXPECTATIONS_BACKEND_PLACEHOLDER
            generate_dataset(
                definition_file=options.dataset_definition,
                dataset_file=options.output,
                dsn=options.dsn,
                backend_class=options.backend,
                query_engine_class=options.query_engine,
                environ=environ,
            )
        elif options.dummy_data_file:
            pass_dummy_data(
                options.dataset_definition, options.output, options.dummy_data_file
            )
        else:
            parser.error(
                "error: one of --dummy-data-file, --dsn or DATABASE_URL environment "
                "variable is required"
            )
    elif options.which == "dump-dataset-sql":
        assert options.backend != EXPECTATIONS_BACKEND_PLACEHOLDER
        dump_dataset_sql(
            options.dataset_definition,
            options.output,
            backend_class=options.backend,
            query_engine_class=options.query_engine,
            environ=environ,
        )
    elif options.which == "generate-measures":
        generate_measures(
            definition_path=options.dataset_definition,
            input_file=options.input,
            dataset_file=options.output,
        )
    elif options.which == "test-connection":
        test_connection(
            backend_class=options.backend,
            url=options.url,
            environ=environ,
        )
    elif options.which == "print-help":
        parser.print_help()
    else:
        assert False, f"Unhandled subcommand: {options.which}"


def build_parser(environ):
    parser = ArgumentParser(
        prog="databuilder", description="Generate datasets in OpenSAFELY"
    )
    parser.set_defaults(which="print-help")

    parser.add_argument(
        "-v", "--version", action="version", version=f"databuilder {__version__}"
    )

    subparsers = parser.add_subparsers(help="sub-command help")
    add_generate_dataset(subparsers, environ)
    add_dump_dataset_sql(subparsers, environ)
    add_generate_measures(subparsers, environ)
    add_test_connection(subparsers, environ)

    return parser


def add_generate_dataset(subparsers, environ):
    parser = subparsers.add_parser("generate-dataset", help="Generate a dataset")
    parser.set_defaults(which="generate-dataset")
    parser.add_argument(
        "--output",
        help=(
            f"Path of the file where the dataset will be written (console by default),"
            f" supported formats: {', '.join(FILE_FORMATS)}"
        ),
        type=valid_output_path,
    )
    parser.add_argument(
        "--dsn",
        help="Data Source Name: URL of remote database, or path to data on disk",
        type=str,
        default=environ.get("DATABASE_URL"),
    )
    parser.add_argument(
        "--dummy-data-file",
        help="Provide dummy data from a file to be validated and used as the dataset",
        type=Path,
    )
    add_common_dataset_arguments(parser, environ)


def add_dump_dataset_sql(subparsers, environ):
    parser = subparsers.add_parser(
        "dump-dataset-sql",
        help=(
            "Output the SQL that would be executed to fetch the results of the "
            "dataset definition"
        ),
    )
    parser.set_defaults(which="dump-dataset-sql")
    parser.add_argument(
        "--output",
        help="SQL output file (outputs to console by default)",
        type=Path,
    )
    add_common_dataset_arguments(parser, environ)


def add_common_dataset_arguments(parser, environ):
    parser.add_argument(
        "dataset_definition",
        help="The path of the file where the dataset is defined",
        type=existing_python_file,
    )
    parser.add_argument(
        "--query-engine",
        type=query_engine_from_id,
        help=f"Dotted import path to class, or one of: {', '.join(QUERY_ENGINE_ALIASES)}",
        default=environ.get("OPENSAFELY_QUERY_ENGINE"),
    )
    parser.add_argument(
        "--backend",
        type=backend_from_id,
        help=f"Dotted import path to class, or one of: {', '.join(BACKEND_ALIASES)}",
        default=environ.get("OPENSAFELY_BACKEND"),
    )


def add_generate_measures(subparsers, environ):
    parser = subparsers.add_parser(
        "generate-measures", help="Generate measures from a dataset"
    )
    parser.set_defaults(which="generate-measures")
    parser.add_argument(
        "--input",
        help="Path and filename (or pattern) of the input file(s)",
        type=Path,
    )
    parser.add_argument(
        "--output",
        help="Path and filename (or pattern) of the file(s) where the dataset will be written",
        type=Path,
    )
    parser.add_argument(
        "dataset_definition",
        help="The path of the file where the dataset is defined",
        type=existing_python_file,
    )


def add_test_connection(subparsers, environ):
    parser = subparsers.add_parser(
        "test-connection", help="test the database connection configuration"
    )
    parser.set_defaults(which="test-connection")
    parser.add_argument(
        "--backend",
        "-b",
        help="backend type to test",
        type=backend_from_id,
        default=environ.get("BACKEND", environ.get("OPENSAFELY_BACKEND")),
    )
    parser.add_argument(
        "--url",
        "-u",
        help="db url",
        default=environ.get("DATABASE_URL"),
    )


def existing_python_file(value):
    path = Path(value)
    if not path.exists():
        raise ArgumentTypeError(f"{value} does not exist")
    if not path.suffix == ".py":
        raise ArgumentTypeError(f"{value} is not a Python file")
    return path


def valid_output_path(value):
    path = Path(value)
    extension = get_file_extension(path)
    if extension not in FILE_FORMATS:
        raise ArgumentTypeError(
            f"'{extension}' is not a supported format, must be one of: "
            f"{', '.join(FILE_FORMATS)}"
        )
    return path


def query_engine_from_id(str_id):
    if "." not in str_id:
        try:
            str_id = QUERY_ENGINE_ALIASES[str_id]
        except KeyError:
            raise ArgumentTypeError(
                f"must be one of: {', '.join(QUERY_ENGINE_ALIASES.keys())} "
                f"(or a full dotted path to a query engine class)"
            )
    query_engine = import_string(str_id)
    assert_duck_type(query_engine, "query engine", "get_results")
    return query_engine


def backend_from_id(str_id):
    if str_id == "expectations":
        return EXPECTATIONS_BACKEND_PLACEHOLDER

    if "." not in str_id:
        try:
            str_id = BACKEND_ALIASES[str_id]
        except KeyError:
            raise ArgumentTypeError(
                f"(or OPENSAFELY_BACKEND) must be one of: {', '.join(BACKEND_ALIASES.keys())} "
                f"(or a full dotted path to a backend class) but got '{str_id}'"
            )
    backend = import_string(str_id)
    assert_duck_type(backend, "backend", "get_table_expression")
    return backend


def import_string(dotted_path):
    if "." not in dotted_path:
        raise ArgumentTypeError("must be a full dotted path to a Python class")
    module_name, _, attribute_name = dotted_path.rpartition(".")
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        raise ArgumentTypeError(f"could not import module '{module_name}'")
    try:
        return getattr(module, attribute_name)
    except AttributeError:
        raise ArgumentTypeError(
            f"module '{module_name}' has no attribute '{attribute_name}'"
        )


def assert_duck_type(obj, type_name, required_method):
    if not hasattr(obj, required_method):
        raise ArgumentTypeError(
            f"{obj} is not a valid {type_name}: no '{required_method}' method"
        )


if __name__ == "__main__":
    entrypoint()
