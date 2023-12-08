# This file is manually created, unlike tpp_schema.py

from sqlalchemy import types as t
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    "Common base class to signal that models below belong to the same database"


class ImmunisationAllOrgsV2(Base):
    __tablename__ = "immunisation_all_orgs_v2"
    _pk = mapped_column(t.Integer, primary_key=True)

    registration_id = mapped_column(t.VARCHAR(128))
    snomed_concept_id = mapped_column(t.BigInteger)
    effective_date = mapped_column(t.DateTime)


class PatientAllOrgsV2(Base):
    __tablename__ = "patient_all_orgs_v2"
    _pk = mapped_column(t.Integer, primary_key=True)

    registration_id = mapped_column(t.VARCHAR(128))
    nhs_no = mapped_column(t.VARCHAR)
    gender = mapped_column(t.Integer)
    date_of_birth = mapped_column(t.Date)
    date_of_death = mapped_column(t.Date)
    hashed_organisation = mapped_column(t.VARCHAR)
    registered_date = mapped_column(t.Date)
    registration_end_date = mapped_column(t.Date)
    rural_urban = mapped_column(t.Integer)
    imd_rank = mapped_column(t.BigInteger)


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
    snomed_concept_id = mapped_column(t.BigInteger)
    effective_date = mapped_column(t.DateTime)


class OnsView(Base):
    __tablename__ = "ons_view"
    _pk = mapped_column(t.Integer, primary_key=True)

    pseudonhsnumber = mapped_column(t.VARCHAR)
    reg_stat_dod = mapped_column(t.VARCHAR)
    icd10u = mapped_column(t.VARCHAR)
    icd10001 = mapped_column(t.VARCHAR)
    icd10002 = mapped_column(t.VARCHAR)
    icd10003 = mapped_column(t.VARCHAR)
    icd10004 = mapped_column(t.VARCHAR)
    icd10005 = mapped_column(t.VARCHAR)
    icd10006 = mapped_column(t.VARCHAR)
    icd10007 = mapped_column(t.VARCHAR)
    icd10008 = mapped_column(t.VARCHAR)
    icd10009 = mapped_column(t.VARCHAR)
    icd10010 = mapped_column(t.VARCHAR)
    icd10011 = mapped_column(t.VARCHAR)
    icd10012 = mapped_column(t.VARCHAR)
    icd10013 = mapped_column(t.VARCHAR)
    icd10014 = mapped_column(t.VARCHAR)
    icd10015 = mapped_column(t.VARCHAR)
    upload_date = mapped_column(t.VARCHAR)
