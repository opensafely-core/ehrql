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


# Marimo
DEFAULT_DATASET_CODE = "\n".join(
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


CELL_TEMPLATE = """\
    @app.cell{kwargs}
    def __():
        {indented_contents}
    """


def get_marimo_cell(content):
    indented = textwrap.indent(content, "  " * 4).lstrip()
    kwargs = "(hide_code=True)" if content.startswith("mo.md") else ""
    return textwrap.dedent(
        CELL_TEMPLATE.format(
            kwargs=kwargs,
            indented_contents=indented,
        )
    )


MARIMO_TEMPLATE = "\n\n".join(
    [
        textwrap.dedent("""\
                import sys
                import marimo

                sys.path.append({cwd!r})

                __generated_with = "0.9.14"
                app = marimo.App(width="medium")
                """),
        get_marimo_cell(
            "\n".join(
                [
                    "import marimo as mo\nimport ehrql.sandbox",
                    "ehrql.sandbox.load_data({dummy_tables_path!r})",
                ]
            )
        ),
        "{cells}",
        textwrap.dedent("""\
                if __name__ == "__main__":
                    app.run()
                """),
    ]
)


def get_marimo_code(cwd, dummy_tables_path, cell_contents):
    cells = "\n\n".join([get_marimo_cell(content) for content in cell_contents])
    return MARIMO_TEMPLATE.format(
        cwd=cwd,
        dummy_tables_path=dummy_tables_path,
        cells=cells,
    )


def _run_marimo(tmp_notebook_path, marimo_code):
    tmp_notebook_path.write_text(marimo_code)
    try:
        subprocess.run(["marimo", "edit", tmp_notebook_path])
    except Exception as e:
        print(e)
        print(tmp_notebook_path)


def run_marimo(dummy_tables_path, definition_file=None):  # pragma: no cover
    if definition_file is not None:
        dataset_code = definition_file.read_text()
        dataset_name = definition_file.name
        cwd = str(definition_file.parent)
    else:
        dataset_code = DEFAULT_DATASET_CODE
        dataset_name = "sandbox"
        cwd = "."
    tmp_notebook_path = Path(tempfile.mkstemp(suffix=f"_{dataset_name}.py")[1])
    marimo_code = get_marimo_code(cwd, str(dummy_tables_path), [dataset_code])
    _run_marimo(tmp_notebook_path, marimo_code)


def run_quiz():
    path = Path(__file__).parent / "example-data"
    marimo_code = get_marimo_code(
        ".",
        str(path),
        [
            DEFAULT_DATASET_CODE,
            "from ehrql.quiz import questions",
        ],
    )
    tmp_notebook_path = Path(tempfile.mkstemp(suffix="_quiz.py")[1])
    _run_marimo(tmp_notebook_path, marimo_code)
