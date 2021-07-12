import csv
import importlib.util
import inspect
import sys
from contextlib import contextmanager

from .backends import BACKENDS
from .query_utils import get_column_definitions


def main(definition_path, output_file, backend_id, db_url):
    backend = BACKENDS[backend_id](db_url)
    cohort = load_cohort(definition_path)
    results = extract(cohort, backend)
    write_output(results, output_file)


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


def write_output(results, output_file):
    output_file.parent.mkdir(parents=True, exist_ok=True)
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
