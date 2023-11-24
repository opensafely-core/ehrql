import pytest

from ehrql.measures.disclosure_control import apply_sdc


@pytest.mark.parametrize("i,expected", [(6, 0), (7, 0), (8, 10)])
def test_apply_sdc(i, expected):
    assert apply_sdc(i) == expected


@pytest.mark.parametrize("bad_value", [-1, 7.1])
def test_apply_sdc_with_bad_value(bad_value):
    with pytest.raises(AssertionError):
        apply_sdc(bad_value)
