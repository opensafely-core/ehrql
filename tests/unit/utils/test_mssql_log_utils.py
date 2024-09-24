from ehrql.utils.mssql_log_utils import (
    append_str_to_last_value,
    format_table_io,
    indent,
    parse_statistics_messages,
)


def test_parse_statistics_messages():
    messages = [
        b"This message will not be parseable and should be ignored",
        (
            b"SQL Server parse and compile time: \n"
            b"   CPU time = 10 ms, elapsed time = 5 ms."
        ),
        (
            b"\n SQL Server Execution Times:\n"
            b"   CPU time = 100 ms,  elapsed time = 200 ms."
        ),
        (
            b"SQL Server parse and compile time: \n"
            b"   CPU time = 50 ms, elapsed time = 16 ms."
        ),
        (
            b"\n SQL Server Execution Times:\n"
            b"   CPU time = 123 ms,  elapsed time = 456 ms."
        ),
        (
            b"Table 'Workfile'. Scan count 1, logical reads 2, physical reads 3,"
            b" read-ahead reads 4, lob logical reads 5, lob physical reads 6,"
            b" lob read-ahead reads 7."
        ),
        (
            b"Table 'Worktable'. Scan count 0, logical reads 0, physical reads 0,"
            b" read-ahead reads 0, lob logical reads 0, lob physical reads 0,"
            b" lob read-ahead reads 0."
        ),
        (
            b"Table '#inline_data_1______________________________________________________________________________________________________00000000149B'."
            b" Scan count 1, logical reads 7, physical reads 0, read-ahead reads 0,"
            b" lob logical reads 0, lob physical reads 0, lob read-ahead reads 0."
        ),
        # Newer version of SQL Server return IO stats in a different order and with
        # additional items, so check we handle those correctly
        (
            b"Table '#tmp_1______________________________________________________________________________________________________________0000000014D9'."
            b" Scan count 1, logical reads 4, physical reads 0, page server reads 0,"
            b" read-ahead reads 0, page server read-ahead reads 0, lob logical reads 0,"
            b" lob physical reads 0, lob page server reads 0, lob read-ahead reads 0,"
            b" lob page server read-ahead reads 0."
        ),
        (
            b"Table '#tmp_1______________________________________________________________________________________________________________0000000014B1'."
            b" Scan count 1, logical reads 0, physical reads 0, read-ahead reads 0,"
            b" lob logical reads 0, lob physical reads 0, lob read-ahead reads 0."
        ),
        (
            b"Table '#tmp_1______________________________________________________________________________________________________________000000001517'."
            b" Scan count 1, logical reads 0, physical reads 0, read-ahead reads 0, "
            b"lob logical reads 0, lob physical reads 0, lob read-ahead reads 0."
        ),
    ]

    timings, table_io = parse_statistics_messages(messages)

    assert timings == {
        "exec_cpu_ms": 223,
        "exec_elapsed_ms": 656,
        "exec_cpu_ratio": 0.34,
        "parse_cpu_ms": 60,
        "parse_elapsed_ms": 21,
    }
    assert table_io == {
        "Workfile": {
            "lob_logical": 5,
            "lob_physical": 6,
            "lob_read_ahead": 7,
            "logical": 2,
            "physical": 3,
            "read_ahead": 4,
            "scans": 1,
        },
        "Worktable": {
            "lob_logical": 0,
            "lob_physical": 0,
            "lob_read_ahead": 0,
            "logical": 0,
            "physical": 0,
            "read_ahead": 0,
            "scans": 0,
        },
        "#inline_data_1": {
            "lob_logical": 0,
            "lob_physical": 0,
            "lob_read_ahead": 0,
            "logical": 7,
            "physical": 0,
            "read_ahead": 0,
            "scans": 1,
        },
        "#tmp_1": {
            "lob_logical": 0,
            "lob_physical": 0,
            "lob_read_ahead": 0,
            "logical": 4,
            "physical": 0,
            "read_ahead": 0,
            "scans": 3,
        },
    }


def test_format_table_io():
    table_io = {
        "Workfile": {
            "lob_logical": 5,
            "lob_physical": 6,
            "lob_read_ahead": 7,
            "logical": 2,
            "physical": 3,
            "read_ahead": 4,
            "scans": 1,
        },
        "Worktable": {
            # Check we correctly handle the case when the figure is wider than the
            # header (which does actually happen in production!)
            "lob_logical": 100_000_000_000,
            "lob_physical": 0,
            "lob_read_ahead": 0,
            "logical": 0,
            "physical": 0,
            "read_ahead": 0,
            "scans": 0,
        },
    }
    output = format_table_io(table_io)
    assert output == (
        "lob_logical  lob_physical lob_read_ahead logical physical read_ahead scans table\n"
        "5            6            7              2       3        4          1     Workfile\n"
        "100000000000 0            0              0       0        0          0     Worktable"
    )


def test_indent():
    lines = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing\n"
        "elit, sed do eiusmod tempor incididunt ut labore et\n"
        "dolore magna aliqua."
    )
    expected = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing\n"
        "    elit, sed do eiusmod tempor incididunt ut labore et\n"
        "    dolore magna aliqua."
    )

    assert indent(lines, prefix="    ") == expected


def test_append_str_to_last_value():
    d = {"a": "foo", "b": "bar", "c": 123}
    append_str_to_last_value(d, "\n")
    assert d == {"a": "foo", "b": "bar", "c": "123\n"}
