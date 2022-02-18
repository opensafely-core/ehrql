import json
import operator

from .backends.base import BaseBackend
from .contracts import contracts
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

    for v in vars(contracts).values():
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
    if d is None:
        return []

    docstring = d.strip()

    return [line.strip() for line in docstring.splitlines()]


def generate_docs(location=None):
    data = {
        "backends": list(_build_backends()),
        "contracts": list(_build_contracts()),
    }

    path = "public_docs.json"  # default to cwd
    if location is not None:
        path = location / path

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    print("Generated data for documentation")
