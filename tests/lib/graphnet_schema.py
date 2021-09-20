import sqlalchemy.orm
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, Boolean, BigInteger, NVARCHAR

Base = sqlalchemy.orm.declarative_base()

class Patients(Base):
    __tablename__ = "TRE.Patients"
    Patient_ID = Column(Integer, primary_key=True)
    Sex = Column(NVARCHAR(50))
    DateOfBirth = Column(Date)
    DateOfDeath = Column(Date)

class ClinicalEvents(Base):
    __tablename__ = "TRE.ClinicalEvents"
    ClinicalEvent_ID = Column(BigInteger, primary_key=True)
    Patient_ID = Column(Integer, ForeignKey("TRE.Patients.Patient_ID"))
    CTV3Code = Column(NVARCHAR(64))
    ConsultationDate = Column(DateTime)
    NumericValue = Column(Float)

class ClinicalEventsSnomed(Base):
    __tablename__ = "TRE.ClinicalEvents_Snomed"
    ClinicalEvent_ID = Column(BigInteger, primary_key=True)
    Patient_ID = Column(Integer, ForeignKey("TRE.Patients.Patient_ID"))
    ConceptID = Column(NVARCHAR(64))
    ConsultationDate = Column(DateTime)
    NumericValue = Column(Float)

class PracticeRegistrations(Base):
    __tablename__ = "TRE.PracticeRegistrations"
    PracticeRegistration_ID = Column(Integer, primary_key=True)
    Patient_ID = Column(Integer, ForeignKey("TRE.Patients.Patient_ID"))
    Organisation_ID = Column(NVARCHAR(50))
    Region = Column(NVARCHAR(50))
    StartDate = Column(DateTime)
    EndDate = Column(DateTime)

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

class PatientAddress(Base):
    __tablename__ = "TRE.PatientAddresses"
    PatientAddress_ID = Column(Integer, primary_key=True)
    Patient_ID = Column(Integer, ForeignKey("TRE.Patients.Patient_ID"))
    StartDate = Column(DateTime)
    EndDate = Column(DateTime)
    IMD = Column(Integer)
    has_postcode = Column(Boolean)
