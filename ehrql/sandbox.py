import code
import readline
import rlcompleter
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import ehrql
import ehrql.tables.core
from ehrql.query_engines.sandbox import SandboxQueryEngine
from ehrql.query_language import BaseFrame, BaseSeries, Dataset
from ehrql.utils.traceback_utils import get_trimmed_traceback


def run(dummy_tables_path):
    # Create a query engine using data at given path.  A user will be able to interact
    # with this data via a Python REPL.
    engine = SandboxQueryEngine(dummy_tables_path)

    # Overwrite __repr__ methods to display contents of frame/series.
    BaseFrame.__repr__ = lambda self: repr(engine.evaluate(self))
    BaseSeries.__repr__ = lambda self: repr(engine.evaluate(self))
    Dataset.__repr__ = lambda self: repr(engine.evaluate_dataset(self))

    # Set up readline etc.
    sys.__interactivehook__()

    # Set up exception handler to trim tracebacks
    sys.excepthook = excepthook

    # Set up namespace for tab-completion.
    namespace = {}
    readline.set_completer(rlcompleter.Completer(namespace).complete)

    # Start running a Python REPL.
    code.interact(local=namespace)


def excepthook(type_, exc, tb):
    traceback = get_trimmed_traceback(exc, "<console>")
    sys.stderr.write(traceback)


def load_data(dummy_tables_path):  # pragma: no cover
    engine = SandboxQueryEngine(dummy_tables_path)

    # Overwrite _repr_markdown_ methods to display contents of frame/series.
    BaseFrame._repr_markdown_ = lambda self: engine.evaluate(self)._repr_markdown_()
    BaseSeries._repr_markdown_ = lambda self: engine.evaluate(self)._repr_markdown_()
    Dataset._repr_markdown_ = lambda self: engine.evaluate_dataset(
        self
    )._repr_markdown_()


def run_marimo(dummy_tables_path, definition_file=None):  # pragma: no cover
    if definition_file is not None:
        dataset_code = definition_file.read_text()
        dataset_name = definition_file.name
        cwd = definition_file.parent
    else:
        dataset_code = "\n".join(
            [
                "from ehrql import (",
                *(f"    {name}," for name in ehrql.__all__),
                ")",
                "from ehrql.tables.core import (",
                *(f"    {name}," for name in ehrql.tables.core.__all__),
                ")",
                "",
                "",
                "dataset = create_dataset()",
            ]
        )
        dataset_name = "sandbox"
        cwd = "."

    indented_code = textwrap.indent(dataset_code, "            ").lstrip()
    notebook_code = textwrap.dedent(
        f"""\
        import sys
        import marimo

        sys.path.append({str(cwd)!r})

        __generated_with = "0.9.14"
        app = marimo.App(width="medium")


        @app.cell
        def __():
            import ehrql.sandbox
            ehrql.sandbox.load_data({str(dummy_tables_path)!r})


        @app.cell
        def __():
            {indented_code}

        if __name__ == "__main__":
            app.run()
        """
    )
    tmp_notebook = Path(tempfile.mkstemp(suffix=f"_{dataset_name}.py")[1])
    tmp_notebook.write_text(notebook_code)

    subprocess.run(["marimo", "edit", tmp_notebook])
