from sqlalchemy import Boolean, Column
from sqlalchemy import Date as SqlaDate
from sqlalchemy import Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class RegistrationHistory(Base):
    __tablename__ = "practice_registrations"
    RegistrationId = Column(Integer, primary_key=True)
    PatientId = Column(Integer)
    StpId = Column(String)


class Events(Base):
    __tablename__ = "events"
    EventId = Column(Integer, primary_key=True)
    PatientId = Column(Integer)
    EventCode = Column(String)
    Date = Column(SqlaDate)
    ResultValue = Column(Float)


class PositiveTests(Base):
    __tablename__ = "pos_tests"
    Id = Column(Integer, primary_key=True)
    PatientId = Column(Integer)
    PositiveResult = Column(Boolean)
    TestDate = Column(SqlaDate)
