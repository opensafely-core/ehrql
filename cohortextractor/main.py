import csv
import importlib
import inspect
import os
import sys
from pathlib import Path

from .backends import BACKENDS
from .query_utils import get_column_definitions


def main(workspace="/workspace", backend_id=None, db_url=None):
    if not db_url:
        db_url = os.environ["TPP_DATABASE_URL"]
    if not backend_id:
        backend_id = os.environ["BACKEND"]
    backend = BACKENDS[backend_id](db_url)
    cohort = load_cohort(workspace)
    results = extract(cohort, backend)
    write_output(results, workspace)


def load_cohort(workspace):
    sys.path.append(workspace)
    study_definition = importlib.import_module("study_definition")
    cohort_classes = [
        obj
        for name, obj in inspect.getmembers(study_definition)
        if inspect.isclass(obj)
    ]
    assert len(cohort_classes) == 1, "A study definition must contain one class only"
    return cohort_classes[0]


def extract(cohort, backend):
    cohort = get_column_definitions(cohort)
    query_engine = backend.query_engine_class(cohort, backend)
    results = query_engine.execute_query()

    for row in results:
        yield dict(row)
    query_engine.close()


def write_output(results, workspace):
    path = Path(workspace) / "outputs/cohort.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(mode="w") as f:
        writer = csv.writer(f)
        headers = None
        for entry in results:
            if not headers:
                headers = entry.keys()
                writer.writerow(headers)
            else:
                assert entry.keys == headers
            writer.writerow(entry.values())
