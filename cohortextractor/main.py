import csv
import importlib.util
import inspect
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path

from cohortextractor.backends import BACKENDS
from cohortextractor.query_utils import get_column_definitions
from cohortextractor.validate_dummy_data import (
    DummyDataValidationError,
    validate_dummy_data,
)


def main(definition_path, output_file, backend_id, db_url, dummy_data_file=None):
    cohort = load_cohort(definition_path)

    if dummy_data_file:
        results = None
        if Path(output_file).suffixes != dummy_data_file.suffixes:
            expected_extension = "".join(output_file.suffixes)
            msg = f"Expected dummy data file with extension {expected_extension}; got {dummy_data_file}"
            raise DummyDataValidationError(msg)
        validate_dummy_data(get_column_definitions(cohort), dummy_data_file)
    else:
        backend = BACKENDS[backend_id](db_url)
        results = extract(cohort, backend)
    write_output(results, output_file, dummy_data_file=dummy_data_file)


def load_cohort(definition_path):
    definition_module = load_module(definition_path)
    cohort_classes = [
        obj
        for name, obj in inspect.getmembers(definition_module)
        if inspect.isclass(obj)
    ]
    assert len(cohort_classes) == 1, "A study definition must contain one class only"
    return cohort_classes[0]


def load_module(definition_path):
    definition_dir = definition_path.parent
    module_name = definition_path.stem

    # Add the directory containing the definition to the path so that the definition can import library modules from
    # that directory
    with added_to_path(str(definition_dir)):
        return importlib.import_module(module_name)


@contextmanager
def added_to_path(directory):
    original = sys.path.copy()
    sys.path.append(directory)
    try:
        yield
    finally:
        sys.path = original


def extract(cohort, backend):
    cohort = get_column_definitions(cohort)
    query_engine = backend.query_engine_class(cohort, backend)
    with query_engine.execute_query() as results:
        for row in results:
            yield dict(row)


def write_output(results, output_file, dummy_data_file=None):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    if dummy_data_file:
        shutil.copyfile(dummy_data_file, output_file)
    else:
        with output_file.open(mode="w") as f:
            writer = csv.writer(f)
            headers = None
            for entry in results:
                if not headers:
                    headers = entry.keys()
                    writer.writerow(headers)
                else:
                    assert entry.keys == headers
                writer.writerow(entry.values())
