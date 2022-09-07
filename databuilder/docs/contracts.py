from databuilder import contracts
from databuilder.query_language import BaseFrame, Series

from ..module_utils import get_submodules
from .common import build_hierarchy, reformat_docstring


def build_contracts():
    """Build a dict representation for each Contract"""

    for dotted_path, contract in _get_contracts():
        columns = {k: v for k, v in vars(contract).items() if isinstance(v, Series)}
        columns = [_build_column(name, instance) for name, instance in columns.items()]

        docstring = reformat_docstring(contract.__doc__)
        hierarchy = build_hierarchy(contract)

        yield {
            "name": contract.__name__,
            "hierarchy": hierarchy,
            "dotted_path": dotted_path,
            "docstring": docstring,
            "columns": columns,
            "contract_support": [],
        }


def _get_contracts():
    for module in get_submodules(contracts):
        for name, value in vars(module).items():
            if isinstance(value, BaseFrame):
                yield f"{module.__name__}.{name}", value.__class__


def _build_column(name, instance):
    return {
        "name": name,
        "description": instance.description,
        "type": instance.type_.__name__,
        "constraints": [c.description for c in instance.constraints],
    }
