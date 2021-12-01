from __future__ import annotations

import csv
import importlib.util
import inspect
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path

import structlog

from .backends import BACKENDS
from .definition.base import cohort_registry
from .measure import MeasuresManager, combine_csv_files_with_dates
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

    cohort_class_generator, index_date_range = load_cohort_generator(module)
    if len(index_date_range) > 1 and "*" not in output_file.name:
        # ensure we have a replaceable pattern as an output file when multiple
        # dates ranges are to be output
        raise ValueError(f"No output pattern found in output file {output_file}")

    for index_date in index_date_range:
        if index_date is not None:
            log.info(f"Setting index_date to {index_date}")
            date_suffix = index_date
        else:
            date_suffix = ""

        if cohort_registry.cohorts:
            # Currently we expect at most one cohort to be registered
            assert (
                len(cohort_registry.cohorts) == 1
            ), f"At most one registered cohort is allowed, found {len(cohort_registry.cohorts)}"
            (cohort,) = cohort_registry.cohorts
        else:
            cohort = (
                cohort_class_generator(index_date)
                if index_date
                else cohort_class_generator()
            )
        cohort_action_function(
            cohort, index_date, output_file, date_suffix, **function_kwargs
        )


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
    else:
        backend = BACKENDS[backend_id](db_url, temporary_database=temporary_database)
        results = extract(cohort, backend)
        write_output(results, output_file_with_date)


def validate_cohort(
    cohort,
    index_date,
    output_file,
    date_suffix,
    backend_id,
):
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
    if index_date_range:
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


def extract(cohort_class, backend):
    cohort = get_column_definitions(cohort_class)
    query_engine = backend.query_engine_class(cohort, backend)
    with query_engine.execute_query() as results:
        for row in results:
            yield dict(row)


def validate(cohort_class, backend):
    try:
        cohort = get_column_definitions(cohort_class)
        query_engine = backend.query_engine_class(cohort, backend)
        return query_engine.get_queries()
    except Exception:
        log.error("Validation failed")
        # raise the exception to ensure the job fails and the error and traceback are logged
        raise


def write_output(results, output_file):
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


def write_validation_output(results, output_file):
    with output_file.open(mode="w") as f:
        for entry in results:
            f.write(f"{str(entry)}\n")
