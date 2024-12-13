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
    Show the output of the specified element within a dataset definition

    _element_<br>
    Any element within the dataset definition file; can be a string, constant value etc,
    but will typically be a dataset variable (filtered table, column, or a dataset itself.)

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
    print(render(element, *other_elements, head=head, tail=tail), file=sys.stderr)


def render(
    element,
    *other_elements,
    head: int | None = None,
    tail: int | None = None,
):
    elements = [element, *other_elements]

    if (
        len(elements) > 1
        and hasattr(element, "__repr_related__")
        and elements_are_related_series(elements)
    ):
        element_reprs = [element.__repr_related__(*other_elements)]
    else:
        element_reprs = [repr(el) for el in elements]

    if head or tail:
        element_reprs = [
            truncate_table(el_repr, head, tail) for el_repr in element_reprs
        ]
    return "\n".join(element_reprs)


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
