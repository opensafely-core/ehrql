from ..contracts.base import Column, TableContract
from ..module_utils import get_sibling_subclasses
from .common import build_hierarchy, reformat_docstring


def build_contracts():
    """Build a dict representation for each Contract"""

    for contract in get_sibling_subclasses(TableContract):
        columns = {k: v for k, v in vars(contract).items() if isinstance(v, Column)}
        columns = [_build_column(name, instance) for name, instance in columns.items()]

        docstring = reformat_docstring(contract.__doc__)
        dotted_path = f"{contract.__module__}.{contract.__qualname__}"

        hierarchy = build_hierarchy(contract)

        yield {
            "name": contract.__name__,
            "hierarchy": hierarchy,
            "dotted_path": dotted_path,
            "docstring": docstring,
            "columns": columns,
            "contract_support": [],
        }


def _build_column(name, instance):
    return {
        "name": name,
        "description": instance.description,
        "type": instance.type.__class__.__name__,
        "constraints": [c.description for c in instance.constraints],
    }
