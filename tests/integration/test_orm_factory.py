import datetime

import pytest
import sqlalchemy
from sqlalchemy.orm import Session, declarative_base

from databuilder.orm_factory import read_orm_models_from_csv_lines
from databuilder.sqlalchemy_types import TYPE_MAP, Integer, type_from_python_type


@pytest.mark.parametrize(
    "type_,csv_value,expected_value",
    [
        (bool, '""', None),
        (bool, "F", False),
        (bool, "T", True),
        (int, "123", 123),
        (float, "1.23", 1.23),
        (str, "foo", "foo"),
        (datetime.date, "2020-10-20", datetime.date(2020, 10, 20)),
    ],
)
def test_read_orm_models_from_csv_lines(
    in_memory_sqlite_database, type_, csv_value, expected_value
):
    column_type = type_from_python_type(type_)

    class Model(declarative_base()):
        __tablename__ = "test"
        pk = sqlalchemy.Column(Integer(), primary_key=True)
        value = sqlalchemy.Column(column_type)

    csv_lines = ["value", csv_value]
    models = read_orm_models_from_csv_lines(csv_lines, Model)

    engine = in_memory_sqlite_database.engine()
    Model.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(models)
        session.flush()
        result = session.query(Model.value).scalar()

    assert result == expected_value


def test_read_orm_models_from_csv_lines_params_are_exhaustive():
    # This is dirty but useful, I think. It checks that the parameters to the test
    # include at least one of every type in `sqlalchemy_types`.
    params = test_read_orm_models_from_csv_lines.pytestmark[0].args[1]
    types = [arg[0] for arg in params]
    assert set(types) == set(TYPE_MAP)
