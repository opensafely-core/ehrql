import code
import sys

from ehrql.query_engines.csv import CSVQueryEngine
from ehrql.query_language import BaseFrame, BaseSeries


def run(dummy_tables_path):
    # Create a CSV query engine using data at given path.  A user will be able to
    # interact with this data via a Python REPL.
    engine = CSVQueryEngine(dummy_tables_path)

    # Overwrite __repr__ methods to display contents of frame/series.
    BaseFrame.__repr__ = lambda self: repr(engine.evaluate(self))
    BaseSeries.__repr__ = lambda self: repr(engine.evaluate(self))

    # Set up readline etc.
    sys.__interactivehook__()

    # Start running a Python REPL.
    code.interact()
