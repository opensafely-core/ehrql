from collections import defaultdict

from databuilder import tables
from databuilder.query_language import BaseFrame, Series

from ..module_utils import get_submodules
from .common import reformat_docstring


def build_schemas(backends=()):
    module_name_to_backends = build_module_name_to_backend_map(backends)

    for module in get_submodules(tables):
        module_tables = list(build_tables(module))
        if not module_tables:
            continue

        docstring = reformat_docstring(module.__doc__)
        dotted_path = module.__name__
        hierarchy = dotted_path.removeprefix(f"{tables.__name__}.").split(".")
        implemented_by = [
            backend_name for backend_name in module_name_to_backends[module.__name__]
        ]

        yield {
            "dotted_path": dotted_path,
            "hierarchy": hierarchy,
            "docstring": docstring,
            "implemented_by": implemented_by,
            "tables": sorted(module_tables, key=lambda t: t["name"]),
        }


def build_module_name_to_backend_map(backends):
    module_name_to_backends = defaultdict(list)
    for backend in backends:
        for module_name in backend["implements"]:
            module_name_to_backends[module_name].append(backend["name"])
    return module_name_to_backends


def build_tables(module):
    for name, obj in vars(module).items():
        if not isinstance(obj, BaseFrame):
            continue
        cls = obj.__class__
        docstring = reformat_docstring(cls.__doc__)
        columns = [
            build_column(attr.name, attr)
            for attr in vars(cls).values()
            if isinstance(attr, Series)
        ]

        yield {
            "name": name,
            "docstring": docstring,
            "columns": columns,
        }


def build_column(name, series):
    return {
        "name": name,
        "description": series.description,
        "type": series.type_.__name__,
        "constraints": [c.description for c in series.constraints],
    }
