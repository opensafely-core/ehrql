import pytest
import sqlalchemy

from ehrql.backend_admin.tpp import maintenance_mode
from ehrql.backends.tpp import TPPBackend
from tests.backend_schemas.tpp.schema import BuildProgress


@pytest.mark.parametrize(
    "description,events,is_in_maintenance_mode,expected_build_count",
    [
        (
            "No OpenSAFELY events",
            [
                {
                    "Event": "Swap Tables",
                    "BuildStart": "2004-05-23T14:35:10",
                    "EventStart": "2004-05-23T14:35:10",
                    "EventEnd": "2004-05-23T15:15:10",
                    "Duration": 40,
                }
            ],
            False,
            0,
        ),
        (
            "Historical finished maintenance mode",
            [
                {
                    "Event": "OpenSAFELY",
                    "BuildStart": "2004-05-23T14:25:10",
                    "EventStart": "2004-05-23T14:25:10",
                    "EventEnd": "2004-05-23T15:25:10",
                    "Duration": 60,
                },
                {
                    "Event": "Swap Tables",
                    "BuildStart": "2004-05-23T14:35:10",
                    "EventStart": "2004-05-23T14:35:10",
                    "EventEnd": "2004-05-23T15:15:10",
                    "Duration": 40,
                },
                {
                    "Event": "CodedEvent_SNOMED",
                    "BuildStart": "2004-05-23T15:15:10",
                    "EventStart": "2004-05-23T15:15:10",
                    "EventEnd": "2004-05-23T15:25:10",
                    "Duration": 10,
                },
            ],
            False,
            0,
        ),
        (
            "Historical unfinished maintenance mode",
            [
                {
                    "Event": "OpenSAFELY",
                    "BuildStart": "2005-06-12T14:25:10",
                    "EventStart": "2005-06-12T14:25:10",
                    "EventEnd": "9999-12-31T00:00:00",
                    "Duration": None,
                },
                {
                    "Event": "Swap Tables",
                    "BuildStart": "2005-06-12T14:25:10",
                    "EventStart": "2005-06-12T14:25:10",
                    "EventEnd": "9999-12-31T00:00:00",
                    "Duration": None,
                },
                {
                    "Event": "OpenSAFELY",
                    "BuildStart": "2024-05-23T14:25:10",
                    "EventStart": "2024-05-23T14:25:10",
                    "EventEnd": "2004-05-23T15:25:10",
                    "Duration": 60,
                },
                {
                    "Event": "Swap Tables",
                    "BuildStart": "2024-05-23T14:35:10",
                    "EventStart": "2024-05-23T14:35:10",
                    "EventEnd": "2024-05-23T15:15:10",
                    "Duration": 40,
                },
                {
                    "Event": "CodedEvent_SNOMED",
                    "BuildStart": "2024-05-23T15:15:10",
                    "EventStart": "2024-05-23T15:15:10",
                    "EventEnd": "2024-05-23T15:25:10",
                    "Duration": 10,
                },
            ],
            False,
            0,
        ),
        (
            "Inconsistent entries, assume maintenance for safety",
            [
                {
                    "Event": "OpenSAFELY",
                    "BuildStart": "2024-05-23T14:25:10",
                    "EventStart": "2024-05-23T14:25:10",
                    "EventEnd": "2004-05-23T15:25:10",
                    "Duration": 60,
                },
                {
                    "Event": "Swap Tables",
                    "BuildStart": "2024-05-23T14:35:10",
                    "EventStart": "2024-05-23T14:35:10",
                    "EventEnd": "2024-05-23T15:15:10",
                    "Duration": 40,
                },
                {
                    "Event": "CodedEvent_SNOMED",
                    "BuildStart": "2024-05-23T15:15:10",
                    "EventStart": "2024-05-23T15:15:10",
                    "EventEnd": "2024-05-23T15:25:10",
                    "Duration": 10,
                },
                {
                    "Event": "OpenSAFELY",
                    "BuildStart": "2024-05-23T14:25:10",
                    "EventStart": "2024-05-23T14:25:10",
                    "EventEnd": "9999-12-31T00:00:00",
                    "Duration": None,
                },
                {
                    "Event": "Swap Tables",
                    "BuildStart": "2024-05-23T14:25:10",
                    "EventStart": "2024-05-23T14:25:10",
                    "EventEnd": "9999-12-31T00:00:00",
                    "Duration": None,
                },
            ],
            True,
            1,
        ),
        (
            "Swapping tables",
            [
                {
                    "Event": "OpenSAFELY",
                    "BuildStart": "2025-06-12T14:25:10",
                    "EventStart": "2025-06-12T14:25:10",
                    "EventEnd": "9999-12-31T00:00:00",
                    "Duration": None,
                },
                {
                    "Event": "Swap Tables",
                    "BuildStart": "2025-06-12T14:25:10",
                    "EventStart": "2025-06-12T14:25:10",
                    "EventEnd": "9999-12-31T00:00:00",
                    "Duration": None,
                },
            ],
            True,
            1,
        ),
        (
            "Swap Table complete but CodedEvent_SNOMED not started",
            [
                {
                    "Event": "OpenSAFELY",
                    "BuildStart": "2025-06-12T14:25:10",
                    "EventStart": "2025-06-12T14:25:10",
                    "EventEnd": "9999-12-31T00:00:00",
                    "Duration": None,
                },
                {
                    "Event": "Swap Tables",
                    "BuildStart": "2025-06-12T14:25:10",
                    "EventStart": "2025-06-12T14:25:10",
                    "EventEnd": "2025-06-12T14:30:10",
                    "Duration": None,
                },
            ],
            True,
            1,
        ),
        (
            "Building CodedEvent_SNOMED",
            [
                {
                    "Event": "OpenSAFELY",
                    "BuildStart": "2025-06-12T14:25:10",
                    "EventStart": "2025-06-12T14:25:10",
                    "EventEnd": "9999-12-31T00:00:00",
                    "Duration": None,
                },
                {
                    "Event": "Swap Tables",
                    "BuildStart": "2025-06-12T14:25:10",
                    "EventStart": "2025-06-12T14:25:10",
                    "EventEnd": "2025-06-12T15:00:00",
                    "Duration": 35,
                },
                {
                    "Event": "CodedEvent_SNOMED",
                    "BuildStart": "2025-06-12T15:00:00",
                    "EventStart": "2025-06-12T15:00:00",
                    "EventEnd": "9999-12-31T00:00:00",
                    "Duration": None,
                },
            ],
            True,
            1,
        ),
        (
            "Multiple ongoing builds",
            [
                {
                    "Event": "OpenSAFELY",
                    "BuildStart": "2025-06-12T14:25:10",
                    "EventStart": "2025-06-12T14:25:10",
                    "EventEnd": "9999-12-31T00:00:00",
                    "Duration": None,
                },
                {
                    "Event": "Swap Tables",
                    "BuildStart": "2025-06-12T14:25:10",
                    "EventStart": "2025-06-12T14:25:10",
                    "EventEnd": "9999-12-31T00:00:00",
                    "Duration": None,
                },
                {
                    "Event": "OpenSAFELY",
                    "BuildStart": "2026-02-01T14:25:10",
                    "EventStart": "2026-02-01T14:25:10",
                    "EventEnd": "9999-12-31T00:00:00",
                    "Duration": None,
                },
            ],
            True,
            2,
        ),
    ],
)
def test_in_maintenance_mode(
    mssql_database,
    description,
    events,
    is_in_maintenance_mode,
    expected_build_count,
):
    db_events = [BuildProgress(**event) for event in events]
    mssql_database.setup(*db_events)

    query_engine = TPPBackend().get_query_engine(dsn=mssql_database.host_url())
    with query_engine.engine.connect() as tpp_connection:
        verify_build_progress_count(tpp_connection, events)
        mode, build_count = maintenance_mode.get_mode_and_build_count(
            tpp_connection, environ={}
        )
    assert mode is is_in_maintenance_mode, description
    assert build_count == expected_build_count


