import json
import textwrap
from datetime import date

import pytest

from ehrql import create_dataset, show
from ehrql.debugger import (
    activate_debug_context,
    elements_are_related_series,
    related_patient_columns_to_records,
    render,
)
from ehrql.query_engines.in_memory_database import PatientColumn
from ehrql.tables import EventFrame, PatientFrame, Series, table


def date_serializer(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError("Type not serializable")  # pragma: no cover


def test_show(capsys):
    expected_output = textwrap.dedent(
        """
        Show line 27:
        'Hello'
        """
    ).strip()

    show("Hello")
    captured = capsys.readouterr()
    assert captured.err.strip() == expected_output, captured.err


def test_show_with_label(capsys):
    expected_output = textwrap.dedent(
        """
        Show line 40: Number
        14
        """
    ).strip()

    show(14, label="Number")
    captured = capsys.readouterr()
    assert captured.err.strip() == expected_output, captured.err


def test_render_string():
    assert render("Hello") == "'Hello'"


def test_render_int_variable():
    assert render(12) == "12"


def test_render_multiple_variables():
    expected_output = textwrap.dedent(
        """
        12
        'Hello'
        """
    ).strip()

    assert render(12, "Hello") == expected_output


def test_related_patient_columns_to_records_full_join():
    c1 = PatientColumn.parse(
        """
        1 | 101
        2 | 102
        4 | 104
        """
    )
    c2 = PatientColumn.parse(
        """
        1 | 201
        2 | 202
        3 | 203
        """
    )
    r = list(related_patient_columns_to_records([c1, c2]))
    r_expected = [
        {"patient_id": 1, "series_1": 101, "series_2": 201},
        {"patient_id": 2, "series_1": 102, "series_2": 202},
        {"patient_id": 3, "series_1": "", "series_2": 203},
        {"patient_id": 4, "series_1": 104, "series_2": ""},
    ]
    assert r == r_expected


def test_render_formatted_table():
    expected_output = textwrap.dedent(
        """
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
    assert render(c).strip() == expected_output


def test_render_truncated_table():
    expected_output = textwrap.dedent(
        """
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

    assert render(c, head=1, tail=1) == expected_output


@table
class patients(PatientFrame):
    date_of_birth = Series(date)
    date_of_death = Series(date)
    sex = Series(str)


@table
class events(EventFrame):
    date = Series(date)
    code = Series(str)
    test_result = Series(int)


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
            patient_id,date_of_birth,date_of_death,sex
            1,1970-01-01,,male
            2,1980-01-01,2020-01-01,female
            """
        )
    )
    tmp_path.joinpath("events.csv").write_text(
        textwrap.dedent(
            """\
            patient_id,date,code,test_result
            1,2010-01-01,abc,32
            1,2020-01-01,def,
            2,2005-01-01,abc,40
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
                {
                    "patient_id": 1,
                    "date_of_birth": date(1970, 1, 1),
                    "date_of_death": "",
                    "sex": "male",
                },
                {
                    "patient_id": 2,
                    "date_of_birth": date(1980, 1, 1),
                    "date_of_death": date(2020, 1, 1),
                    "sex": "female",
                },
            ],
        ),
        (
            patients.date_of_birth,
            [
                {"patient_id": 1, "value": date(1970, 1, 1)},
                {"patient_id": 2, "value": date(1980, 1, 1)},
            ],
        ),
        (
            init_dataset(
                dob=patients.date_of_birth,
                count=events.count_for_patient(),
                dod=patients.date_of_death,
            ),
            [
                {"patient_id": 1, "dob": date(1970, 1, 1), "count": 2, "dod": ""},
                {
                    "patient_id": 2,
                    "dob": date(1980, 1, 1),
                    "count": 1,
                    "dod": date(2020, 1, 1),
                },
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


@pytest.mark.parametrize(
    "elements,expected",
    [
        ((patients.date_of_birth, patients.sex), True),
        ((events.date, events.code), True),
        ((patients.date_of_birth, events.count_for_patient()), True),
        ((patients, patients.date_of_birth), False),
        ((patients.date_of_birth, events.date), False),
        ((patients.date_of_birth, {"some": "dict"}, patients.sex), False),
    ],
)
def test_elements_are_related_series(elements, expected):
    assert elements_are_related_series(elements) == expected


def test_repr_related_patient_series(dummy_tables_path):
    with activate_debug_context(
        dummy_tables_path=dummy_tables_path,
        render_function=lambda value: json.dumps(
            list(value), indent=4, default=date_serializer
        ),
    ):
        rendered = render(
            patients.date_of_birth,
            patients.sex,
            events.count_for_patient(),
            patients.date_of_death,
        )
    assert json.loads(rendered) == [
        {
            "patient_id": 1,
            "series_1": "1970-01-01",
            "series_2": "male",
            "series_3": 2,
            "series_4": "",
        },
        {
            "patient_id": 2,
            "series_1": "1980-01-01",
            "series_2": "female",
            "series_3": 1,
            "series_4": "2020-01-01",
        },
    ]


def test_repr_related_event_series(dummy_tables_path):
    with activate_debug_context(
        dummy_tables_path=dummy_tables_path,
        render_function=lambda value: json.dumps(
            list(value), indent=4, default=date_serializer
        ),
    ):
        rendered = render(events.date, events.code, events.test_result)
    assert json.loads(rendered) == [
        {
            "patient_id": 1,
            "row_id": 1,
            "series_1": "2010-01-01",
            "series_2": "abc",
            "series_3": 32,
        },
        {
            "patient_id": 1,
            "row_id": 2,
            "series_1": "2020-01-01",
            "series_2": "def",
            "series_3": "",
        },
        {
            "patient_id": 2,
            "row_id": 3,
            "series_1": "2005-01-01",
            "series_2": "abc",
            "series_3": 40,
        },
    ]


def test_repr_date_difference(dummy_tables_path):
    with activate_debug_context(
        dummy_tables_path=dummy_tables_path,
        render_function=lambda value: json.dumps(list(value), indent=4),
    ):
        rendered = render(patients.date_of_death - events.date)
    assert json.loads(rendered) == [
        {"patient_id": 1, "row_id": 1, "value": ""},
        {"patient_id": 1, "row_id": 2, "value": ""},
        {"patient_id": 2, "row_id": 3, "value": "5478 days"},
    ]


def test_repr_related_date_difference_patient_series(dummy_tables_path):
    with activate_debug_context(
        dummy_tables_path=dummy_tables_path,
        render_function=lambda value: json.dumps(list(value), indent=4),
    ):
        rendered = render(
            "2024-01-01" - patients.date_of_birth,
            patients.sex,
        )
    assert json.loads(rendered) == [
        {"patient_id": 1, "series_1": "19723 days", "series_2": "male"},
        {"patient_id": 2, "series_1": "16071 days", "series_2": "female"},
    ]


def test_repr_related_date_difference_event_series(dummy_tables_path):
    with activate_debug_context(
        dummy_tables_path=dummy_tables_path,
        render_function=lambda value: json.dumps(list(value), indent=4),
    ):
        rendered = render(
            events.date - patients.date_of_birth,
            events.code,
        )
    assert json.loads(rendered) == [
        {"patient_id": 1, "row_id": 1, "series_1": "14610 days", "series_2": "abc"},
        {"patient_id": 1, "row_id": 2, "series_1": "18262 days", "series_2": "def"},
        {"patient_id": 2, "row_id": 3, "series_1": "9132 days", "series_2": "abc"},
    ]
