import pytest

import ehrql.tables
from ehrql.query_language import BaseFrame
from ehrql.utils.module_utils import get_submodules


@pytest.mark.parametrize("module", list(get_submodules(ehrql.tables)))
def test___all__(module):
    table_names = {
        name for name, obj in vars(module).items() if isinstance(obj, BaseFrame)
    }
    if not table_names:
        pytest.skip(f"{module.__name__} has no tables")
    assert module.__all__ == sorted(module.__all__)
    assert table_names == set(module.__all__)
