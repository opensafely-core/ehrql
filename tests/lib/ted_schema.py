# This file is manually created for TED database schema

from sqlalchemy import types as t
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    "Common base class to signal that models below belong to the same database"


class Students(Base):
    __tablename__ = "Students"
    _pk = mapped_column(t.Integer, primary_key=True)

    Student_ID = mapped_column(t.Integer, nullable=False)
    MAT_ID = mapped_column(
        t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"), nullable=False
    )
    School_ID = mapped_column(
        t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"), nullable=False
    )
    Cohort = mapped_column(t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"))
    Gender = mapped_column(t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"))
    KS2_maths = mapped_column(t.Float)
    KS2_reading = mapped_column(t.Float)
    CAT_test = mapped_column(t.Float, name="CAT test")
    Reading_Age = mapped_column(t.Float, name="Reading Age")
    PP_status = mapped_column(t.Boolean)
    EAL = mapped_column(t.Boolean)
    SEN = mapped_column(t.Boolean)
    SEN_E = mapped_column(t.Boolean, name="SEN E")
    LAC = mapped_column(t.Boolean)
    Attendance = mapped_column(t.Integer)


class AttainmentResults(Base):
    __tablename__ = "AttainmentResults"
    _pk = mapped_column(t.Integer, primary_key=True)

    Student_ID = mapped_column(t.Integer, nullable=False)
    Assessment_ID = mapped_column(t.Integer)
    Class_ID = mapped_column(
        t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"), nullable=False
    )
    Date = mapped_column(t.Date)
    Score = mapped_column(t.Float)
    Predicted_Grade = mapped_column(t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"))


class Assessments(Base):
    __tablename__ = "Assessments"
    _pk = mapped_column(t.Integer, primary_key=True)

    Assessment_ID = mapped_column(t.Integer, nullable=False)
    Subject = mapped_column(
        t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"), nullable=False
    )
    No_qns = mapped_column(t.Integer)
    Assessment_type = mapped_column(t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"))


class Classes(Base):
    __tablename__ = "Classes"
    _pk = mapped_column(t.Integer, primary_key=True)

    Class_ID = mapped_column(
        t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"), nullable=False
    )
    School_ID = mapped_column(t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"))
    Year_group = mapped_column(t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"))
    Academic_year = mapped_column(t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"))


class TeacherClassAllocation(Base):
    __tablename__ = "TeacherClassAllocation"
    _pk = mapped_column(t.Integer, primary_key=True)

    Tch_Class_ID = mapped_column(
        t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"), nullable=False
    )
    Teacher_ID = mapped_column(
        t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"), nullable=False
    )
    Class_ID = mapped_column(
        t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"), nullable=False
    )
    Subject = mapped_column(t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"))
    Academic_year = mapped_column(t.VARCHAR(collation="SQL_Latin1_General_CP1_CS_AS"))
    Percentage = mapped_column(t.Float)