@pytest.mark.parametrize(
    "events,expected",
    [
        (
            [
                {
                    "Event": "OpenSAFELY",
                    "BuildStart": "2004-05-23T14:25:10",
                    "EventStart": "2004-05-23T14:25:10",
                    "EventEnd": "2004-05-23T15:25:10",
                    "Duration": 60,
                }
            ],
            "none;0",
        ),
        (
            [
                {
                    "Event": "OpenSAFELY",
                    "BuildStart": "2025-06-12T14:25:10",
                    "EventStart": "2025-06-12T14:25:10",
                    "EventEnd": "9999-12-31T00:00:00",
                    "Duration": None,
                },
                {
                    "Event": "Swap Tables",
                    "BuildStart": "2025-06-12T14:25:10",
                    "EventStart": "2025-06-12T14:25:10",
                    "EventEnd": "9999-12-31T00:00:00",
                    "Duration": None,
                },
            ],
            "db-maintenance;1",
        ),
    ],
)
def test_in_maintenance_mode_task_run_output(mssql_database, capsys, events, expected):
    db_events = [BuildProgress(**event) for event in events]
    mssql_database.setup(*db_events)

    query_engine = TPPBackend().get_query_engine(dsn=mssql_database.host_url())
    with query_engine.engine.connect() as tpp_connection:
        verify_build_progress_count(tpp_connection, events)

    maintenance_mode.run(
        backend_class=TPPBackend,
        dsn=mssql_database.host_url(),
        environ={},
        user_args=[],
    )
    assert capsys.readouterr().out.strip() == expected


