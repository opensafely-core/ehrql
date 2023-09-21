import pytest

from ehrql.query_language import BaseFrame
from ehrql.tables.beta import tpp
from ehrql.tables.examples import tutorial


@pytest.mark.parametrize("module", [tpp, tutorial])
def test___all__(module):
    assert module.__all__ == sorted(module.__all__)
    table_names = {
        type(obj).__name__
        for obj in vars(module).values()
        if isinstance(obj, BaseFrame)
    }
    assert table_names == set(module.__all__)
