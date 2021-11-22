from __future__ import annotations

from datetime import date

from cohortextractor.dsl import (
    Codelist,
    Cohort,
    Column,
    EventTable,
    Expression,
    PatientTable,
    categorise,
)


# These table definitions will be imported from elsewhere, and researchers will not have
# to write them.


class Patients(PatientTable):
    patient_id: Column[Patients, int] = Column("patient_id")
    sex: Column[Patients, str] = Column("sex")


class Immunisations(EventTable):
    patient_id: Column[Immunisations, int] = Column("patient_id")
    date: Column[Immunisations, date] = Column("date")
    code: Column[Immunisations, str] = Column("code")


patients = Patients()
imms = Immunisations()

# This is a cohort definition, of the kind that researchers will have to implement.

cohort = Cohort()
cohort.sex = patients.select_column(patients.sex)

in_codelist: Expression[Immunisations, str, bool] = imms.code in Codelist(["123", "234"])  # type: ignore
covid_imms = imms.filter(in_codelist)

first = covid_imms.sort_by(imms.date).first()
cohort.first_date = first.select_column(imms.date)
cohort.first_code = first.select_column(imms.code)

later_than_first: Expression[Immunisations, date, bool] = imms.date > (cohort.first_date + 28)  # type: ignore
second = covid_imms.filter(later_than_first).sort_by(imms.date).first()
cohort.second_date = second.select_column(covid_imms.date)
cohort.second_code = second.select_column(covid_imms.code)

cohort.codes_match = categorise(
    {
        "yes": cohort.first_code == cohort.second_code,
        "no": True,
    }
)
