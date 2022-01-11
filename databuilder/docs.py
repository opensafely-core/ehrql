import json
import operator

from .backends.base import BaseBackend
from .contracts import tables
from .contracts.base import TableContract


def _build_backends():
    backends = sorted(BaseBackend.__subclasses__(), key=operator.attrgetter("__name__"))

    for backend in backends:
        tables = [getattr(backend, name) for name in backend.tables]
        tables = [table.implements.__name__ for table in tables if table.implements]
        yield {
            "name": backend.__name__,
            "tables": tables,
        }


def _build_contracts():
    """Build a dict representation for each Contract"""

    for v in vars(tables).values():
        if not (
            isinstance(v, type) and v != TableContract and issubclass(v, TableContract)
        ):
            continue
        contract = v
        docstring = _reformat_docstring(contract.__doc__)
        dotted_path = f"{contract.__module__}.{contract.__qualname__}"

        yield {
            "name": contract.__name__,
            "dotted_path": dotted_path,
            "docstring": docstring,
            "columns": [],
            "contract_support": [],
        }


def _reformat_docstring(d):
    """Reformat docstring to make it easier to use in a markdown/HTML document."""
    docstring = d.strip()

    return [line.strip() for line in docstring.split("\n")]


def generate_docs():
    data = {
        "contracts": list(_build_contracts()),
        "backends": list(_build_backends()),
    }

    with open("backend_docs.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Generated data for backends")
