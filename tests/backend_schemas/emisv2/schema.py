from sqlalchemy import types as t
from sqlalchemy.orm import DeclarativeBase, mapped_column
from trino.sqlalchemy import datatype as trdt


class Base(DeclarativeBase):
    "Common base class to signal that models below belong to the same database"


class Consultation(Base):
    __tablename__ = "consultation"
    _pk = mapped_column(t.Integer, primary_key=True)

    patient_id = mapped_column(t.VARBINARY())
    consultation_id = mapped_column(t.VARBINARY(), unique=True)
    effective_datetime = mapped_column(trdt.TIMESTAMP(precision=6, timezone=True))


class MedicationIssueRecord(Base):
    __tablename__ = "medication_issue_record"
    _pk = mapped_column(t.Integer, primary_key=True)

    patient_id = mapped_column(t.VARBINARY())
    consultation_id = mapped_column(t.VARBINARY())
    dmd_product_code_id = mapped_column(t.BIGINT())
    effective_datetime = mapped_column(trdt.TIMESTAMP(precision=6, timezone=True))


class Patient(Base):
    __tablename__ = "patient"
    _pk = mapped_column(t.Integer, primary_key=True)

    patient_id = mapped_column(t.VARBINARY(), unique=True)
    date_of_birth = mapped_column(trdt.TIMESTAMP(precision=6))


class Observation(Base):
    __tablename__ = "observation"
    _pk = mapped_column(t.Integer, primary_key=True)

    patient_id = mapped_column(t.VARBINARY())
    consultation_id = mapped_column(t.VARBINARY())
    effective_datetime = mapped_column(trdt.TIMESTAMP(precision=6, timezone=True))
    numeric_value = mapped_column(t.DECIMAL(precision=19, scale=3))
    snomed_concept_id = mapped_column(t.BIGINT())
