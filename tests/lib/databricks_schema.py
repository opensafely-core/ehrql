import sqlalchemy.orm
import sqlalchemy.types
from sqlalchemy import Column, Integer, Text

from cohortextractor.query_engines.spark_lib import SparkDate as Date


Base = sqlalchemy.orm.declarative_base()

# ** NOTE ON PRIMARY KEYS **
# Spark has no concept of primary keys but SQLAlchemy's ORM requires some way to
# uniquely identify rows so we still need to flag the column (or combination of
# columns) which serve this role as being primary keys.


class PCareMeds(Base):
    __tablename__ = "PCAREMEDS_pcaremeds"

    Person_ID = Column(Integer, primary_key=True)
    PatientDoB = Column(Date)
    PrescribeddmdCode = Column(Text(collation="Latin1_General_BIN"), primary_key=True)
    ProcessingPeriodDate = Column(Date, primary_key=True)


class MPSHESApc(Base):
    __tablename__ = "HES_AHAS_MPS_hes_apc_1920"

    PERSON_ID = Column(Integer, primary_key=True)
    EPIKEY = Column(Integer, primary_key=True)


class HESApc(Base):
    __tablename__ = "HES_AHAS_hes_apc_1920"

    EPIKEY = Column(Integer, primary_key=True)
    ADMIDATE = Column(Date)
    DIAG_4_01 = Column(Text(collation="Latin1_General_BIN"))
    ADMIMETH = Column(Integer)
    FAE = Column(Integer)


class HESApcOtr(Base):
    __tablename__ = "HES_AHAS_hes_apc_otr_1920"

    EPIKEY = Column(Integer, primary_key=True)
    SUSSPELLID = Column(Integer)
