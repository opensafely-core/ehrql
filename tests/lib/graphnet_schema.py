import sqlalchemy.orm
from sqlalchemy import (
    NVARCHAR,
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
)

Base = sqlalchemy.orm.declarative_base()


class Patients(Base):
    __tablename__ = "TRE.Patients"
    Patient_ID = Column(Integer, primary_key=True)
    Sex = Column(NVARCHAR(50))
    DateOfBirth = Column(Date)
    DateOfDeath = Column(Date)


def patient(patient_id, sex, dob, *entities, date_of_death=None):
    for entity in entities:
        entity.Patient_ID = patient_id
    return [
        Patients(
            Patient_ID=patient_id, Sex=sex, DateOfBirth=dob, DateOfDeath=date_of_death
        ),
        *entities,
    ]


class ClinicalEvents(Base):
    __tablename__ = "TRE.ClinicalEvents"
    ClinicalEvent_ID = Column(BigInteger, primary_key=True)
    Patient_ID = Column(Integer, ForeignKey("TRE.Patients.Patient_ID"))
    Code = Column(NVARCHAR(128, collation="Latin1_General_BIN"))
    CodingSystem = Column(NVARCHAR(32))
    ConsultationDate = Column(DateTime)
    NumericValue = Column(Float)
    CareSetting = Column(NVARCHAR(9))


def snomed_clinical_event(code, date, numeric_value=None):
    return ClinicalEvents(
        Code=code,
        CodingSystem="snomed",
        ConsultationDate=date,
        NumericValue=numeric_value,
    )


class PracticeRegistrations(Base):
    __tablename__ = "TRE.PracticeRegistrations"
    PracticeRegistration_ID = Column(Integer, primary_key=True)
    Patient_ID = Column(Integer, ForeignKey("TRE.Patients.Patient_ID"))
    Organisation_ID = Column(NVARCHAR(50))
    Region = Column(NVARCHAR(50))
    StartDate = Column(DateTime)
    EndDate = Column(DateTime)


def registration(start_date, end_date, organisation_id=None, region=None):
    return PracticeRegistrations(
        StartDate=start_date,
        EndDate=end_date,
        Organisation_ID=organisation_id,
        Region=region,
    )


class CovidTestResults(Base):
    __tablename__ = "TRE.CovidTestResults"
    CovidTestResult_ID = Column(BigInteger, primary_key=True)
    Patient_ID = Column(Integer, ForeignKey("TRE.Patients.Patient_ID"))
    SpecimenDate = Column(DateTime)
    positive_result = Column(Boolean)


class Hospitalizations(Base):
    __tablename__ = "TRE.Hospitalisations"
    Hospitalisation_ID = Column(Integer, primary_key=True)
    Patient_ID = Column(Integer, ForeignKey("TRE.Patients.Patient_ID"))
    AdmitDate = Column(DateTime)
    DiagCode = Column(NVARCHAR(32))


def hospitalization(admit_date=None, code=None):
    return Hospitalizations(AdmitDate=admit_date, DiagCode=code)


class PatientAddress(Base):
    __tablename__ = "TRE.PatientAddresses"
    PatientAddress_ID = Column(Integer, primary_key=True)
    Patient_ID = Column(Integer, ForeignKey("TRE.Patients.Patient_ID"))
    StartDate = Column(DateTime)
    EndDate = Column(DateTime)
    IMD = Column(Integer)
    MSOACode = Column(NVARCHAR(9))
    has_postcode = Column(Boolean)


def patient_address(start_date, end_date, imd, msoa, postcode):
    return PatientAddress(
        StartDate=start_date,
        EndDate=end_date,
        IMD=imd,
        MSOACode=msoa,
        has_postcode=postcode,
    )
