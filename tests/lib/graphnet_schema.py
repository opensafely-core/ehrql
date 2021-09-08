import sqlalchemy.orm
from sqlalchemy import Column, Date, Integer


Base = sqlalchemy.orm.declarative_base()


class Patients(Base):
    __tablename__ = "Patients"
    patient_id = Column(Integer, primary_key=True)
    date_of_birth = Column(Date)
