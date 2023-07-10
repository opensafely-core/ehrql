from databuilder.ehrql import Dataset, case, when, days
import codelists

from variable_lib import long_covid_events_during, long_covid_dx_during
from datasets import (
    add_common_variables,
    study_start_date,
    study_end_date,
    covid_to_longcovid_lag
)

dataset = Dataset()

lc_code_any = long_covid_events_during(study_start_date, study_end_date)
lc_dx_code = long_covid_dx_during(study_start_date, study_end_date)

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

add_common_variables(dataset, study_start_date, first_lc_code.best_date, population=lc_code_any.exists_for_patient())

# add specfic variables
dataset.first_lc = first_lc_code.best_date
dataset.first_lc_code = first_lc_code.best_code
dataset.test_to_lc_gap = (first_lc_code.best_date - dataset.latest_test_before_diagnosis).days
dataset.vacc_to_lc_gap = (first_lc_code.best_date - dataset.date_last_vacc).days

dataset.first_lc_dx = first_lc_dx_code.date
dataset.lc_dx_flag = lc_dx_flag

# create new outcome variable for lc_dx depending on previous covid test/hospitatlisation
dataset.longcovid_categorical = case(
    when(dataset.first_lc_dx.is_after(dataset.first_covid_hosp + days(covid_to_longcovid_lag)) & dataset.first_covid_critical).then("LC post-critical COVID hospitalisation"),
    when(dataset.first_lc_dx.is_after(dataset.first_covid_hosp + days(covid_to_longcovid_lag))).then("LC post-COVID hospitalisation"),
    when(dataset.first_lc_dx.is_after(dataset.latest_primarycare_covid + days(covid_to_longcovid_lag))).then("LC post-primary care COVID"),
    when(dataset.first_lc_dx.is_after(dataset.latest_test_before_diagnosis + days(covid_to_longcovid_lag))).then("LC post-positive test"),
    when(dataset.first_lc_dx.is_after(dataset.pt_start_date)).then("LC only")
)
