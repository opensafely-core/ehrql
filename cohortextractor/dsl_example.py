from cohortextractor.dsl import (
    Codelist,
    Cohort,
    Column,
    EventTable,
    PatientTable,
    categorise,
)


# These table definitions will be imported from elsewhere, and researchers will not have
# to write them.


class Patients(PatientTable):
    patient_id = Column("patient_id")
    sex = Column("sex")


class Immunisations(EventTable):
    patient_id = Column("patient_id")
    date = Column("date")
    code = Column("code")


patients = Patients()
imms = Immunisations()

# This is a cohort definition, of the kind that researchers will have to implement.

cohort = Cohort()
cohort.sex = patients.select_column(patients.sex)

covid_imms = imms.filter(imms.code in Codelist(["123", "234"]))

first = covid_imms.sort_by(imms.date).first()
cohort.first_date = first.select_column(imms.date)
cohort.first_code = first.select_column(imms.code)

second = (
    covid_imms.filter(imms.date > (cohort.first_date + 28)).sort_by(imms.date).first()
)
cohort.second_date = second.select_column("date")
cohort.second_code = second.select_column("code")

cohort.codes_match = categorise(
    {
        "yes": cohort.first_code == cohort.second_code,
        "no": True,
    }
)
