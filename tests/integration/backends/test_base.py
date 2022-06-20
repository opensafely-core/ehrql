import datetime

import pytest
import sqlalchemy

from databuilder import sqlalchemy_types
from databuilder.backends.base import BaseBackend, Column, MappedTable, QueryTable
from databuilder.query_engines.base_sql import BaseSQLQueryEngine
from databuilder.query_language import Dataset, build_event_table, build_patient_table

from ...lib.util import next_id

Base = sqlalchemy.orm.declarative_base()


# Simple schema to test against
patients = build_patient_table(
    "patients",
    {"date_of_birth": datetime.date},
)
covid_tests = build_event_table(
    "covid_tests",
    {"date": datetime.date, "positive": int},
)


class TestBackend(BaseBackend):
    backend_id = "tests_integration_backends_test_base"
    query_engine_class = BaseSQLQueryEngine
    patient_join_column = "patient_id"

    # Define a table whose name and column names don't match the user-facing schema
    patients = MappedTable(
        source="patient_record",
        columns=dict(
            patient_id=Column("integer", source="PatientId"),
            date_of_birth=Column("date", source="DoB"),
        ),
    )

    # Define a table which is a VIEW-like representation of data from multuple
    # underlying tables
    covid_tests = QueryTable(
        columns=dict(
            date=Column("date"),
            positive=Column("boolean"),
        ),
        query="""
            SELECT patient_id, date, 1 AS positive FROM positive_result
            UNION ALL
            SELECT patient_id, date, 0 AS positive FROM negative_result
        """,
    )


class PatientRecord(Base):
    __tablename__ = "patient_record"
    pk = sqlalchemy.Column(sqlalchemy_types.Integer, primary_key=True, default=next_id)
    PatientId = sqlalchemy.Column(sqlalchemy_types.Integer)
    DoB = sqlalchemy.Column(sqlalchemy_types.Date)


class PositiveResult(Base):
    __tablename__ = "positive_result"
    pk = sqlalchemy.Column(sqlalchemy_types.Integer, primary_key=True, default=next_id)
    patient_id = sqlalchemy.Column(sqlalchemy_types.Integer)
    date = sqlalchemy.Column(sqlalchemy_types.Date)


class NegativeResult(Base):
    __tablename__ = "negative_result"
    pk = sqlalchemy.Column(sqlalchemy_types.Integer, primary_key=True, default=next_id)
    patient_id = sqlalchemy.Column(sqlalchemy_types.Integer)
    date = sqlalchemy.Column(sqlalchemy_types.Date)


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
        engine, covid_tests.take(covid_tests.positive == 1).date.maximum_for_patient()
    )
    assert results == {1: datetime.date(2020, 6, 1)}


def _extract(engine, series):
    dataset = Dataset()
    dataset.set_population(
        patients.exists_for_patient() | covid_tests.exists_for_patient()
    )
    dataset.v = series
    return {
        r["patient_id"]: r["v"] for r in engine.extract(dataset, backend=TestBackend())
    }
