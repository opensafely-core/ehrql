# This file is manually created for TIDE database schema

from sqlalchemy import types as t
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    "Common base class to signal that models below belong to the same database"


class Pupils(Base):
    __tablename__ = "pupils"
    _pk = mapped_column(t.Integer, primary_key=True)

    pupil_id = mapped_column(t.Integer, nullable=False)
    mat_id = mapped_column(
        t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"), nullable=False
    )
    gender = mapped_column(
        t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"), nullable=False
    )
    date_of_birth = mapped_column(t.Date, nullable=False)
    eal = mapped_column(t.Boolean)
    send = mapped_column(t.Boolean)
    pupil_premium = mapped_column(t.Boolean)
    attendance = mapped_column(t.Integer)


class Assessments(Base):
    __tablename__ = "assessments"
    _pk = mapped_column(t.Integer, primary_key=True)

    pupil_id = mapped_column(t.Integer, nullable=False)
    date = mapped_column(t.Date)
    teacher_id = mapped_column(
        t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"), nullable=False
    )
    subject = mapped_column(
        t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"), nullable=False
    )
    result = mapped_column(t.Float)
