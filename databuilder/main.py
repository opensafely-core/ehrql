import csv
import importlib.util
import shutil
import sys
from contextlib import contextmanager

import structlog

from . import query_language as ql
from .backends import BACKENDS
from .definition.base import dataset_registry
from .validate_dummy_data import validate_dummy_data_file, validate_file_types_match

log = structlog.getLogger()


def generate_dataset(
    definition_file,
    dataset_file,
    backend_id,
    db_url,
    temporary_database,
):
    log.info(f"Generating dataset for {str(definition_file)}")

    dataset = load_definition(definition_file)
    backend = BACKENDS[backend_id](db_url, temporary_database=temporary_database)
    results = extract(dataset, backend)

    dataset_file.parent.mkdir(parents=True, exist_ok=True)
    write_dataset(results, dataset_file)


def pass_dummy_data(definition_file, dataset_file, dummy_data_file):
    log.info(f"Generating dataset for {str(definition_file)}")

    dataset = load_definition(definition_file)
    validate_dummy_data_file(dataset, dummy_data_file)
    validate_file_types_match(dummy_data_file, dataset_file)

    dataset_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(dummy_data_file, dataset_file)


def validate_dataset(definition_file, output_file, backend_id):
    log.info(f"Validating dataset for {str(definition_file)}")

    dataset = load_definition(definition_file)
    backend = BACKENDS[backend_id](database_url=None)
    results = validate(dataset, backend)
    log.info("Validation succeeded")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open(mode="w") as f:
        for entry in results:
            f.write(f"{str(entry)}\n")


def generate_measures(
    definition_path, input_file, dataset_file
):  # pragma: no cover (measures not implemented)
    raise NotImplementedError


def test_connection(backend, url):
    from sqlalchemy import select

    backend = BACKENDS[backend](url, temporary_database=None)
    query_engine = backend.query_engine_class(backend)
    with query_engine.engine.connect() as connection:
        connection.execute(select(1))
    print("SUCCESS")


def load_definition(definition_file):
    load_module(definition_file)
    assert len(dataset_registry.datasets) == 1
    return dataset_registry.datasets.copy().pop()


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


@contextmanager
def add_to_sys_path(directory):
    original = sys.path.copy()
    sys.path.append(directory)
    try:
        yield
    finally:
        sys.path = original


def extract(dataset_definition, backend):
    """
    Extracts the dataset from the backend specified
    Args:
        dataset_definition: The definition of the Dataset
        backend: The Backend that the Dataset is being extracted from
    Returns:
        Yields the dataset as rows
    """
    backend.validate_contracts()
    dataset = ql.compile(dataset_definition)
    query_engine = backend.query_engine_class(backend)
    with query_engine.execute_query(dataset) as results:
        for row in results:
            yield dict(row)


def validate(dataset_class, backend):
    try:
        dataset = ql.compile(dataset_class)
        query_engine = backend.query_engine_class(backend)
        setup_queries, results_query, cleanup_queries = query_engine.get_queries(
            dataset
        )
        return setup_queries + [results_query] + cleanup_queries
    except Exception:  # pragma: no cover (puzzle: dataset definition that compiles to QM but not SQL)
        log.error("Validation failed")
        # raise the exception to ensure the job fails and the error and traceback are logged
        raise


def write_dataset(results, dataset_file):
    with dataset_file.open(mode="w") as f:
        writer = csv.writer(f)
        headers = None
        for entry in results:
            fields = entry.keys()
            if not headers:
                headers = fields
                writer.writerow(headers)
            else:
                assert fields == headers, f"Expected fields {headers}, but got {fields}"
            writer.writerow(entry.values())
