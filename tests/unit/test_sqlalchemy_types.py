import datetime

import pytest

from databuilder import sqlalchemy_types as types
from databuilder.codes import CTV3Code
from databuilder.sqlalchemy_types import type_from_python_type


@pytest.mark.parametrize(
    "type_,expected",
    [
        (bool, types.Boolean),
        (datetime.date, types.Date),
        (float, types.Float),
        (int, types.Integer),
        (str, types.Text),
        (CTV3Code, types.Text),
    ],
)
def test_type_from_python_type(type_, expected):
    assert type_from_python_type(type_) == expected


class UnknownType:
    ...


def test_type_from_python_type_raises_error_on_unknown_type():
    with pytest.raises(TypeError):
        type_from_python_type(UnknownType)


class TypeWithMethod:
    @classmethod
    def _primitive_type(cls):
        return int


def test_type_from_python_type_respects_primitive_type_method():
    assert type_from_python_type(TypeWithMethod) == types.Integer
