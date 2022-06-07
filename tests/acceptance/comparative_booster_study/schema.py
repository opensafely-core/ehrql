import datetime

import sqlalchemy.orm

from databuilder.query_language import build_event_table, build_patient_table

from ...lib.util import orm_class_from_table

Base = sqlalchemy.orm.declarative_base()


patients = build_patient_table(
    "patients",
    {
        "date_of_birth": datetime.date,
    },
)

Patient = orm_class_from_table(Base, patients)


vaccinations = build_event_table(
    "vaccinations",
    {
        "date": datetime.date,
        "target_disease": str,
        "product_name": str,
    },
)

Vaccination = orm_class_from_table(Base, vaccinations)
