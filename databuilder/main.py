import csv
import importlib.util
import inspect
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path

import structlog

from .backends import BACKENDS
from .definition.base import dataset_registry
from .measure import MeasuresManager, combine_csv_files_with_dates
from .query_utils import get_column_definitions, get_measures
from .validate_dummy_data import validate_dummy_data

log = structlog.getLogger()


def run_dataset_action(
    dataset_action_function, definition_path, dataset_file, **function_kwargs
):
    log.info(f"Running {dataset_action_function.__name__} for {str(definition_path)}")
    log.debug("args:", **function_kwargs)

    dataset_file.parent.mkdir(parents=True, exist_ok=True)
    module = load_module(definition_path)

    load_dataset_generator(module)
    assert len(dataset_registry.datasets) == 1
    dataset = list(dataset_registry.datasets)[0]
    dataset_action_function(dataset, None, dataset_file, "", **function_kwargs)


def generate_dataset(
    dataset,
    index_date,
    dataset_file,
    date_suffix,
    backend_id,
    db_url,
    dummy_data_file=None,
    temporary_database=None,
):
    dataset_file_with_date = _replace_filepath_pattern(dataset_file, date_suffix)

    if (
        dummy_data_file and not db_url
    ):  # pragma: no cover (dummy data not currently tested)
        dummy_data_file_with_date = Path(str(dummy_data_file).replace("*", date_suffix))
        validate_dummy_data(dataset, dummy_data_file_with_date, dataset_file_with_date)
        shutil.copyfile(dummy_data_file_with_date, dataset_file_with_date)
    else:  # pragma: no cover (Re-implement when testing with new QL)
        backend = BACKENDS[backend_id](db_url, temporary_database=temporary_database)
        results = extract(dataset, backend)
        write_dataset(results, dataset_file_with_date)


def validate_dataset(
    dataset,
    index_date,
    dataset_file,
    date_suffix,
    backend_id,
):  # pragma: no cover (Re-implement when testing with new QL)
    dataset_file_with_date = _replace_filepath_pattern(dataset_file, date_suffix)
    if index_date:
        log.info("Validating for index date", index_date=index_date)
    backend = BACKENDS[backend_id](database_url=None)
    results = validate(dataset, backend)
    log.info("Validation succeeded")
    write_validation_output(results, dataset_file_with_date)


def generate_measures(
    definition_path, input_file, dataset_file
):  # pragma: no cover (measure not currently working)
    definition_module = load_module(definition_path)
    dataset_generator, index_date_range = load_dataset_generator(definition_module)
    dataset_file.parent.mkdir(parents=True, exist_ok=True)

    measures = []
    for index_date in index_date_range:
        dataset = (
            dataset_generator() if index_date is None else dataset_generator(index_date)
        )
        input_file_with_date = _replace_filepath_pattern(input_file, index_date or "")
        measures = get_measures(dataset)
        if not measures:
            log.warning(
                "No measures variable found", definition_file=definition_path.name
            )
        for measure_id, results in calculate_measures_results(
            measures, input_file_with_date
        ):
            filename_part = (
                measure_id if index_date is None else f"{measure_id}_{index_date}"
            )
            measure_dataset_file = _replace_filepath_pattern(
                dataset_file, filename_part
            )
            results.to_csv(measure_dataset_file, index=False)
            log.info("Created measure dataset", dataset=dataset_file)

    # Combine any date-stamped files into one additional single file per
    # measure Use the measures from the latest dataset, since we only care
    # about their ids here
    for measure in measures:
        combine_csv_files_with_dates(dataset_file, measure.id)
        log.info(f"Combined measure dataset for all dates in {dataset_file}")


def test_connection(backend, url):
    from sqlalchemy import select

    backend = BACKENDS[backend](url, temporary_database=None)
    query_engine = backend.query_engine_class({}, backend)
    with query_engine.engine.connect() as connection:
        connection.execute(select(1))
    print("SUCCESS")


def _replace_filepath_pattern(filepath, filename_part):
    """
    Take a filepath and replace a '*' with the specified filename part
    Returns a new Path
    """
    return Path(str(filepath).replace("*", filename_part))


def calculate_measures_results(
    measures, input_file
):  # pragma: no cover (measure not currently working)
    measures_manager = MeasuresManager(measures, input_file)
    yield from measures_manager.calculate_measures()


def load_dataset_classes(definition_module):
    return [
        obj
        for name, obj in inspect.getmembers(definition_module)
        if inspect.isclass(obj) and obj.__name__ == "Dataset"
    ]


def load_dataset_generator(definition_module):
    """
    Load the dataset definition module and identify the Dataset class or dataset generator
    function.
    Return a function that returns a Dataset class, and the index date range, if applicable.
    """
    load_dataset_classes(definition_module)


def load_module(definition_path):
    # Add the directory containing the definition to the path so that the definition can import library modules from
    # that directory
    definition_dir = definition_path.parent
    module_name = definition_path.stem
    with added_to_path(str(definition_dir)):
        module = importlib.import_module(module_name)
        return module


@contextmanager
def added_to_path(directory):
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
