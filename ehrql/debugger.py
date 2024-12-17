import contextlib
import inspect
import sys

from ehrql.query_engines.in_memory_database import (
    EventColumn,
    PatientColumn,
    render_value,
)
from ehrql.query_engines.sandbox import SandboxQueryEngine
from ehrql.query_language import BaseFrame, BaseSeries, Dataset, DateDifference
from ehrql.query_model import nodes as qm
from ehrql.renderers import truncate_table
from ehrql.utils.docs_utils import exclude_from_docs


DEBUG_QUERY_ENGINE = None


@exclude_from_docs
def show(
    element,
    *other_elements,
    label: str | None = None,
    head: int | None = None,
    tail: int | None = None,
):
    """
    Show the output of the specified element or elements

    _element_<br>
    Any ehrql object, such as a series, frame, or dataset

    _other_elements_<br>
    0 or more series, but only if the _element_ was also a series, and only if they are all
    from the same domain

    _label_<br>
    Optional label which will be printed in the show output.

    _head_<br>
    Show only the first N lines. If the output is an ehrQL column, table or dataset, it will
    print only the first N lines of the table.

    _tail_<br>
    Show only the last N lines. If the output is an ehrQL column, table or dataset, it will
    print only the last N lines of the table.

    head and tail arguments can be combined, e.g. to show the first and last 5 lines of a table:

      show(<table>, head=5, tail=5)
    """
    line_no = inspect.getframeinfo(sys._getframe(1))[1]
    label = f" {label}" if label else ""
    print(f"Show line {line_no}:{label}", file=sys.stderr)

    if DEBUG_QUERY_ENGINE is None:
        # We're not in debug mode so ignore
        print(
            " - show() ignored because we're not running in debug mode", file=sys.stderr
        )
        return

    elements = [element, *other_elements]

    is_single_ehrql_object = is_ehrql_object(element) and len(other_elements) == 0
    is_multiple_series_same_domain = len(elements) > 1 and elements_are_related_series(
        elements
    )

    # We throw an error unless show() is called with:
    # 1. A single ehrql object (series, frame, dataset)
    # 2. Multiple series drawn from the same domain
    if is_single_ehrql_object | is_multiple_series_same_domain:
        print(render(element, *other_elements, head=head, tail=tail), file=sys.stderr)
    else:
        raise TypeError(
            "\n\nshow() can be used in two ways. Either:\n"
            " - call it with a single argument such as:\n"
            "     show(dataset)\n"
            "     show(patients)\n"
            '     show(clinical_events.date.is_after("2024-01-01"))\n'
            " - or call it with multiple columns/series:\n"
            "     show(patients.sex, patients.date_of_birth)\n"
            '     show(patients.sex == "male", patients.date_of_birth.is_before("2006-01-01"))\n\n'
            "If passing in multiple arguments, they must either have:\n"
            " - one row per patient (e.g. patients.sex, clinical_events.count_for_patient()), or\n"
            " - multiple rows per patient AND be from the same table (e.g. clinical_events.date, "
            "clinical_events.numeric_values)"
        )


def render(
    element,
    *other_elements,
    head: int | None = None,
    tail: int | None = None,
):
    if len(other_elements) == 0:
        # single ehrql element so we just display it
        element_repr = repr(element)
    elif hasattr(element, "__repr_related__"):
        # multiple ehrql series so we combine them
        element_repr = element.__repr_related__(*other_elements)
    else:
        raise TypeError(
            "When render() is called on multiple series, the first argument must have a __repr_related__ attribute."
        )

    if head or tail:
        element_repr = truncate_table(element_repr, head, tail)
    return element_repr


@contextlib.contextmanager
def activate_debug_context(*, dummy_tables_path, render_function):
    global DEBUG_QUERY_ENGINE

    # Record original methods
    BaseFrame__repr__ = BaseFrame.__repr__
    BaseSeries__repr__ = BaseSeries.__repr__
    DateDifference__repr__ = DateDifference.__repr__
    Dataset__repr__ = Dataset.__repr__

    query_engine = SandboxQueryEngine(dummy_tables_path)
    DEBUG_QUERY_ENGINE = query_engine

    def repr_ehrql(obj, template=None):
        return query_engine.evaluate(obj)._render_(render_function)

    def repr_related_ehrql(*series_args):
        return render_function(
            related_columns_to_records(
                [query_engine.evaluate(series) for series in series_args]
            )
        )

    # Temporarily overwrite __repr__ methods to display contents
    BaseFrame.__repr__ = repr_ehrql
    BaseSeries.__repr__ = repr_ehrql
    DateDifference.__repr__ = repr_ehrql
    Dataset.__repr__ = repr_ehrql

    # Add additional method for displaying related series together
    BaseSeries.__repr_related__ = repr_related_ehrql
    DateDifference.__repr_related__ = repr_related_ehrql

    try:
        yield
    finally:
        DEBUG_QUERY_ENGINE = None
        # Restore original methods
        BaseFrame.__repr__ = BaseFrame__repr__
        BaseSeries.__repr__ = BaseSeries__repr__
        DateDifference.__repr__ = DateDifference__repr__
        Dataset.__repr__ = Dataset__repr__
        del BaseSeries.__repr_related__
        del DateDifference.__repr_related__


def elements_are_related_series(elements):
    # We render a DateDifference in days. A DateDifference itself isn't a Series, so we need to convert it
    # to days before we can compare it with other elements.
    elements = [el.days if isinstance(el, DateDifference) else el for el in elements]

    qm_nodes = [getattr(el, "_qm_node", None) for el in elements]
    if not all(isinstance(node, qm.Series) for node in qm_nodes):
        return False
    domains = {qm.get_domain(node) for node in qm_nodes}
    return len(domains) == 1


def related_columns_to_records(columns):
    if isinstance(columns[0], PatientColumn):
        return related_patient_columns_to_records(columns)
    elif isinstance(columns[0], EventColumn):
        return related_event_columns_to_records(columns)
    else:
        assert False


def related_patient_columns_to_records(columns):
    patients_all = set()
    for c in columns:
        patients_all.update(c.patient_to_value.keys())
    for patient_id in sorted(patients_all):
        record = {"patient_id": patient_id}
        for i, column in enumerate(columns, start=1):
            record[f"series_{i}"] = render_value(column[patient_id], convert_null=True)
        yield record


def related_event_columns_to_records(columns):
    for patient_id, row in columns[0].patient_to_rows.items():
        for row_id in row.keys():
            record = {"patient_id": patient_id, "row_id": row_id}
            for i, column in enumerate(columns, start=1):
                record[f"series_{i}"] = render_value(
                    column[patient_id][row_id], convert_null=True
                )
            yield record


def is_ehrql_object(element):
    # Currently this is just if the thing is a Frame, BaseSeries, DateDifference
    # or Dataset, and only used by the show() method. NB - show() doesn't work
    # with Measures, so this doesn't check for them
    is_frame = isinstance(getattr(element, "_qm_node", None), qm.Frame)
    return is_frame | isinstance(element, BaseSeries | DateDifference | Dataset)
