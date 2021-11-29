import sqlalchemy.orm
import sqlalchemy.types
from sqlalchemy import DDL, Column, Date, Integer, Text, event

# generate surrogate PK ids ourselves, as spark doesn't support auto id
next_id = iter(range(1, 2 ** 63)).__next__

Base = sqlalchemy.orm.declarative_base()

# ** NOTE ON PRIMARY KEYS **
# Spark has no concept of primary keys but SQLAlchemy's ORM requires some way to
# uniquely identify rows so we still need to flag the column (or combination of
# columns) which serve this role as being primary keys.


class PCareMeds(Base):
    __tablename__ = "pcaremeds"
    __table_args__ = {"schema": "PCAREMEDS"}

    Person_ID = Column(Integer, primary_key=True, default=next_id)
    PatientDoB = Column(Date)
    PrescribeddmdCode = Column(Text(collation="Latin1_General_BIN"))
    ProcessingPeriodDate = Column(Date)


class MPSHESApc(Base):
    __tablename__ = "hes_apc_1920"
    __table_args__ = {"schema": "HES_AHAS_MPS"}

    PERSON_ID = Column(Integer, primary_key=True)
    EPIKEY = Column(Integer, primary_key=True)


class HESApc(Base):
    __tablename__ = "hes_apc_1920"
    __table_args__ = {"schema": "HES_AHAS"}

    EPIKEY = Column(Integer, primary_key=True)
    ADMIDATE = Column(Date)
    DIAG_4_01 = Column(Text(collation="Latin1_General_BIN"))
    ADMIMETH = Column(Integer)
    FAE = Column(Integer)


class HESApcOtr(Base):
    __tablename__ = "hes_apc_otr_1920"
    __table_args__ = {"schema": "HES_AHAS"}

    EPIKEY = Column(Integer, primary_key=True)
    SUSSPELLID = Column(Integer)


@event.listens_for(Base.metadata, "before_create")
def receive_before_create(target, connection, **kw):
    """Ensure all schema objects are created."""
    for mapper in Base.registry.mappers:
        cls = mapper.class_
        table_args = getattr(cls, "__table_args__", {})
        schema = table_args.get("schema")
        if schema:  # pragma: no cover
            connection.execute(DDL(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
