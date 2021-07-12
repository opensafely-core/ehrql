import csv
import importlib.util
import inspect

from .backends import BACKENDS
from .query_utils import get_column_definitions


def main(definition_path, output_file, backend_id, db_url):
    backend = BACKENDS[backend_id](db_url)
    cohort = load_cohort(definition_path)
    results = extract(cohort, backend)
    write_output(results, output_file)


def load_cohort(definition):
    cohort_definition = load_module_by_path(definition)
    cohort_classes = [
        obj
        for name, obj in inspect.getmembers(cohort_definition)
        if inspect.isclass(obj)
    ]
    assert len(cohort_classes) == 1, "A study definition must contain one class only"
    return cohort_classes[0]


def load_module_by_path(path):
    # We have to jump through hoops here because the thing we've got in our hand is the full path of the file where the
    # module is defined.
    spec = importlib.util.spec_from_file_location("cohort_definition", path)
    cohort_definition = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cohort_definition)
    return cohort_definition


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
