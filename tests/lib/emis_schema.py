# This file is manually created, unlike tpp_schema.py

from sqlalchemy import types as t
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    "Common base class to signal that models below belong to the same database"


class PatientAllOrgsV2(Base):
    __tablename__ = "patient_all_orgs_v2"
    _pk = mapped_column(t.Integer, primary_key=True)

    registration_id = mapped_column(t.VARCHAR(128))
    gender = mapped_column(t.Integer)
    date_of_birth = mapped_column(t.Date)
    date_of_death = mapped_column(t.Date)


class ObservationAllOrgsV2(Base):
    __tablename__ = "observation_all_orgs_v2"
    _pk = mapped_column(t.Integer, primary_key=True)

    registration_id = mapped_column(t.VARCHAR(128))
    snomed_concept_id = mapped_column(t.Integer)
    effective_date = mapped_column(t.DateTime)
    value_pq_1 = mapped_column(t.DECIMAL(20, 2))


class MedicationAllOrgsV2(Base):
    __tablename__ = "medication_all_orgs_v2"
    _pk = mapped_column(t.Integer, primary_key=True)

    registration_id = mapped_column(t.VARCHAR(128))
    snomed_concept_id = mapped_column(t.Integer)
    effective_date = mapped_column(t.DateTime)
