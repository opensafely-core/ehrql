from databuilder.ehrql import Dataset, case, when
from databuilder.tables.beta.tpp import (
  clinical_events
)
import codelists

from datetime import datetime, timedelta
from variable_lib import long_covid_events_during
from datasets import add_common_variables, study_start_date, study_end_date

dataset = Dataset()

lc_dx = long_covid_events_during(study_start_date, study_end_date)

# long covid code
first_lc_dx = lc_dx.sort_by(lc_dx.date).first_for_patient()

# create flag about whether this is a diagnosis or a referral code
lc_dx_flag = case(
  when(first_lc_dx.snomedct_code.is_in(codelists.long_covid_nice_dx)).then("Dx"),
  when(first_lc_dx.snomedct_code.is_in(codelists.long_covid_assessment_codes)).then("Rx"),
  when(first_lc_dx.snomedct_code.is_in(codelists.long_covid_referral_codes)).then("Rx")
) # default = NULL

add_common_variables(dataset, study_start_date, first_lc_dx.date, population=first_lc_dx.exists_for_patient())

# add specfic variables
dataset.first_lc_dx = first_lc_dx.date
dataset.lc_dx_flag = lc_dx_flag
dataset.test_to_lc_dx_gap = (first_lc_dx.date - dataset.latest_test_before_diagnosis).days
dataset.vacc_to_lc_dx_gap = (first_lc_dx.date - dataset.date_last_vacc).days
