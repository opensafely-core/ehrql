import code
import sys

from ehrql.debugger import activate_debug_context
from ehrql.renderers import DISPLAY_RENDERERS
from ehrql.utils.traceback_utils import get_trimmed_traceback


def run(dummy_tables_path):
    # Set up readline etc.
    sys.__interactivehook__()

    # Set up exception handler to trim tracebacks
    sys.excepthook = excepthook

    # Set up namespace for tab-completion.
    namespace = {}

    # The readline library is not available in pyodide, it uses a different
    # readline implementation that is enabled by default
    try:
        import readline
        import rlcompleter

        readline.set_completer(rlcompleter.Completer(namespace).complete)
    except ImportError:
        pass

    # Start running a Python REPL.
    with activate_debug_context(
        dummy_tables_path=dummy_tables_path,
        render_function=DISPLAY_RENDERERS["ascii"],
    ):
        code.interact(local=namespace)


def excepthook(type_, exc, tb):
    traceback = get_trimmed_traceback(exc, "<console>")
    sys.stderr.write(traceback)
