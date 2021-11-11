import sqlalchemy
import sqlalchemy.orm

from cohortextractor.backends.base import BaseBackend, Column, MappedTable, QueryTable
from cohortextractor.query_engines.mssql import MssqlQueryEngine


class MockBackend(BaseBackend):
    backend_id = "mock"
    query_engine_class = MssqlQueryEngine
    patient_join_column = "PatientId"

    patients = MappedTable(
        source="patients",
        columns=dict(
            height=Column("float", source="Height"),
            date_of_birth=Column("date", source="DateOfBirth"),
        ),
    )
    practice_registrations = MappedTable(
        source="practice_registrations",
        columns=dict(
            stp=Column("varchar", source="StpId"),
            date_start=Column("datetime", source="StartDate"),
            date_end=Column("datetime", source="EndDate"),
        ),
    )
    clinical_events = MappedTable(
        source="events",
        columns=dict(
            code=Column("varchar", source="EventCode"),
            system=Column("varchar", source="System"),
            date=Column("varchar", source="Date"),
            result=Column("float", source="ResultValue"),
        ),
    )

    positive_tests = QueryTable(
        columns=dict(
            patient_id=Column("integer"),
            result=Column("boolean"),
            test_date=Column("date"),
        ),
        query="""
            SELECT PatientID as patient_id, PositiveResult as result, TestDate as test_date FROM all_tests
        """,
    )


Base = sqlalchemy.orm.declarative_base()


class RegistrationHistory(Base):
    __tablename__ = "practice_registrations"
    RegistrationId = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    PatientId = sqlalchemy.Column(sqlalchemy.Integer)
    StpId = sqlalchemy.Column(sqlalchemy.String)
    StartDate = sqlalchemy.Column(sqlalchemy.Date)
    EndDate = sqlalchemy.Column(sqlalchemy.Date)


class CTV3Events(Base):
    __tablename__ = "events"
    EventId = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    PatientId = sqlalchemy.Column(sqlalchemy.Integer)
    EventCode = sqlalchemy.Column(sqlalchemy.String(collation="Latin1_General_BIN"))
    System = sqlalchemy.Column(sqlalchemy.String)
    Date = sqlalchemy.Column(sqlalchemy.Date)
    ResultValue = sqlalchemy.Column(sqlalchemy.Float)


def ctv3_event(code, date=None, value=None, system="ctv3"):
    return CTV3Events(EventCode=code, Date=date, ResultValue=value, System=system)


class AllTests(Base):
    __tablename__ = "all_tests"
    Id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    PatientId = sqlalchemy.Column(sqlalchemy.Integer)
    PositiveResult = sqlalchemy.Column(sqlalchemy.Boolean)
    NegativeResult = sqlalchemy.Column(sqlalchemy.Boolean)
    TestDate = sqlalchemy.Column(sqlalchemy.Date)


def positive_test(result, test_date=None):
    return AllTests(PositiveResult=result, TestDate=test_date)


class Patients(Base):
    __tablename__ = "patients"
    Id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    PatientId = sqlalchemy.Column(sqlalchemy.Integer)
    Height = sqlalchemy.Column(sqlalchemy.Float)
    DateOfBirth = sqlalchemy.Column(sqlalchemy.Date)


def patient(patient_id, *entities, height=None, dob=None):
    entities = list(entities)
    if not any(isinstance(e, RegistrationHistory) for e in entities):
        entities.append(
            RegistrationHistory(StartDate="1900-01-01", EndDate="2999-12-31")
        )
    for entity in entities:
        entity.PatientId = patient_id
    return [Patients(PatientId=patient_id, Height=height, DateOfBirth=dob), *entities]
