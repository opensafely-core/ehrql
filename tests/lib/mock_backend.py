import sqlalchemy.orm

from databuilder.backends.base import BaseBackend, Column, MappedTable, QueryTable
from databuilder.query_engines.mssql import MSSQLQueryEngine

from . import contracts
from .util import next_id, null


class MockBackend(BaseBackend):
    backend_id = "mock_backend"
    query_engine_class = MSSQLQueryEngine
    patient_join_column = "PatientId"

    patients = MappedTable(
        implements=contracts.Patients,
        source="patients",
        columns=dict(
            height=Column("integer", source="Height"),
            date_of_birth=Column("date", source="DateOfBirth"),
            sex=Column("varchar", source="Sex"),
            some_bool=Column("boolean", source="SomeBool"),
            some_int=Column("integer", source="SomeInt"),
        ),
    )
    practice_registrations = MappedTable(
        implements=contracts.Registrations,
        source="practice_registrations",
        columns=dict(
            stp=Column("varchar", source="StpId"),
            date_start=Column("date", source="StartDate"),
            date_end=Column("date", source="EndDate"),
        ),
    )
    clinical_events = MappedTable(
        implements=contracts.Events,
        source="events",
        columns=dict(
            code=Column("varchar", source="EventCode"),
            system=Column("varchar", source="System"),
            date=Column("date", source="Date"),
            value=Column("integer", source="ResultValue"),
        ),
    )
    positive_tests = QueryTable(
        implements=contracts.Tests,
        columns=dict(
            patient_id=Column("integer"),
            result=Column("boolean"),
            test_date=Column("date"),
        ),
        query="""
            SELECT
              PatientID as patient_id,
              PositiveResult as result,
              TestDate as test_date
            FROM
              all_tests
        """,
    )


Base = sqlalchemy.orm.declarative_base()


class RegistrationHistory(Base):
    __tablename__ = "practice_registrations"
    RegistrationId = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, default=next_id
    )
    PatientId = sqlalchemy.Column(sqlalchemy.Integer, default=null)
    StpId = sqlalchemy.Column(sqlalchemy.String, default=null)
    StartDate = sqlalchemy.Column(sqlalchemy.Date, default=null)
    EndDate = sqlalchemy.Column(sqlalchemy.Date, default=null)


class CTV3Events(Base):
    __tablename__ = "events"
    EventId = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, default=next_id)
    PatientId = sqlalchemy.Column(sqlalchemy.Integer, default=null)
    EventCode = sqlalchemy.Column(sqlalchemy.String, default=null)
    System = sqlalchemy.Column(sqlalchemy.String, default=null)
    Date = sqlalchemy.Column(sqlalchemy.Date, default=null)
    ResultValue = sqlalchemy.Column(sqlalchemy.Float, default=null)


def ctv3_event(code, date=None, value=None, system="ctv3"):
    return CTV3Events(EventCode=code, Date=date, ResultValue=value, System=system)


class AllTests(Base):
    __tablename__ = "all_tests"
    Id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, default=next_id)
    PatientId = sqlalchemy.Column(sqlalchemy.Integer, default=null)
    PositiveResult = sqlalchemy.Column(sqlalchemy.Boolean, default=null)
    NegativeResult = sqlalchemy.Column(sqlalchemy.Boolean, default=null)
    TestDate = sqlalchemy.Column(sqlalchemy.Date, default=null)


def positive_test(result, test_date=None):
    return AllTests(PositiveResult=result, TestDate=test_date)


class Patients(Base):
    __tablename__ = "patients"
    Id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, default=next_id)
    PatientId = sqlalchemy.Column(sqlalchemy.Integer, default=null)
    Height = sqlalchemy.Column(sqlalchemy.Float, default=null)
    DateOfBirth = sqlalchemy.Column(sqlalchemy.Date, default=null)
    Sex = sqlalchemy.Column(sqlalchemy.Text, default=null)
    SomeBool = sqlalchemy.Column(sqlalchemy.Boolean, default=null)
    SomeInt = sqlalchemy.Column(sqlalchemy.Integer, default=null)


def patient(
    patient_id, *entities, height=None, dob=None, sex="M", some_bool=False, some_int=0
):
    entities = list(entities)
    # add a default RegistrationHistory entry
    entities.append(RegistrationHistory(StartDate="1900-01-01", EndDate="2999-12-31"))
    for entity in entities:
        entity.PatientId = patient_id
    return [
        Patients(
            PatientId=patient_id,
            Height=height,
            DateOfBirth=dob,
            SomeBool=some_bool,
            SomeInt=some_int,
        ),
        *entities,
    ]
