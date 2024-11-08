import inspect
import sys


def show(element):
    """
    Show the output of the specified element within a
    dataset definition (a string, value, dataset variable, table
    etc.)
    """
    line_no = inspect.getframeinfo(sys._getframe(1))[1]
    print(f"Debug at line {line_no}:", file=sys.stderr)
    print(element, file=sys.stderr)


def stop():
    """
    Stop loading the dataset definition at this point and show the
    current contents of the dataset.
    """
