import sqlalchemy
import sqlalchemy.orm

from cohortextractor.backends.base import BaseBackend, Column, MappedTable
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
            date=Column("varchar", source="Date"),
            result=Column("float", source="ResultValue"),
        ),
    )
    positive_tests = MappedTable(
        source="pos_tests",
        columns=dict(
            result=Column("boolean", source="PositiveResult"),
            test_date=Column("date", source="TestDate"),
        ),
    )


Base = sqlalchemy.orm.declarative_base()


class RegistrationHistory(Base):
    __tablename__ = "practice_registrations"
    RegistrationId = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    PatientId = sqlalchemy.Column(sqlalchemy.Integer)
    StpId = sqlalchemy.Column(sqlalchemy.String)
    StartDate = sqlalchemy.Column(sqlalchemy.Date)
    EndDate = sqlalchemy.Column(sqlalchemy.Date)


class Events(Base):
    __tablename__ = "events"
    EventId = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    PatientId = sqlalchemy.Column(sqlalchemy.Integer)
    EventCode = sqlalchemy.Column(sqlalchemy.String(collation="Latin1_General_BIN"))
    Date = sqlalchemy.Column(sqlalchemy.Date)
    ResultValue = sqlalchemy.Column(sqlalchemy.Float)


class PositiveTests(Base):
    __tablename__ = "pos_tests"
    Id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    PatientId = sqlalchemy.Column(sqlalchemy.Integer)
    PositiveResult = sqlalchemy.Column(sqlalchemy.Boolean)
    TestDate = sqlalchemy.Column(sqlalchemy.Date)


class Patients(Base):
    __tablename__ = "patients"
    Id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    PatientId = sqlalchemy.Column(sqlalchemy.Integer)
    Height = sqlalchemy.Column(sqlalchemy.Float)
    DateOfBirth = sqlalchemy.Column(sqlalchemy.Date)
