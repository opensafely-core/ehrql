import csv
import importlib.util
import inspect
import shutil
import sys
from contextlib import contextmanager

import structlog

from .backends import BACKENDS
from .definition.base import dataset_registry
from .query_utils import get_column_definitions
from .validate_dummy_data import validate_dummy_data_file, validate_file_types_match

log = structlog.getLogger()


def run_dataset_action(
    dataset_action_function, definition_path, dataset_file, **function_kwargs
):
    log.info(f"Running {dataset_action_function.__name__} for {str(definition_path)}")
    log.debug("args:", **function_kwargs)

    dataset_file.parent.mkdir(parents=True, exist_ok=True)
    module = load_module(definition_path)

    load_dataset_classes(module)
    assert len(dataset_registry.datasets) == 1
    dataset = list(dataset_registry.datasets)[0]
    dataset_action_function(dataset, dataset_file, **function_kwargs)


def generate_dataset(
    dataset,
    dataset_file,
    backend_id,
    db_url,
    dummy_data_file=None,
    temporary_database=None,
):
    if dummy_data_file and not db_url:
        validate_file_types_match(dummy_data_file, dataset_file)
        validate_dummy_data_file(dataset, dummy_data_file)
        shutil.copyfile(dummy_data_file, dataset_file)
    else:
        backend = BACKENDS[backend_id](db_url, temporary_database=temporary_database)
        results = extract(dataset, backend)
        write_dataset(results, dataset_file)


def validate_dataset(
    dataset,
    output_file,
    backend_id,
):  # pragma: no cover (Re-implement when testing with new QL)
    backend = BACKENDS[backend_id](database_url=None)
    results = validate(dataset, backend)
    log.info("Validation succeeded")
    write_validation_output(results, output_file)


def generate_measures(
    definition_path, input_file, dataset_file
):  # pragma: no cover (measures not implemented)
    raise NotImplementedError


def test_connection(backend, url):
    from sqlalchemy import select

    backend = BACKENDS[backend](url, temporary_database=None)
    query_engine = backend.query_engine_class({}, backend)
    with query_engine.engine.connect() as connection:
        connection.execute(select(1))
    print("SUCCESS")


def load_dataset_classes(definition_module):
    return [
        obj
        for name, obj in inspect.getmembers(definition_module)
        if inspect.isclass(obj) and obj.__name__ == "Dataset"
    ]


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
    dataset = get_column_definitions(dataset_definition)
    query_engine = backend.query_engine_class(dataset, backend)
    with query_engine.execute_query() as results:
        for row in results:
            yield dict(row)


def validate(
    dataset_class, backend
):  # pragma: no cover (Re-implement when testing with new QL)
    try:
        dataset = get_column_definitions(dataset_class)
        query_engine = backend.query_engine_class(dataset, backend)
        setup_queries, results_query, cleanup_queries = query_engine.get_queries()
        return setup_queries + [results_query] + cleanup_queries
    except Exception:
        log.error("Validation failed")
        # raise the exception to ensure the job fails and the error and traceback are logged
        raise


def write_dataset(
    results, dataset_file
):  # pragma: no cover (Re-implement when testing with new QL)
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


def write_validation_output(
    results, output_file
):  # pragma: no cover (Re-implement when testing with new QL)
    with output_file.open(mode="w") as f:
        for entry in results:
            f.write(f"{str(entry)}\n")
