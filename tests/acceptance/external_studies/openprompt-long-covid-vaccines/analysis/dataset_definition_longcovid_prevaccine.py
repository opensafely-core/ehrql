from databuilder.ehrql import Dataset, when, case, days
from datetime import date
from variable_lib import long_covid_events_during, long_covid_dx_during
from databuilder.tables.beta.tpp import (
  patients,
  practice_registrations,
  clinical_events,
  vaccinations,
  ons_deaths,
  sgss_covid_all_tests,
  hospital_admissions
)
from variable_lib import (
  age_as_of,
  has_died,
  address_as_of
)
import datetime
import codelists
dataset = Dataset()

study_start_date = datetime.date(2020, 11, 1)
lc_prevaccine_end_date = date(2023, 1, 31)

minimum_registration = 90  # ~3 months of previous registration
covid_to_longcovid_lag = 84  # 12 weeks
vaccine_effective_lag = 14  # 2 weeks for vaccine to become effective
vaccine_to_longcovid_lag = covid_to_longcovid_lag + vaccine_effective_lag

# Get people with a Long COVID code --------------------------------------------------------
lc_code_any = long_covid_events_during(study_start_date, lc_prevaccine_end_date)
lc_dx_code = long_covid_dx_during(study_start_date, lc_prevaccine_end_date)

# long covid code
first_lc_code_any = lc_code_any.sort_by(lc_code_any.date).first_for_patient()
first_lc_dx_code = lc_dx_code.sort_by(lc_dx_code.date).first_for_patient()

# use the record of a patient's long covid on Dx (even if they had a Rx earlier)
first_lc_code = Dataset()
first_lc_code.has_dx = first_lc_dx_code.exists_for_patient()

first_lc_code.best_date = case(
    when(first_lc_code.has_dx & first_lc_dx_code.date.is_after(first_lc_code_any.date)).then(first_lc_dx_code.date),
    when(first_lc_code.has_dx & first_lc_dx_code.date.is_on_or_before(first_lc_code_any.date)).then(first_lc_code_any.date),
    when(~first_lc_code.has_dx).then(first_lc_code_any.date)
)
first_lc_code.best_code = case(
    when(first_lc_code.has_dx & first_lc_dx_code.date.is_after(first_lc_code_any.date)).then(first_lc_dx_code.snomedct_code),
    when(first_lc_code.has_dx & first_lc_dx_code.date.is_on_or_before(first_lc_code_any.date)).then(first_lc_code_any.snomedct_code),
    when(~first_lc_code.has_dx).then(first_lc_code_any.snomedct_code)
)

# create flag about whether this is a diagnosis or a referral code
# default = NULL
lc_dx_flag = case(
  when(first_lc_code.best_code.is_in(codelists.long_covid_nice_dx)).then("Dx"),
  when(first_lc_code.best_code.is_in(codelists.long_covid_assessment_codes)).then("Rx"),
  when(first_lc_code.best_code.is_in(codelists.long_covid_referral_codes)).then("Rx")
)

# add specfic variables
dataset.first_lc = first_lc_code.best_date
dataset.first_lc_code = first_lc_code.best_code

dataset.first_lc_dx = first_lc_dx_code.date
dataset.lc_dx_flag = lc_dx_flag

# practice registration selection ---------------------------------------------------------------
registrations = practice_registrations \
    .except_where(practice_registrations.end_date <= study_start_date)

# get the number of registrations in this period to exclude anyone with >1 in the `set_population` later
registrations_number = registrations.count_for_patient()

# need to get the start and end date of last registration only
registration = registrations \
    .sort_by(practice_registrations.start_date).last_for_patient()

dataset.pt_start_date = case(
    when(registration.start_date + days(minimum_registration) > study_start_date).then(registration.start_date + days(minimum_registration)),
    default=study_start_date,
)

dataset.pt_end_date = case(
    when(registration.end_date.is_null()).then(lc_prevaccine_end_date),
    when(registration.end_date > lc_prevaccine_end_date).then(lc_prevaccine_end_date),
    default=registration.end_date,
)

# Demographic variables ------------------------------------------------------------
dataset.sex = patients.sex
dataset.age = age_as_of(study_start_date)
dataset.has_died = has_died(study_start_date)
dataset.msoa = address_as_of(study_start_date).msoa_code
dataset.practice_nuts = registration.practice_nuts1_region_name
dataset.imd = address_as_of(study_start_date).imd_rounded

