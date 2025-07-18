import json
import sys
from pathlib import Path

import pytest

from ehrql.exceptions import ParameterError
from ehrql.user_parameters import get_parameter


@pytest.fixture(autouse=True)
def reset_sys_argv():
    original_argv = sys.argv
    yield
    sys.argv = original_argv


def test_get_parameters():
    sys.argv = ["dataset_definition.py", "--foo", "1", "--bar", "2"]
    assert get_parameter("foo") == "1"
    assert get_parameter("bar", type=int) == 2
    assert get_parameter("foobar", default="foo") == "foo"


def test_get_parameters_multiple_values():
    sys.argv = ["dataset_definition.py", "--foo", "1", "3", "--bar", "2"]
    assert get_parameter("foo", type=int) == [1, 3]


def test_get_parameters_with_no_default():
    sys.argv = [
        "dataset_definition.py",
    ]
    with pytest.raises(
        ParameterError,
        match="dataset_definition.py error: parameter `foo` defined but no values found",
    ):
        get_parameter("foo", type=int)


def test_get_parameters_with_list_default():
    sys.argv = [
        "dataset_definition.py",
    ]
    assert get_parameter("foo", type=int, default=[1]) == [1]


@pytest.mark.parametrize(
    "value,arg_type,expected",
    [
        ("1", int, 1),
        ("1", float, 1.0),
        ("foo", Path, Path("foo")),
        ('{"foo": 1}', json.loads, {"foo": 1}),
        ("1", lambda x: int(x) + 1, 2),
    ],
)
def test_get_parameters_types(value, arg_type, expected):
    # test that we can pass any arbitrary callable that takes a single
    # string
    # https://docs.python.org/3.10/library/argparse.html#type
    sys.argv = [
        "dataset_definition.py",
        "--foo",
        value,
    ]
    assert get_parameter("foo", type=arg_type) == expected


def test_get_dataset_parameters_invalid_type():
    # test that we can pass any arbitrary callable that takes a single
    # string
    # https://docs.python.org/3.10/library/argparse.html#type
    sys.argv = [
        "test_dataset_definition.py",
        "--foo",
        "1",
    ]

    with pytest.raises(ParameterError, match="<class 'list'> is not a valid type\n\n"):
        assert get_parameter("foo", type=list)


@pytest.mark.parametrize(
    "falsey_string, truthy_string",
    [
        ("0", "1"),
        ("false", "true"),
        ("False", "True"),
    ],
)
def test_get_bool_parameter(falsey_string, truthy_string):
    sys.argv = [
        "dataset_definition.py",
        "--f_param",
        falsey_string,
        "--t_param",
        truthy_string,
    ]
    assert get_parameter("f_param", type=bool) is False
    assert get_parameter("t_param", type=bool) is True


def test_get_bad_bool_parameter():
    sys.argv = ["dataset_definition.py", "--foo", "trueish"]
    with pytest.raises(
        ParameterError, match="'trueish' is an invalid value for `bool` type parameter"
    ):
        get_parameter("foo", type=bool)
