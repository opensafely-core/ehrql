import datetime

import pytest

from ehrql.backend_admin.emisv2.cleanup_temp_tables import (
    TABLE_NAME_PATTERN,
    table_is_older_than,
)


@pytest.mark.parametrize(
    "name,match",
    [
        # inline table match
        ("ehrql_20260101_1200_a1b2c3d4e5f6_inline_data_3", True),
        # tmp table match
        ("ehrql_20260101_1200_a1b2c3d4e5f6_tmp_7", True),
        ("foo", False),
        ("ehrql_results", False),
        # Too few hex chars
        ("ehrql_20260101_1200_a1b2c3_tmp_1", False),
        # Wrong suffix
        ("ehrql_20260101_1200_a1b2c3d4e5f6_other_1", False),
        # Missing counter
        ("ehrql_20260101_1200_a1b2c3d4e5f6_tmp_", False),
        # Mixed case hex disallowed (we use lowercase only)
        ("ehrql_20260101_1200_A1B2C3D4E5F6_tmp_1", False),
        # bad timestamp format
        ("ehrql_01122026_1200_a1b2c3d4e5f6_tmp_7", False),
    ],
)
def test_table_name_pattern_matches(name, match):
    if match:
        assert TABLE_NAME_PATTERN.match(name)
    else:
        assert TABLE_NAME_PATTERN.match(name) is None


@pytest.mark.parametrize(
    "table_name,older_than",
    [
        # match, older than cutoff
        ("ehrql_20260401_1200_a1b2c3d4e5f6_tmp_1", True),
        # match, not older than cutoff
        ("ehrql_20260515_1200_a1b2c3d4e5f6_tmp_1", False),
        # no matches
        ("ehrql_01012026_1200_a1b2c3d4e5f6_tmp_1", False),
        ("not_an_ehrql_table", False),
    ],
)
def test_is_older_than(table_name, older_than):
    cutoff = datetime.datetime(2026, 5, 1, tzinfo=datetime.UTC)
    assert table_is_older_than(table_name, cutoff) is older_than
