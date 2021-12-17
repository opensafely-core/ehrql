import sqlalchemy
import sqlalchemy.orm

from databuilder.backends.base import BaseBackend, Column, MappedTable, QueryTable
from databuilder.dsl import Column as DSLColumn
from databuilder.dsl import DateColumn, IdColumn, IntColumn, PatientFrame
from databuilder.query_engines.mssql import MssqlQueryEngine
from databuilder.query_language import Table


def backend_factory(query_engine_cls):
    """
    Return a instance of MockBackend associated with the supplied Query Engine

    Note: argument name can't be `query_engine_class` because Python's scoping rules
    won't let us reference it in the class body.
    """

    class MockBackend(BaseBackend):
        backend_id = f"mock_{query_engine_cls.__name__}"
        query_engine_class = query_engine_cls
        patient_join_column = "PatientId"

        patients = MappedTable(
            source="patients",
            columns=dict(
                height=Column("float", source="Height"),
                date_of_birth=Column("date", source="DateOfBirth"),
                sex=Column("varchar", source="Sex"),
            ),
        )
        practice_registrations = MappedTable(
            source="practice_registrations",
            columns=dict(
                stp=Column("varchar", source="StpId"),
                date_start=Column("date", source="StartDate"),
                date_end=Column("date", source="EndDate"),
            ),
        )
        clinical_events = MappedTable(
            source="events",
            columns=dict(
                code=Column("varchar", source="EventCode"),
                system=Column("varchar", source="System"),
                date=Column("date", source="Date"),
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
                SELECT
                  PatientID as patient_id,
                  PositiveResult as result,
                  TestDate as test_date
                FROM
                  all_tests
            """,
        )

    return MockBackend


# Create a default MockBackend instance for code which is still expecting this
MockBackend = backend_factory(MssqlQueryEngine)

# Generate an integer sequence to use as default IDs. Normally you'd rely on the DBMS to
# provide these, but we need to support DBMSs like Spark which don't have this feature.
next_id = iter(range(1, 2 ** 63)).__next__


# We need each NULL-able column to have an explicit default of NULL. Without this,
# SQLAlchemy will just omit empty columns from the INSERT. That's fine for most DBMSs
# but Spark needs every column in the table to be specified, even if it just has a NULL
# value. Note: we have to use a callable returning `None` here because if we use `None`
# directly SQLAlchemy interprets this is "there is no default".
def null():
    return None


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
    EventCode = sqlalchemy.Column(
        sqlalchemy.String(collation="Latin1_General_BIN"), default=null
    )
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


def patient(patient_id, *entities, height=None, dob=None, sex="M"):
    entities = list(entities)
    # add a default RegistrationHistory entry
    entities.append(RegistrationHistory(StartDate="1900-01-01", EndDate="2999-12-31"))
    for entity in entities:
        entity.PatientId = patient_id
    return [Patients(PatientId=patient_id, Height=height, DateOfBirth=dob), *entities]


class MockPatients(PatientFrame):
    """
    A PatientFrame instance that can be used with mock backends
    """

    patient_id = IdColumn("patient_id")
    height = IntColumn("height")
    date_of_birth = DateColumn("date_of_birth")
    sex = DSLColumn("sex")

    def __init__(self):
        super().__init__(Table("patients").first_by("patient_id"))
