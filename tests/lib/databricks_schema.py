import sqlalchemy.orm
from sqlalchemy import Column, Date, Integer, Text


Base = sqlalchemy.orm.declarative_base()


class PCareMeds(Base):
    __tablename__ = "PCAREMEDS_pcaremeds"

    # Doesn't exist in real schema but needed by SQLAlchemy
    pk = Column(Integer, primary_key=True)

    Person_ID = Column(Integer)
    PatientDoB = Column(Date)
    PrescribeddmdCode = Column(Text(collation="Latin1_General_BIN"))
    ProcessingPeriodDate = Column(Date)


class MPSHESApc(Base):
    __tablename__ = "HES_AHAS_MPS_hes_apc_1920"

    # Doesn't exist in real schema but needed by SQLAlchemy
    pk = Column(Integer, primary_key=True)

    PERSON_ID = Column(Integer)
    EPIKEY = Column(Integer)


class HESApc(Base):
    __tablename__ = "HES_AHAS_hes_apc_1920"

    # Doesn't exist in real schema but needed by SQLAlchemy
    pk = Column(Integer, primary_key=True)

    EPIKEY = Column(Integer)
    ADMIDATE = Column(Date)
    DIAG_4_01 = Column(Text(collation="Latin1_General_BIN"))
    ADMINMETH = Column(Integer)
    FAE = Column(Integer)


class HESApcOtr(Base):
    __tablename__ = "HES_AHAS_hes_apc_otr_1920"

    # Doesn't exist in real schema but needed by SQLAlchemy
    pk = Column(Integer, primary_key=True)

    EPIKEY = Column(Integer)
    SUSSPELLID = Column(Integer)
