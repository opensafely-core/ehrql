import re

import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column

from ehrql.query_engines.mssql_dialect import SelectStarInto
from ehrql.utils.mssql_log_utils import execute_with_log


class Base(DeclarativeBase): ...


class TableA(Base):
    __tablename__ = "table_a"
    pk = mapped_column(sqlalchemy.Integer, primary_key=True)


class TableB(Base):
    __tablename__ = "table_b"
    pk = mapped_column(sqlalchemy.Integer, primary_key=True)


def test_execute_with_log(mssql_database):
    log_lines = []

    # Simulate approximately how structlog will format our logs
    def log(event, **kwargs):
        attrs = " ".join(f"{k}={v}" for k, v in kwargs.items())
        log_lines.append(
            f"2023-01-01 10:00:00 [info     ] {event}{' ' if attrs else ''}{attrs}"
        )

    mssql_database.setup(
        TableA(pk=1),
        TableA(pk=6),
        TableB(pk=3),
        TableB(pk=8),
    )

    select_a = sqlalchemy.select(TableA.pk).where(TableA.pk < 5)
    select_b = sqlalchemy.select(TableB.pk).where(TableB.pk < 5)
    select_all = select_a.union_all(select_b)

    # `execute_with_log` can't return results so to check it's done the right thing we
    # need to write the results to a temporary table and read them from there
    tmp_table = sqlalchemy.Table(
        "#tmp_table", sqlalchemy.MetaData(), sqlalchemy.Column("pk", sqlalchemy.Integer)
    )
    query = SelectStarInto(tmp_table, select_all.alias())

    with mssql_database.engine().connect() as connection:
        # Execute a query that does no IO to check we handle that correctly
        execute_with_log(connection, sqlalchemy.text("SELECT 1"), log)
        # Execute the main query
        execute_with_log(connection, query, log, query_id="test_query")
        # Retrive results from temporary table
        response = connection.execute(sqlalchemy.select(tmp_table.c.pk))
        results = list(response)

    assert results == [(1,), (3,)]

    assert log_lines[0] == (
        "2023-01-01 10:00:00 [info     ] SQL:\n"
        "                                SELECT 1"
    )

    assert log_lines[1] == (
        "2023-01-01 10:00:00 [info     ] 0 seconds: exec_cpu_ms=0 exec_elapsed_ms=0 exec_cpu_ratio=0.0 parse_cpu_ms=0 parse_elapsed_ms=0\n"
        "\n"
    )

    assert log_lines[2] == (
        "2023-01-01 10:00:00 [info     ] SQL:\n"
        "                                SELECT * INTO [#tmp_table] FROM (SELECT table_a.pk AS pk \n"
        "                                FROM table_a \n"
        "                                WHERE table_a.pk < %(pk_1)s UNION ALL SELECT table_b.pk AS pk \n"
        "                                FROM table_b \n"
        "                                WHERE table_b.pk < %(pk_2)s) AS anon_1"
    )

    assert log_lines[3] == (
        "2023-01-01 10:00:00 [info     ] scans logical physical read_ahead lob_logical lob_physical lob_read_ahead table\n"
        "                                1     2       0        0          0           0            0              table_b\n"
        "                                1     2       0        0          0           0            0              table_a"
    )

    assert re.search(
        r"\d+ seconds: exec_cpu_ms=\d+ exec_elapsed_ms=\d+ exec_cpu_ratio=[\d\.]+ parse_cpu_ms=\d+ parse_elapsed_ms=\d+ query_id=test_query",
        log_lines[4],
    )
