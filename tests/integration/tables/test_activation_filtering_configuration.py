import inspect

import pytest

from ehrql.query_model.nodes import SelectPatientTable, SelectTable
from ehrql.tables import core, tpp
from ehrql.tables.raw import core as core_raw
from ehrql.tables.raw import tpp as tpp_raw


@pytest.mark.parametrize("module", [core, core_raw, tpp, tpp_raw])
def test_all_tables_configure_activation_filtering(module):
    for name, obj in inspect.getmembers(module):
        if hasattr(obj, "_qm_node") and isinstance(
            obj._qm_node, (SelectTable, SelectPatientTable)
        ):
            meta = getattr(obj, "_meta", None)
            is_configured = hasattr(meta, "activation_filter_field") or hasattr(
                meta, "_activation_filtered"
            )
            assert is_configured, (
                f"{module.__name__}.{name} must configure GP activation filtering by specifying one of `activation_filter_field` or `_activation_filtered = False` in its _meta subclass"
            )
