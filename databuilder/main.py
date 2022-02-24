from __future__ import annotations

import csv
import importlib.util
import inspect
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import structlog

from .backends import BACKENDS
from .backends.base import BaseBackend
from .dsl import Cohort
from .measure import MeasuresManager, combine_csv_files_with_dates
from .query_language import Dataset
from .query_utils import get_column_definitions, get_measures
from .validate_dummy_data import validate_dummy_data

log = structlog.getLogger()


def run_cohort_action(
    cohort_action_function, definition_path, output_file, **function_kwargs
):
    log.info(f"Running {cohort_action_function.__name__} for {str(definition_path)}")
    log.debug("args:", **function_kwargs)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    module = load_module(definition_path)
    dataset = load_dataset(module)
    cohort_action_function(dataset, "", output_file, "", **function_kwargs)


def generate_cohort(
    cohort,
    index_date,
    output_file,
    date_suffix,
    backend_id,
    db_url,
    dummy_data_file=None,
    temporary_database=None,
):
    output_file_with_date = _replace_filepath_pattern(output_file, date_suffix)
    if index_date:
        log.info("Generating cohort for index date", index_date=index_date)

    if dummy_data_file and not db_url:
        dummy_data_file_with_date = Path(str(dummy_data_file).replace("*", date_suffix))
        validate_dummy_data(cohort, dummy_data_file_with_date, output_file_with_date)
        shutil.copyfile(dummy_data_file_with_date, output_file_with_date)
    else:  # pragma: no cover (Re-implement when testing with new QL)
        backend = BACKENDS[backend_id](db_url, temporary_database=temporary_database)
        results = extract(cohort, backend)
        write_output(results, output_file_with_date)


def validate_cohort(
    cohort,
    index_date,
    output_file,
    date_suffix,
    backend_id,
):  # pragma: no cover (Re-implement when testing with new QL)
    output_file_with_date = _replace_filepath_pattern(output_file, date_suffix)
    if index_date:
        log.info("Validating for index date", index_date=index_date)
    backend = BACKENDS[backend_id](database_url=None)
    results = validate(cohort, backend)
    log.info("Validation succeeded")
    write_validation_output(results, output_file_with_date)


def generate_measures(definition_path, input_file, output_file):
    definition_module = load_module(definition_path)
    cohort_generator, index_date_range = load_cohort_generator(definition_module)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    measures = []
    for index_date in index_date_range:
        cohort = (
            cohort_generator() if index_date is None else cohort_generator(index_date)
        )
        input_file_with_date = _replace_filepath_pattern(input_file, index_date or "")
        measures = get_measures(cohort)
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
            measure_output_file = _replace_filepath_pattern(output_file, filename_part)
            results.to_csv(measure_output_file, index=False)
            log.info("Created measure output", output=output_file)

    # Combine any date-stamped files into one additional single file per measure
    # Use the measures from the latest cohort, since we only care about their ids here
    for measure in measures:
        combine_csv_files_with_dates(output_file, measure.id)
        log.info(f"Combined measure output for all dates in {output_file}")


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


def calculate_measures_results(measures, input_file):
    measures_manager = MeasuresManager(measures, input_file)
    yield from measures_manager.calculate_measures()


def load_cohort_classes(definition_module):
    return [
        obj
        for name, obj in inspect.getmembers(definition_module)
        if inspect.isclass(obj) and obj.__name__ == "Cohort"
    ]


def load_cohort_functions(definition_module):
    return [
        obj
        for name, obj in inspect.getmembers(definition_module)
        if inspect.isfunction(obj) and obj.__name__ == "cohort"
    ]


def load_dataset(definition_module):
    datasets = [
        obj
        for name, obj in inspect.getmembers(definition_module)
        if isinstance(obj, Dataset)
    ]
    if len(datasets) != 1:
        raise ValueError(
            "A dataset definition must contain one and only one 'Dataset' class"
        )
    return datasets[0]


def load_cohort_generator(definition_module):
    """
    Load the cohort definition module and identify the Cohort class or cohort generator
    function.
    Return a function that returns a Cohort class, and the index date range, if applicable.
    """
    cohort_classes = load_cohort_classes(definition_module)
    cohort_functions = load_cohort_functions(definition_module)

    if (len(cohort_classes) + len(cohort_functions)) != 1:
        raise ValueError(
            "A study definition must contain one and only one 'cohort' function or 'Cohort' class"
        )

    if cohort_classes:
        return lambda: cohort_classes[0], [None]

    cohort_function = cohort_functions[0]
    index_date_range = getattr(definition_module, "index_date_range", None)
    if index_date_range:  # pragma: no cover (Re-implement when testing with new QL)
        if list(inspect.signature(cohort_function).parameters.keys()) != ["index_date"]:
            raise ValueError(
                "A study definition with index_date_range must pass a single index_date argument to the 'cohort' function"
            )
    return cohort_function, index_date_range or [None]


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


def extract(
    cohort_definition: Cohort | Dataset | type, backend: BaseBackend
) -> Generator[dict[str, str], None, None]:
    """
    Extracts the cohort from the backend specified
    Args:
        cohort_definition: The definition of the Cohort
        backend: The Backend that the Cohort is being extracted from
    Returns:
        Yields the cohort as rows
    """
    backend.validate_contracts()
    cohort = get_column_definitions(cohort_definition)
    query_engine = backend.query_engine_class(cohort, backend)
    with query_engine.execute_query() as results:
        for row in results:
            yield dict(row)


def validate(
    cohort_class, backend
):  # pragma: no cover (Re-implement when testing with new QL)
    try:
        cohort = get_column_definitions(cohort_class)
        query_engine = backend.query_engine_class(cohort, backend)
        setup_queries, results_query, cleanup_queries = query_engine.get_queries()
        return setup_queries + [results_query] + cleanup_queries
    except Exception:
        log.error("Validation failed")
        # raise the exception to ensure the job fails and the error and traceback are logged
        raise


def write_output(
    results, output_file
):  # pragma: no cover (Re-implement when testing with new QL)
    with output_file.open(mode="w") as f:
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
