from sqlalchemy import types as t
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    "Common base class to signal that models below belong to the same database"


class Patient(Base):
    __tablename__ = "patient"
    _pk = mapped_column(t.Integer, primary_key=True)

    patient_id = mapped_column(t.VARBINARY(16), unique=True)
    date_of_birth = mapped_column(t.DateTime)
