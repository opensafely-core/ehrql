from databuilder.ehrql import codelist_from_csv


# A variety of plausible long covid codelists:
# https://www.opencodelists.org/codelist/opensafely/nice-managing-the-long-term-effects-of-covid-19/64f1ae69/
long_covid_nice_dx = codelist_from_csv(
    "codelists/opensafely-nice-managing-the-long-term-effects-of-covid-19.csv",
    column="code"
)


# https://www.opencodelists.org/codelist/opensafely/referral-and-signposting-for-long-covid/12d06dc0/
long_covid_referral_codes = codelist_from_csv(
    "codelists/opensafely-referral-and-signposting-for-long-covid.csv",
    column="code"
)


# https://www.opencodelists.org/codelist/opensafely/assessment-instruments-and-outcome-measures-for-long-covid/79c0fa8a/
long_covid_assessment_codes = codelist_from_csv(
    "codelists/opensafely-assessment-instruments-and-outcome-measures-for-long-covid.csv",
    column="code"
)

long_covid_combine = (
    long_covid_nice_dx
    + long_covid_referral_codes
    + long_covid_assessment_codes
)

# https://www.opencodelists.org/codelist/opensafely/covid-identification-in-primary-care-probable-covid-sequelae/2020-07-16/
covid_primary_care_sequelae = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-probable-covid-sequelae.csv",
    column="CTV3ID",
)

# some demographic codelists:
ethnicity = codelist_from_csv(
    "codelists/opensafely-ethnicity.csv",
    column="Code",
    category_column="Grouping_6",
)

# adminstered vaccine codes
vac_adm_1 = codelist_from_csv(
  "codelists/primis-covid19-vacc-uptake-covadm1.csv",
  column="code"
)
vac_adm_2 = codelist_from_csv(
  "codelists/primis-covid19-vacc-uptake-covadm2.csv",
  column="code"
)
vac_adm_3 = codelist_from_csv(
  "codelists/primis-covid19-vacc-uptake-covadm3_cod.csv",
  column="code"
)
vac_adm_4 = codelist_from_csv(
  "codelists/primis-covid19-vacc-uptake-covadm4_cod.csv",
  column="code"
)
vac_adm_5 = codelist_from_csv(
  "codelists/primis-covid19-vacc-uptake-covadm5_cod.csv",
  column="code"
)

vac_adm_combine = vac_adm_1 + vac_adm_2 + vac_adm_3 + vac_adm_4 + vac_adm_5

hosp_covid = codelist_from_csv(
  "codelists/opensafely-covid-identification.csv",
  column="icd10_code"
)
