import importlib.util
import shutil
import sys
from contextlib import contextmanager, nullcontext

import structlog

from databuilder.column_specs import get_column_specs
from databuilder.file_formats import (
    validate_dataset,
    validate_file_types_match,
    write_dataset,
)
from databuilder.itertools_utils import eager_iterator
from databuilder.query_language import Dataset, compile
from databuilder.sqlalchemy_utils import clause_as_str, get_setup_and_cleanup_queries
from databuilder.traceback_utils import trim_and_print_exception

log = structlog.getLogger()


def generate_dataset(
    definition_file,
    dataset_file,
    dsn,
    backend_class,
    query_engine_class,
    environ,
):
    log.info(f"Generating dataset for {str(definition_file)}")
    dataset_definition = load_definition(definition_file)
    variable_definitions = compile(dataset_definition)
    column_specs = get_column_specs(variable_definitions)

    query_engine = get_query_engine(dsn, backend_class, query_engine_class, environ)
    results = query_engine.get_results(variable_definitions)
    # Because `results` is a generator we won't actually execute any queries until we
    # start consuming it. But we want to make sure we trigger any errors (or relevant
    # log output) before we create the output file. Wrapping the generator in
    # `eager_iterator` ensures this happens by consuming the first item upfront.
    results = eager_iterator(results)
    write_dataset(dataset_file, results, column_specs)


def pass_dummy_data(definition_file, dataset_file, dummy_data_file):
    log.info(f"Generating dataset for {str(definition_file)}")

    dataset_definition = load_definition(definition_file)
    variable_definitions = compile(dataset_definition)
    column_specs = get_column_specs(variable_definitions)

    validate_file_types_match(dummy_data_file, dataset_file)
    validate_dataset(dummy_data_file, column_specs)

    dataset_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(dummy_data_file, dataset_file)


def dump_dataset_sql(
    definition_file, output_file, backend_class, query_engine_class, environ
):
    log.info(f"Generating SQL for {str(definition_file)}")

    dataset_definition = load_definition(definition_file)
    query_engine = get_query_engine(None, backend_class, query_engine_class, environ)

    variable_definitions = compile(dataset_definition)
    all_query_strings = get_sql_strings(query_engine, variable_definitions)
    log.info("SQL generation succeeded")

    with open_output_file(output_file) as f:
        for query_str in all_query_strings:
            f.write(f"{query_str};\n\n")


def get_sql_strings(query_engine, variable_definitions):
    results_query = query_engine.get_query(variable_definitions)
    setup_queries, cleanup_queries = get_setup_and_cleanup_queries(results_query)
    dialect = query_engine.sqlalchemy_dialect()
    sql_strings = []

    for n, query in enumerate(setup_queries, start=1):
        sql = clause_as_str(query, dialect)
        sql_strings.append(f"-- Setup query {n:03} / {len(setup_queries):03}\n{sql}")

    sql = clause_as_str(results_query, dialect)
    sql_strings.append(f"-- Results query\n{sql}")

    assert not cleanup_queries, "Support these once tests exercise them"

    return sql_strings


def open_output_file(output_file):
    # If a file path is supplied, create it and open for writing
    if output_file is not None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        return output_file.open("w")
    # Otherwise return `stdout` wrapped in a no-op context manager
    else:
        return nullcontext(sys.stdout)


def get_query_engine(dsn, backend_class, query_engine_class, environ):
    # Construct backend if supplied
    if backend_class:
        backend = backend_class()
    else:
        backend = None

    if not query_engine_class:
        # Use the query engine class specified by the backend, if we have one
        if backend:
            query_engine_class = backend.query_engine_class
        # Otherwise default to using SQLite
        else:
            from databuilder.query_engines.csv import (
                CSVQueryEngine as query_engine_class,
            )

    return query_engine_class(dsn=dsn, backend=backend, config=environ)


def generate_measures(
    definition_path, input_file, dataset_file
):  # pragma: no cover (measures not implemented)
    raise NotImplementedError


def test_connection(backend_class, url, environ):
    from sqlalchemy import select

    backend = backend_class()
    query_engine = backend.query_engine_class(url, backend, config=environ)
    with query_engine.engine.connect() as connection:
        connection.execute(select(1))
    print("SUCCESS")


def load_definition(definition_file):
    try:
        module = load_module(definition_file)
    except Exception:
        trim_and_print_exception()
        sys.exit(1)
    try:
        dataset = module.dataset
    except AttributeError:
        raise AttributeError("A dataset definition must define one 'dataset'")
    assert isinstance(
        dataset, Dataset
    ), "'dataset' must be an instance of databuilder.ehrql.Dataset()"
    return dataset


def load_module(definition_path):
    # Taken from the official recipe for importing a module from a file path:
    # https://docs.python.org/3.9/library/importlib.html#importing-a-source-file-directly

    # The name we give the module is arbitrary
    spec = importlib.util.spec_from_file_location("dataset", definition_path)
    module = importlib.util.module_from_spec(spec)
    # Temporarily add the directory containing the definition to the path so that the
    # definition can import library modules from that directory
    with add_to_sys_path(str(definition_path.parent)):
        spec.loader.exec_module(module)
    return module


@contextmanager
def add_to_sys_path(directory):
    original = sys.path.copy()
    sys.path.append(directory)
    try:
        yield
    finally:
        sys.path = original
