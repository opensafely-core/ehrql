import inspect
import sys

from ehrql.renderers import truncate_table
from ehrql.utils.docs_utils import exclude_from_docs


@exclude_from_docs
def show(
    element, label: str | None = None, head: int | None = None, tail: int | None = None
):
    """
    Show the output of the specified element within a dataset definition

    _element_<br>
    Any element within the dataset definition file; can be a string, constant value etc,
    but will typically be a dataset variable (filtered table, column, or a dataset itself.)

    _label_<br>
    Optional label which will be printed in the debug output.

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
    element_repr = repr(element)
    if head or tail:
        element_repr = truncate_table(element_repr, head, tail)
    label = f" {label}" if label else ""
    print(f"Debug line {line_no}:{label}", file=sys.stderr)
    print(element_repr, file=sys.stderr)


def stop(*, head: int | None = None, tail: int | None = None):
    """
    Stop loading the dataset definition and show the contents of the dataset at this point.

    _head_<br>
    Show only the first N lines of the dataset.

    _tail_<br>
    Show only the last N lines of the dataset.

    head and tail arguments can be combined, e.g. to show the first and last 5 lines of the dataset:

      stop(head=5, tail=5)
    """
    line_no = inspect.getframeinfo(sys._getframe(1))[1]
    print(f"Stopping at line {line_no}", file=sys.stderr)
