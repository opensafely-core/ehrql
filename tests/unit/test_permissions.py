from ehrql.permissions import format_table_list
from ehrql.query_model import nodes as qm
from ehrql.tables.core import clinical_events, patients


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
