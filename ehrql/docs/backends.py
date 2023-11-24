import sys
from pathlib import Path

import ehrql
import ehrql.tables
from ehrql.utils.module_utils import get_sibling_subclasses

from ..backends.base import SQLBackend
from .common import get_docstring


SORT_ORDER = {k: i for i, k in enumerate(["TPP", "EMIS"])}


def build_backends():
    backend_classes = get_sibling_subclasses(SQLBackend)

    backends = []
    for backend in backend_classes:
        implements = [
            namespace.__name__.removeprefix(ehrql.tables.__name__ + ".")
            for namespace in backend.implements
        ]
        backends.append(
            {
                "name": backend.display_name,
                "dotted_path": f"{backend.__module__}.{backend.__qualname__}",
                "file_path": relative_file_path(backend.__module__),
                "docstring": get_docstring(backend),
                "implements": implements,
            }
        )

    backends.sort(key=sort_key)
    return backends


def relative_file_path(module_dotted_path):
    module_file = Path(sys.modules[module_dotted_path].__file__)
    ehrql_base = Path(ehrql.__file__).parents[1]
    return str(module_file.relative_to(ehrql_base))


def sort_key(obj):
    k = obj["name"]
    return SORT_ORDER.get(k, float("+inf")), k
