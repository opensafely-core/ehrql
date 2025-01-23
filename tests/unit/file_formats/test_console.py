import datetime
import textwrap

from ehrql.file_formats.console import write_rows_console, write_tables_console
from ehrql.query_model.column_specs import ColumnSpec
from ehrql.sqlalchemy_types import TYPE_MAP


def test_write_rows_console(capsys):
    column_specs = {
        "patient_id": ColumnSpec(int),
        "b": ColumnSpec(bool),
        "i": ColumnSpec(int),
        "f": ColumnSpec(float),
        "s": ColumnSpec(str),
        "c": ColumnSpec(str, categories=("A", "B")),
        "d": ColumnSpec(datetime.date),
    }

    rows = [
        (123, True, 1, 2.3, "a", "A", datetime.date(2020, 1, 1)),
        (456, False, -5, -0.4, "b", "B", datetime.date(2022, 12, 31)),
        (789, None, None, None, None, None, None),
    ]

    # Check the example uses at least one of every supported type
    assert {spec.type for spec in column_specs.values()} == set(TYPE_MAP)

    write_rows_console(rows, column_specs)
    output = capsys.readouterr().out

    # The CSV module does its own newline handling, hence the carriage returns below
    assert output == textwrap.dedent(
        """\
        patient_id,b,i,f,s,c,d\r
        123,T,1,2.3,a,A,2020-01-01\r
        456,F,-5,-0.4,b,B,2022-12-31\r
        789,,,,,,\r
        """
    )


def test_write_tables_console(capsys):
    table_specs = {
        "table_1": {
            "patient_id": ColumnSpec(int),
            "b": ColumnSpec(bool),
            "i": ColumnSpec(int),
        },
        "table_2": {
            "patient_id": ColumnSpec(int),
            "s": ColumnSpec(str),
            "d": ColumnSpec(datetime.date),
        },
    }

    tables = [
        [
            (123, True, 1),
            (456, False, 2),
        ],
        [
            (789, "a", datetime.date(2025, 1, 1)),
            (987, "B", datetime.date(2025, 2, 3)),
        ],
    ]

    write_tables_console(tables, table_specs)
    output = capsys.readouterr().out

    # The CSV module does its own newline handling, hence the carriage returns below
    assert output == textwrap.dedent(
        """\
        table_1
        patient_id,b,i\r
        123,T,1\r
        456,F,2\r


        table_2
        patient_id,s,d\r
        789,a,2025-01-01\r
        987,B,2025-02-03\r
        """
    )
