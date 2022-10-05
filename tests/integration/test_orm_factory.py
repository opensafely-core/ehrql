import datetime
from io import StringIO

import pytest
import sqlalchemy
from sqlalchemy.orm import Session, declarative_base

from databuilder.orm_factory import (
    orm_csv_writer,
    read_orm_models_from_csv_lines,
    write_orm_models_to_csv_directory,
)
from databuilder.sqlalchemy_types import (
    TYPE_MAP,
    Date,
    Integer,
    String,
    type_from_python_type,
)


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


def test_write_orm_models_to_csv_directory(tmp_path):
    Base = declarative_base()

    class Patient(Base):
        __tablename__ = "patients"
        patient_id = sqlalchemy.Column(Integer(), primary_key=True)
        date_of_birth = sqlalchemy.Column(Date())

    class Event(Base):
        __tablename__ = "events"
        row_id = sqlalchemy.Column(Integer(), primary_key=True)
        patient_id = sqlalchemy.Column(Integer())
        date = sqlalchemy.Column(Date())
        code = sqlalchemy.Column(String())

    models = [
        Patient(patient_id=1, date_of_birth=datetime.date(2000, 1, 1)),
        Patient(patient_id=2),
        Event(patient_id=1, date=datetime.date(2020, 1, 1), code="abc"),
        Event(patient_id=1, date=datetime.date(2020, 1, 2), code="def"),
        Event(patient_id=2, date=datetime.date(2021, 3, 4), code=None),
    ]

    csv_dir = tmp_path / "csvs"
    write_orm_models_to_csv_directory(csv_dir, [Patient, Event], models)

    patients_csv = (csv_dir / "patients.csv").read_text()
    events_csv = (csv_dir / "events.csv").read_text()
    assert patients_csv == "patient_id,date_of_birth\n1,2000-01-01\n2,\n"
    assert events_csv == (
        "patient_id,date,code\n"
        "1,2020-01-01,abc\n"
        "1,2020-01-02,def\n2,2021-03-04,\n"
    )


@pytest.mark.parametrize(
    "type_,expected_csv,value",
    [
        (bool, "", None),
        (bool, "F", False),
        (bool, "T", True),
        (int, "123", 123),
        (float, "1.23", 1.23),
        (str, "foo", "foo"),
        (datetime.date, "2020-10-20", datetime.date(2020, 10, 20)),
    ],
)
def test_orm_csv_writer(type_, expected_csv, value):
    column_type = type_from_python_type(type_)

    class Model(declarative_base()):
        __tablename__ = "test"
        row_id = sqlalchemy.Column(Integer(), primary_key=True)
        patient_id = sqlalchemy.Column(Integer())
        value = sqlalchemy.Column(column_type)

    fileobj = StringIO()
    writer = orm_csv_writer(fileobj, Model)
    writer(Model(patient_id=1, value=value))

    assert fileobj.getvalue() == f"patient_id,value\r\n1,{expected_csv}\r\n"


def test_orm_csv_writer_params_are_exhaustive():
    # This is dirty but useful, I think. It checks that the parameters to the test
    # include at least one of every type in `sqlalchemy_types`.
    params = test_orm_csv_writer.pytestmark[0].args[1]
    types = [arg[0] for arg in params]
    assert set(types) == set(TYPE_MAP)
