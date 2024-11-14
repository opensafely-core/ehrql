import textwrap

from ehrql.debug import show


def test_show_string(capsys):
    expected_output = textwrap.dedent(
        """
        Debug line 14:
        'Hello'
        """
    ).strip()

    show("Hello")
    captured = capsys.readouterr()
    assert captured.err.strip() == expected_output, captured.err


def test_show_int_variable(capsys):
    expected_output = textwrap.dedent(
        """
        Debug line 28:
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
        Debug line 41: Number
        14
        """
    ).strip()

    show(14, label="Number")
    captured = capsys.readouterr()
    assert captured.err.strip() == expected_output, captured.err
