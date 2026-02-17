from ehrql.permissions import format_table_list, parse_permissions
from ehrql.query_model import nodes as qm
from ehrql.tables.core import clinical_events, patients


def test_parse_permissions_handles_empty_value():
    assert parse_permissions({}) == set()
    assert parse_permissions({"EHRQL_PERMISSIONS": ""}) == set()


def test_format_table_list():
    assert (
        format_table_list(
            [
                patients._qm_node,
            ]
        )
        == "`core.patients` table"
    )
    assert (
        format_table_list(
            [
                patients._qm_node,
                clinical_events._qm_node,
            ]
        )
        == "`core.patients` and `core.clinical_events` tables"
    )

    # Create an unregistered table node
    table_node = qm.SelectTable("some_table", schema=qm.TableSchema())

    assert (
        format_table_list(
            [
                table_node,
            ]
        )
        == "`some_table` table"
    )
