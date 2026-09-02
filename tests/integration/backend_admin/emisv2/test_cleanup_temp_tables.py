import datetime
import logging

import pytest
import sqlalchemy

from ehrql.backend_admin.emisv2 import cleanup_temp_tables
from ehrql.backends.emisv2 import EMISV2Backend


@pytest.fixture
def test_tables(trino_database):
    query_engine = EMISV2Backend().get_query_engine(trino_database.host_url())

    now = datetime.datetime.now(datetime.UTC)
    old = now - datetime.timedelta(days=30)
    other_schema = "other_schema"
    table_names = {
        query_engine.temp_table_schema: {
            "old": f"ehrql_{old:%Y%m%d_%H%M}_a1b2c3d4e5f6_tmp_1",
            "recent": f"ehrql_{now:%Y%m%d_%H%M}_a1b2c3d4e5f6_tmp_2",
            # Same prefix but no timestamp, doesn't match the strict pattern
            "unrelated_ehrql": "ehrql_results_summary",
            # Contains the timestamp but doesn't match the pattern
            "unrelated": f"test_user_table_{now:%Y%m%d_%H%M%S}",
        },
        other_schema: {
            # Matches the pattern and is old, but lives in `other_schema` rather
            # than the temp-table schema. Cleanup must leave it alone.
            "other_schema_old": f"ehrql_{old:%Y%m%d_%H%M}_deadbeefcafe_tmp_99"
        },
    }

    with query_engine.engine.connect() as connection:
        connection.execute(
            sqlalchemy.text(f'CREATE SCHEMA IF NOT EXISTS "{other_schema}"')
        )
        for schema, tables in table_names.items():
            for name in tables.values():
                connection.execute(
                    sqlalchemy.text(f'CREATE TABLE "{schema}"."{name}" (x INTEGER)')
                )

    yield query_engine, table_names, other_schema

    with query_engine.engine.connect() as connection:
        for schema, tables in table_names.items():
            for name in tables.values():
                connection.execute(
                    sqlalchemy.text(f'DROP TABLE IF EXISTS "{schema}"."{name}"')
                )
        connection.execute(sqlalchemy.text(f'DROP SCHEMA IF EXISTS "{other_schema}"'))


def _existing_test_tables(connection, schema, table_names):
    placeholders = ", ".join(f":n{i}" for i in range(len(table_names)))
    params = {f"n{i}": name for i, name in enumerate(table_names)}
    result = connection.execute(
        sqlalchemy.text(
            "SELECT table_name FROM information_schema.tables "
            f"WHERE table_schema = :schema AND table_name IN ({placeholders})"
        ),
        {"schema": schema, **params},
    )
    return {row[0] for row in result}


def test_cleanup_temp_tables_drops_old_only(test_tables, capsys):
    query_engine, table_names, other_schema = test_tables
    temp_tables = table_names[query_engine.temp_table_schema]
    temp_table_names = list(temp_tables.values())
    other_table_names = list(table_names[other_schema].values())

    cleanup_temp_tables.run(
        backend_class=EMISV2Backend,
        dsn=query_engine.dsn,
        max_age_days=14,
        dry_run=False,
        environ={},
        user_args=[],
    )

    assert capsys.readouterr().out.strip() == "true"

    with query_engine.engine.connect() as connection:
        temp_tables_remaining = _existing_test_tables(
            connection, query_engine.temp_table_schema, temp_table_names
        )
        other_remaining = _existing_test_tables(
            connection, other_schema, other_table_names
        )

    assert temp_tables["old"] not in temp_tables_remaining
    assert temp_tables["recent"] in temp_tables_remaining
    assert temp_tables["unrelated_ehrql"] in temp_tables_remaining
    assert temp_tables["unrelated"] in temp_tables_remaining
    # The matching-pattern table in the non-temp schema must be untouched.
    assert other_remaining == set(other_table_names)


def test_cleanup_temp_tables_nothing_to_drop(test_tables, caplog, capsys):
    query_engine, table_names, other_schema = test_tables
    temp_table_names = list(table_names[query_engine.temp_table_schema].values())
    other_table_names = list(table_names[other_schema].values())

    # call cleanup_temp_tables with a longer max_age_days so none of our
    # test tables are old enough ("old" tables are timestamped 30 days ago)
    with caplog.at_level(
        logging.INFO, logger="ehrql.backend_admin.emisv2.cleanup_temp_tables"
    ):
        cleanup_temp_tables.run(
            backend_class=EMISV2Backend,
            dsn=query_engine.dsn,
            max_age_days=31,
            dry_run=False,
            environ={},
            user_args=[],
        )

    assert any(
        "No ehrQL temporary tables older than 31 days" in record.message
        for record in caplog.records
    )

    assert capsys.readouterr().out.strip() == "false"

    with query_engine.engine.connect() as connection:
        remaining = _existing_test_tables(
            connection, query_engine.temp_table_schema, temp_table_names
        )
        other_remaining = _existing_test_tables(
            connection, other_schema, other_table_names
        )

    assert remaining == set(temp_table_names)
    assert other_remaining == set(other_table_names)


def test_cleanup_temp_tables_dry_run_drops_nothing(test_tables, caplog, capsys):
    query_engine, table_names, other_schema = test_tables
    temp_tables = table_names[query_engine.temp_table_schema]
    temp_table_names = list(temp_tables.values())
    other_table_names = list(table_names[other_schema].values())

    with caplog.at_level(
        logging.INFO, logger="ehrql.backend_admin.emisv2.cleanup_temp_tables"
    ):
        cleanup_temp_tables.run(
            backend_class=EMISV2Backend,
            dsn=query_engine.dsn,
            max_age_days=14,
            dry_run=True,
            environ={},
            user_args=[],
        )

    assert capsys.readouterr().out.strip() == "false"

    with query_engine.engine.connect() as connection:
        remaining = _existing_test_tables(
            connection, query_engine.temp_table_schema, temp_table_names
        )
        other_remaining = _existing_test_tables(
            connection, other_schema, other_table_names
        )

    # All tables, including the old one, should still be present.
    assert remaining == set(temp_table_names)
    assert other_remaining == set(other_table_names)
    # The would-be drop is logged.
    assert any(
        "Would drop" in record.message and temp_tables["old"] in record.message
        for record in caplog.records
    )
