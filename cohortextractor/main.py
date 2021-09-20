import calendar
import csv
import datetime
import importlib.util
import inspect
import re
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path

import structlog

from .backends import BACKENDS
from .measure import Measure, MeasuresManager
from .query_utils import get_column_definitions, get_measures
from .validate_dummy_data import validate_dummy_data


log = structlog.getLogger()


def generate_cohort(
    definition_path,
    output_file,
    backend_id,
    db_url,
    index_date_range=None,
    dummy_data_file=None,
    temporary_database=None,
):
    log.info(
        f"Generating cohort for {definition_path.name} as {output_file}",
    )
    log.debug(
        "args:",
        definition_path=definition_path,
        output_file=output_file,
        backend=backend_id,
        index_date_range=index_date_range,
        dummy_data_file=dummy_data_file,
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)

    for index_date in _generate_date_range(index_date_range):
        if index_date is not None:
            log.info(f"Setting index_date to {index_date}")
            date_suffix = f"_{index_date}"
        else:
            date_suffix = ""
        cohort = load_cohort(definition_path, index_date)
        output_file_with_date = Path(str(output_file).replace("*", date_suffix))
        if dummy_data_file and not db_url:
            dummy_data_file_with_date = Path(
                str(dummy_data_file).replace("*", date_suffix)
            )
            validate_dummy_data(
                cohort, dummy_data_file_with_date, output_file_with_date
            )
            shutil.copyfile(dummy_data_file_with_date, output_file_with_date)
        else:
            backend = BACKENDS[backend_id](
                db_url, temporary_database=temporary_database
            )
            results = extract(cohort, backend)
            write_output(results, output_file_with_date)


def _generate_date_range(date_range_str):
    # Bail out with an "empty" range: this means we don't need separate
    # codepaths to handle the range, single date, and no date supplied cases
    if not date_range_str:
        return [None]
    start, end, period = _parse_date_range(date_range_str)
    if end < start:
        raise ValueError(
            f"Invalid date range '{date_range_str}': end cannot be earlier than start"
        )
    dates = []
    while start <= end:
        dates.append(start.isoformat())
        start = _increment_date(start, period)
    # The latest data is generally more interesting/useful so we may as well
    # extract that first
    dates.reverse()
    return dates


def _parse_date_range(date_range_str):
    period = "month"
    if " to " in date_range_str:
        start, end = date_range_str.split(" to ", 1)
        if " by " in end:
            end, period = end.split(" by ", 1)
    else:
        start = end = date_range_str
    try:
        start = _parse_date(start)
        end = _parse_date(end)
    except ValueError:
        raise ValueError(
            f"Invalid date range '{date_range_str}': Dates must be in YYYY-MM-DD "
            f"format or 'today' and ranges must be in the form "
            f"'DATE to DATE by (week|month)'"
        )
    if period not in ("week", "month"):
        raise ValueError(f"Unknown time period '{period}': must be 'week' or 'month'")
    return start, end, period


def _parse_date(date_str):
    if date_str == "today":
        return datetime.date.today()
    else:
        return datetime.date.fromisoformat(date_str)


def _increment_date(date, period):
    if period == "week":
        return date + datetime.timedelta(days=7)
    elif period == "month":
        if date.month < 12:
            try:
                return date.replace(month=date.month + 1)
            except ValueError:
                # If the month we've replaced the date in is out of range, it will be at the end
                # of a month which has fewer days than the previous month (e.g. 31st Aug + 1 month)
                # set to last day of previous month instead
                _, last_day_of_month = calendar.monthrange(date.year, date.month)
                return date.replace(day=last_day_of_month)
        else:
            return date.replace(month=1, year=date.year + 1)
    else:
        raise ValueError(f"Unknown time period '{period}'")


def generate_measures(definition_path, input_file, output_file):
    cohort = load_cohort(definition_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    for measure_id, results in calculate_measures_results(cohort, input_file):
        measure_output_file = str(output_file).replace("*", measure_id)
        results.to_csv(measure_output_file, index=False)
        log.info("Created measure output", output=output_file)


def calculate_measures_results(cohort, input_file):
    measures = get_measures(cohort)
    measures_manager = MeasuresManager(measures, input_file)
    yield from measures_manager.calculate_measures()


def load_cohort(definition_path, index_date=None):
    definition_module = load_module(definition_path, index_date)
    imported_classes = [Measure]
    cohort_classes = [
        obj
        for name, obj in inspect.getmembers(definition_module)
        if inspect.isclass(obj) and obj not in imported_classes
    ]
    assert len(cohort_classes) == 1, "A study definition must contain one class only"
    return cohort_classes[0]


def load_module(definition_path, index_date=None):
    if index_date is not None:
        with temp_definition_path(definition_path, index_date) as temp_path:
            with open(definition_path, "r") as orig, open(temp_path, "w") as new:
                # Copy the cohort definition file, replace the BASE_INDEX_DATE definition
                # with the current index date and load this modified module
                contents = orig.read()
                pattern = r"(BASE_INDEX_DATE\s*=\s*.+)([\s|\n].*)"
                contents = re.sub(
                    pattern, rf'BASE_INDEX_DATE = "{index_date}"\2', contents
                )
                new.write(contents)
            module = _load_module(temp_path)
        return module
    return _load_module(definition_path)


def _load_module(definition_path):
    # Add the directory containing the definition to the path so that the definition can import library modules from
    # that directory
    definition_dir = definition_path.parent
    module_name = definition_path.stem
    with added_to_path(str(definition_dir)):
        module = importlib.import_module(module_name)
        # Reload the module in case a module with the same name was loaded previously
        importlib.reload(module)
        return module


@contextmanager
def temp_definition_path(definition_path, index_date):
    temp_path = definition_path.parent / f"{definition_path.stem}_{index_date}.py"
    yield temp_path
    temp_path.unlink()


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
