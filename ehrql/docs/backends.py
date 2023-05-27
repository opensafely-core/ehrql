import operator
import sys
from pathlib import Path

import ehrql
import ehrql.tables
from ehrql.docs.common import reformat_docstring
from ehrql.utils.module_utils import get_sibling_subclasses

from ..backends.base import BaseBackend


def build_backends():
    backends = get_sibling_subclasses(BaseBackend)
    backends.sort(key=operator.attrgetter("__name__"))

    for backend in backends:
        implements = [
            namespace.__name__.removeprefix(ehrql.tables.__name__ + ".")
            for namespace in backend.implements
        ]
        yield {
            "name": backend.display_name,
            "dotted_path": f"{backend.__module__}.{backend.__qualname__}",
            "file_path": relative_file_path(backend.__module__),
            "docstring": reformat_docstring(backend.__doc__),
            "implements": implements,
            # TODO: Backends no longer implement individual contracts but we leave this
            # empty list in place for now while we update the docs code which expects it
            "contracts": [],
        }


def relative_file_path(module_dotted_path):
    module_file = Path(sys.modules[module_dotted_path].__file__)
    ehrql_base = Path(ehrql.__file__).parents[1]
    return str(module_file.relative_to(ehrql_base))
