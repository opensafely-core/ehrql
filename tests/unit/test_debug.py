import textwrap

from ehrql.debug import show
from ehrql.query_engines.in_memory_database import PatientColumn


def test_show_string(capsys):
    expected_output = textwrap.dedent(
        """
        Debug line 15:
        'Hello'
        """
    ).strip()

    show("Hello")
    captured = capsys.readouterr()
    assert captured.err.strip() == expected_output, captured.err


def test_show_int_variable(capsys):
    expected_output = textwrap.dedent(
        """
        Debug line 29:
        12
        """
    ).strip()

    foo = 12
    show(foo)
    captured = capsys.readouterr()
    assert captured.err.strip() == expected_output, captured.err


def test_show_with_label(capsys):
    expected_output = textwrap.dedent(
        """
        Debug line 42: Number
        14
        """
    ).strip()

    show(14, label="Number")
    captured = capsys.readouterr()
    assert captured.err.strip() == expected_output, captured.err


def test_show_formatted_table(capsys):
    expected_output = textwrap.dedent(
        """
        Debug line 64:
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
    show(c)
    captured = capsys.readouterr()
    assert captured.err.strip() == expected_output, captured.err
