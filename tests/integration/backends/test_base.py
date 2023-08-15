import datetime

import pytest
import sqlalchemy

from ehrql import Dataset
from ehrql.backends.base import MappedTable, QueryTable, SQLBackend
from ehrql.query_engines.base_sql import BaseSQLQueryEngine
from ehrql.tables import EventFrame, PatientFrame, Series, table


Base = sqlalchemy.orm.declarative_base()


# Simple schema to test against
@table
class patients(PatientFrame):
    date_of_birth = Series(datetime.date)


@table
class covid_tests(EventFrame):
    date = Series(datetime.date)
    positive = Series(int)


class BackendFixture(SQLBackend):
    display_name = "Backend Fixture"
    query_engine_class = BaseSQLQueryEngine
    patient_join_column = "patient_id"

    # Define a table whose name and column names don't match the user-facing schema
    patients = MappedTable(
        source="patient_record",
        columns=dict(
            patient_id="PatientId",
            date_of_birth="DoB",
        ),
    )

    # Define a table which is a VIEW-like representation of data from multuple
    # underlying tables
    covid_tests = QueryTable(
        """
        SELECT patient_id, date, 1 AS positive FROM positive_result
        UNION ALL
        SELECT patient_id, date, 0 AS positive FROM negative_result
        """
    )


class PatientRecord(Base):
    __tablename__ = "patient_record"
    pk = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    PatientId = sqlalchemy.Column(sqlalchemy.Integer)
    DoB = sqlalchemy.Column(sqlalchemy.Date)


class PositiveResult(Base):
    __tablename__ = "positive_result"
    pk = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    patient_id = sqlalchemy.Column(sqlalchemy.Integer)
    date = sqlalchemy.Column(sqlalchemy.Date)


class NegativeResult(Base):
    __tablename__ = "negative_result"
    pk = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    patient_id = sqlalchemy.Column(sqlalchemy.Integer)
    date = sqlalchemy.Column(sqlalchemy.Date)


def test_mapped_table(engine):
    if engine.name == "in_memory":
        pytest.skip("doesn't apply to non-SQL engines")

    engine.setup(
        PatientRecord(PatientId=1, DoB=datetime.date(2001, 2, 3)),
    )
    results = _extract(engine, patients.date_of_birth)
    assert results == {1: datetime.date(2001, 2, 3)}


def test_query_table(engine):
    if engine.name == "in_memory":
        pytest.skip("doesn't apply to non-SQL engines")

    engine.setup(
        PositiveResult(patient_id=1, date=datetime.date(2020, 6, 1)),
        NegativeResult(patient_id=1, date=datetime.date(2020, 7, 1)),
    )
    results = _extract(
        engine, covid_tests.where(covid_tests.positive == 1).date.maximum_for_patient()
    )
    assert results == {1: datetime.date(2020, 6, 1)}


def _extract(engine, series):
    dataset = Dataset()
    dataset.define_population(
        patients.exists_for_patient() | covid_tests.exists_for_patient()
    )
    dataset.v = series
    return {
        r["patient_id"]: r["v"]
        for r in engine.extract(dataset, backend=BackendFixture())
    }
