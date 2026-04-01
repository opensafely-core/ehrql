from sqlalchemy import types as t
from sqlalchemy.orm import DeclarativeBase, mapped_column
from trino.sqlalchemy import datatype as trdt


class Base(DeclarativeBase):
    "Common base class to signal that models below belong to the same database"


class Patient(Base):
    __tablename__ = "patient"
    _pk = mapped_column(t.Integer, primary_key=True)

    patient_id = mapped_column(t.VARBINARY())
    date_of_birth = mapped_column(trdt.TIMESTAMP(precision=6))
