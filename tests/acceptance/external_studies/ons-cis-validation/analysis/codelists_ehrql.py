from databuilder.ehrql import codelist_from_csv


covid_icd10 = codelist_from_csv(
    "codelists/opensafely-covid-identification.csv",
    column="icd10_code",
)

covid_emergency = ["1240751000000100"]

covid_primary_care_positive_test = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-probable-covid-positive-test.csv",
    column="CTV3ID",
)

covid_primary_care_code = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-probable-covid-clinical-code.csv",
    column="CTV3ID",
)

covid_primary_care_sequelae = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-probable-covid-sequelae.csv",
    column="CTV3ID",
)

ethnicity = codelist_from_csv(
    "codelists/opensafely-ethnicity.csv",
    column="Code",
)

carehome = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-longres.csv",
    column="code",
)
