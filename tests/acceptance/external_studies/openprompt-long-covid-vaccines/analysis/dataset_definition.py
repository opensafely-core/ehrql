# where EHRQl is defined. Only really need Dastaset, tehe others are specific
from databuilder.ehrql import Dataset, days, years, case, when
# this is where we import the schema to run the study with
from databuilder.tables.beta.tpp import (
  patients,
  practice_registrations,
  clinical_events,
  vaccinations,
  sgss_covid_all_tests
)

from variable_lib import (
  age_as_of, 
  has_died,
  address_as_of,
  create_sequential_variables
)
import codelists

# Set index date
study_start_date = "2020-11-01"  # can just hardcode as string format instead of date() from datetime. But need that package for operations on dates
start_of_alpha_epoch = "2020-12-15"  # needs finalising 
start_of_delta_epoch = "2021-06-01"  # needs finalising 
start_of_omicron_epoch = "2022-01-01"
covid_to_longcovid_lag = 84  # 12 weeks
vaccine_effective_lag = 14  # 2 weeks for vaccine to become effective
vaccine_to_longcovid_lag = covid_to_longcovid_lag + vaccine_effective_lag
minimum_registration = 90  # ~3 months of previous registration
minimum_age_at_reg = years(18)

dataset = Dataset()

# practice registration selection
registrations = practice_registrations \
    .except_where(practice_registrations.start_date > study_start_date - days(minimum_registration)) \
    .except_where(practice_registrations.end_date <= study_start_date)
# get the number of registrations in this period to exclude anyone with >1 in the `set_population` later
registrations_number = registrations.count_for_patient()

# need to get the start and end date of last registration only
registration = registrations \
    .sort_by(practice_registrations.start_date).last_for_patient()
dataset.uts = case(
    when(registration.end_date.is_null()).then(study_end_date),
    when(registration.end_date > study_end_date).then(study_end_date),
    default=registration.end_date,
)

# long covid code
first_lc_dx = clinical_events.where(clinical_events.snomedct_code.is_in(codelists.long_covid_combine)) \
  .where(clinical_events.date >= start_of_omicron_epoch + days(covid_to_longcovid_lag)) \
  .sort_by(clinical_events.date).first_for_patient()

# set study end date for everyone 
# end follow up when long covid diagnosis, leave the practice, die, or end of study 
end_date = "2022-11-01"

# covid tests
dataset.latest_test_before_diagnosis = sgss_covid_all_tests \
    .where(sgss_covid_all_tests.is_positive) \
    .except_where(sgss_covid_all_tests.specimen_taken_date >= first_lc_dx.date - days(30)) \
    .sort_by(sgss_covid_all_tests.specimen_taken_date).last_for_patient().specimen_taken_date

dataset.all_test_positive = sgss_covid_all_tests \
    .where(sgss_covid_all_tests.is_positive) \
    .except_where(sgss_covid_all_tests.specimen_taken_date <= study_start_date) \
    .except_where(sgss_covid_all_tests.specimen_taken_date >= first_lc_dx.date - days(covid_to_longcovid_lag)) \
    .count_for_patient()

# Demographic variables
dataset.sex = patients.sex
dataset.age = age_as_of(study_start_date)
dataset.has_died = has_died(study_start_date)
dataset.msoa = address_as_of(study_start_date).msoa_code
dataset.imd = address_as_of(study_start_date).imd_rounded

# Ethnicity in 6 categories
dataset.ethnicity = (
    clinical_events.where(clinical_events.ctv3_code.is_in(codelists.ethnicity))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .ctv3_code.to_category(codelists.ethnicity)
)

# vaccine code
create_sequential_variables(
  dataset,
  "covid_vax_{n}_adm",
  num_variables=5,
  events=clinical_events.where(clinical_events.snomedct_code.is_in(codelists.vac_adm_combine)),
  column="date"
)

# Vaccines from the vaccines schema
all_vacc =  vaccinations \
  .where(vaccinations.date < first_lc_dx.date - days(vaccine_to_longcovid_lag)) \
  .where(vaccinations.target_disease == "SARS-2 CORONAVIRUS")
dataset.no_prev_vacc = all_vacc.count_for_patient()
dataset.date_last_vacc = all_vacc.sort_by(all_vacc.date).last_for_patient().date

# set pop and define vars
dataset.define_population(registrations_number == 1)  # when run this then 50% don't have registration as default? Dataset has 500 rows from expectation = 1000
dataset.first_lc_dx = first_lc_dx.date

# Next bits of code
# Get cohort and follow all of England (or adults only?)
# patients.satisfying https://github.com/opensafely/long-covid/blob/d44629d020e2687171264d6b42bb81a6aa92f07e/analysis/study_definition_cohort.py#L50
# Add infecction SGSS data
# Add hospitalisation data