@pytest.mark.parametrize(
    "table_available,is_in_maintenance_mode", [(True, False), (False, True)]
)
def test_in_maintenance_mode_checks_coded_event_snomed_availability(
    mssql_database,
    table_available,
    is_in_maintenance_mode,
):
    # Main build has started, SwapTables and CodedEvent_SNOMED events have not started yet
    # We are not in maintenance mode according to the BuildProgress table, but the final
    # check to ensure availability of the CodedEvent_SNOMED table can override this
    events = [
        BuildProgress(
            Event="OpenSAFELY",
            BuildStart="2025-06-12T14:25:10",
            EventStart="2025-06-12T14:25:10",
            EventEnd="9999-12-31T00:00:00",
            Duration=None,
        )
    ]
    mssql_database.setup(*events)

    query_engine = TPPBackend().get_query_engine(dsn=mssql_database.host_url())
    with query_engine.engine.connect() as tpp_connection:
        verify_build_progress_count(tpp_connection, events)
        if not table_available:
            tpp_connection.execute(
                sqlalchemy.text(
                    """
                    DROP TABLE CodedEvent_SNOMED
                    """
                )
            )

        mode, _ = maintenance_mode.get_mode_and_build_count(tpp_connection, environ={})
        assert mode == is_in_maintenance_mode


def test_in_maintenance_mode_custom_event(mssql_database):
    events = [
        BuildProgress(
            Event="OpenSAFELY",
            BuildStart="2025-06-12T14:25:10",
            EventStart="2025-06-12T14:25:10",
            EventEnd="9999-12-31T00:00:00",
            Duration=None,
        ),
        BuildProgress(
            Event="Custom event",
            BuildStart="2025-06-12T14:25:10",
            EventStart="2025-06-12T14:25:10",
            EventEnd="9999-12-31T00:00:00",
            Duration=None,
        ),
    ]

    mssql_database.setup(*events)

    query_engine = TPPBackend().get_query_engine(dsn=mssql_database.host_url())
    with query_engine.engine.connect() as tpp_connection:
        verify_build_progress_count(tpp_connection, events)
        mode, _ = maintenance_mode.get_mode_and_build_count(
            tpp_connection,
            environ={"TPP_MAINTENANCE_START_EVENT": "Custom event,Other"},
        )
        assert mode


def verify_build_progress_count(tpp_connection, events):
    result = tpp_connection.execute(sqlalchemy.text("select * from BuildProgress"))
    assert len(list(result)) == len(events)
