import textwrap

import pytest

from ehrql import create_dataset, debug
from ehrql.debugger import activate_debug_context, stop
from ehrql.query_engines.in_memory_database import PatientColumn
from ehrql.tables import EventFrame, PatientFrame, Series, table


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


@table
class patients(PatientFrame):
    date_of_birth = Series(str)
    sex = Series(str)


@table
class events(EventFrame):
    date = Series(str)
    code = Series(str)


def init_dataset(**kwargs):
    dataset = create_dataset()
    for key, value in kwargs.items():
        setattr(dataset, key, value)
    return dataset


@pytest.fixture(scope="session")
def dummy_tables_path(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("dummy_tables")
    tmp_path.joinpath("patients.csv").write_text(
        textwrap.dedent(
            """\
            patient_id,date_of_birth,sex
            1,1970-01-01,male
            2,1980-01-01,female
            """
        )
    )
    tmp_path.joinpath("events.csv").write_text(
        textwrap.dedent(
            """\
            patient_id,date,code
            1,2010-01-01,abc
            1,2020-01-01,def
            2,2005-01-01,abc
            """
        )
    )
    return tmp_path


@pytest.mark.parametrize(
    "expression,contents",
    [
        (
            patients,
            [
                {"patient_id": 1, "date_of_birth": "1970-01-01", "sex": "male"},
                {"patient_id": 2, "date_of_birth": "1980-01-01", "sex": "female"},
            ],
        ),
        (
            patients.date_of_birth,
            [
                {"patient_id": 1, "value": "1970-01-01"},
                {"patient_id": 2, "value": "1980-01-01"},
            ],
        ),
        (
            init_dataset(dob=patients.date_of_birth, count=events.count_for_patient()),
            [
                {"patient_id": 1, "dob": "1970-01-01", "count": 2},
                {"patient_id": 2, "dob": "1980-01-01", "count": 1},
            ],
        ),
    ],
)
def test_activate_debug_context(dummy_tables_path, expression, contents):
    with activate_debug_context(
        dummy_tables_path=dummy_tables_path,
        render_function=lambda value: repr(list(value)),
    ):
        assert repr(expression) == repr(contents)