# death ------------------------------------------------------------
dataset.death_date = patients.date_of_death
dataset.ons_death_date = ons_deaths.date

# Ethnicity in 6 categories ------------------------------------------------------------
dataset.ethnicity = clinical_events.where(clinical_events.ctv3_code.is_in(codelists.ethnicity)) \
    .sort_by(clinical_events.date) \
    .last_for_patient() \
    .ctv3_code.to_category(codelists.ethnicity)

# Define the population ---------------------------------------------------------------
population = lc_code_any.exists_for_patient()
population = population & (registrations_number == 1) & (dataset.age <= 100) & (dataset.age >= 18) & (dataset.sex.contains("male"))
dataset.define_population(population)

# covid tests ------------------------------------------------------------
dataset.first_test_post_lc = sgss_covid_all_tests \
    .where(sgss_covid_all_tests.is_positive) \
    .where(sgss_covid_all_tests.specimen_taken_date.is_between_but_not_on(dataset.pt_start_date, dataset.pt_end_date)) \
    .sort_by(sgss_covid_all_tests.specimen_taken_date).first_for_patient().specimen_taken_date

dataset.all_test_positive = sgss_covid_all_tests \
    .where(sgss_covid_all_tests.is_positive) \
    .where(sgss_covid_all_tests.specimen_taken_date.is_between_but_not_on(dataset.pt_start_date, dataset.pt_end_date)) \
    .count_for_patient()

dataset.all_tests = sgss_covid_all_tests \
    .where(sgss_covid_all_tests.specimen_taken_date.is_between_but_not_on(dataset.pt_start_date, dataset.pt_end_date)) \
    .count_for_patient()

# VACCCINES ------------------------------------------------------------
already_vacced = vaccinations \
  .where(vaccinations.date.is_before(dataset.pt_start_date)) \
  .sort_by(vaccinations.date) \
  .first_for_patient()

dataset.already_vacced = case(
    when(already_vacced.exists_for_patient()).then(1),
    when(~already_vacced.exists_for_patient()).then(0)
)

# Vaccines from the vaccines schema
# only take one record per day to remove duplication
all_vacc = vaccinations \
    .where(vaccinations.date.is_before(dataset.pt_end_date)) \
    .where(vaccinations.target_disease == "SARS-2 CORONAVIRUS")

# this will be replaced with distinct_count_for_patient() once it is developed
dataset.no_total_vacc = all_vacc \
    .count_for_patient()
dataset.no_post_lc_vacc = all_vacc \
  .where(all_vacc.date.is_after(dataset.pt_start_date)) \
  .count_for_patient()

dataset.date_first_vacc_ever = all_vacc \
  .sort_by(all_vacc.date) \
  .first_for_patient().date

dataset.date_first_vacc_post_lc = all_vacc \
  .where(all_vacc.date.is_after(dataset.pt_start_date)) \
  .sort_by(all_vacc.date) \
  .first_for_patient().date

# FIRST VACCINE DOSE ------------------------------------------------------------
# first vaccine dose was 8th December 2020
vaccine_dose_1 = all_vacc \
    .where(all_vacc.date.is_after(datetime.date(2020, 12, 7))) \
    .sort_by(all_vacc.date) \
    .first_for_patient()
dataset.vaccine_dose_1_date = vaccine_dose_1.date
dataset.vaccine_dose_1_manufacturer = vaccine_dose_1.product_name

# SECOND VACCINE DOSE ------------------------------------------------------------
# first recorded 2nd dose was 29th December 2020
# need a 19 day gap from first dose
vaccine_dose_2 = all_vacc \
    .where(all_vacc.date.is_after(datetime.date(2020, 12, 28))) \
    .where(all_vacc.date.is_after(dataset.vaccine_dose_1_date + days(19))) \
    .sort_by(all_vacc.date) \
    .first_for_patient()
dataset.vaccine_dose_2_date = vaccine_dose_2.date
dataset.vaccine_dose_2_manufacturer = vaccine_dose_2.product_name

# Final variables for useful time gaps
# the variable is called `latest_test_before_diagnosis` but in this case it is latest test before `pt_end_date`
dataset.lc_to_test_gap = (dataset.first_test_post_lc - first_lc_code.best_date).days
dataset.lc_to_vacc_gap = (dataset.date_first_vacc_post_lc - first_lc_code.best_date).days
