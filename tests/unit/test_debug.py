import textwrap

from ehrql import debug
from ehrql.debugger import stop
from ehrql.query_engines.in_memory_database import PatientColumn


def test_show_string(capsys):
    expected_output = textwrap.dedent(
        """
        Debug line 16:
        'Hello'
        """
    ).strip()

    debug("Hello")
    captured = capsys.readouterr()
    assert captured.err.strip() == expected_output, captured.err


def test_show_int_variable(capsys):
    expected_output = textwrap.dedent(
        """
        Debug line 30:
        12
        """
    ).strip()

    foo = 12
    debug(foo)
    captured = capsys.readouterr()
    assert captured.err.strip() == expected_output, captured.err


def test_show_multiple_variables(capsys):
    expected_output = textwrap.dedent(
        """
        Debug line 46:
        12
        'Hello'
        """
    ).strip()

    foo = 12
    bar = "Hello"
    debug(foo, bar)
    captured = capsys.readouterr()
    assert captured.err.strip() == expected_output, captured.err


def test_show_with_label(capsys):
    expected_output = textwrap.dedent(
        """
        Debug line 59: Number
        14
        """
    ).strip()

    debug(14, label="Number")
    captured = capsys.readouterr()
    assert captured.err.strip() == expected_output, captured.err


def test_show_formatted_table(capsys):
    expected_output = textwrap.dedent(
        """
        Debug line 81:
        patient_id        | value
        ------------------+------------------
        1                 | 101
        2                 | 201
        """
    ).strip()

    c = PatientColumn.parse(
        """
        1 | 101
        2 | 201
        """
    )
    debug(c)
    captured = capsys.readouterr()
    assert captured.err.strip() == expected_output, captured.err


def test_show_truncated_table(capsys):
    expected_output = textwrap.dedent(
        """
        Debug line 107:
        patient_id        | value
        ------------------+------------------
        1                 | 101
        ...               | ...
        4                 | 401
        """
    ).strip()

    c = PatientColumn.parse(
        """
        1 | 101
        2 | 201
        3 | 301
        4 | 401
        """
    )

    debug(c, head=1, tail=1)
    captured = capsys.readouterr()
    assert captured.err.strip() == expected_output, captured.err


def test_stop(capsys):
    stop()
    captured = capsys.readouterr()
    assert captured.err.strip() == "Stopping at line 113"


def test_stop_with_head_and_tail(capsys):
    stop(head=1, tail=1)
    captured = capsys.readouterr()
    assert captured.err.strip() == "Stopping at line 119"
