import sqlalchemy.orm
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String


Base = sqlalchemy.orm.declarative_base()


class Patient(Base):
    __tablename__ = "Patient"
    Patient_ID = Column(Integer, primary_key=True)


class RegistrationHistory(Base):
    __tablename__ = "RegistrationHistory"
    Registration_ID = Column(Integer, primary_key=True)
    Patient_ID = Column(Integer, ForeignKey("Patient.Patient_ID"))
    StartDate = Column(DateTime)
    EndDate = Column(DateTime)


class Events(Base):
    __tablename__ = "CodedEvent"
    CodedEvent_ID = Column(Integer, primary_key=True)
    Patient_ID = Column(Integer, ForeignKey("Patient.Patient_ID"))
    CTV3Code = Column(
        String(
            collation="Latin1_General_BIN"
        )  # TODO: copied collation from old cohort extractor, do we actually need it?
    )
    ConsultationDate = Column(DateTime)


class SGSSPositiveTests(Base):
    __tablename__ = "SGSS_AllTests_Positive"
    Result_ID = Column(
        Integer, primary_key=True
    )  # Doesn't exist but needed by SQLAlchemy
    Patient_ID = Column(Integer, ForeignKey("Patient.Patient_ID"))
    Organism_Species_Name = Column(String)
    Specimen_Date = Column(Date)


class SGSSNegativeTests(Base):
    __tablename__ = "SGSS_AllTests_Negative"
    Result_ID = Column(
        Integer, primary_key=True
    )  # Doesn't exist but needed by SQLAlchemy
    Patient_ID = Column(Integer, ForeignKey("Patient.Patient_ID"))
    Organism_Species_Name = Column(String)
    Specimen_Date = Column(Date)
