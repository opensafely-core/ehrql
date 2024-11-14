import inspect
import sys


def show(element, label: str | None = None):
    """
    Show the output of the specified element within a dataset definition

    _element_<br>
    Any element within the dataset definition file; can be a string, constant value etc,
    but will typically be a dataset variable (filtered table, column, or a dataset itself.)

    _label_<br>
    Optional label which will be printed in the debug output.
    """
    line_no = inspect.getframeinfo(sys._getframe(1))[1]
    element_repr = repr(element)
    label = f" {label}" if label else ""
    print(f"Debug line {line_no}:{label}", file=sys.stderr)
    print(element_repr, file=sys.stderr)


def stop():
    """This doesn't do anything, it's just an indication that we should stop here"""
