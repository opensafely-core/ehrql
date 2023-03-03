from databuilder.ehrql import Dataset
from databuilder.tables.beta.tpp import (
  clinical_events
)

from datetime import date
from variable_lib import long_covid_events_during
from datasets import add_common_variables, study_start_date

dataset = Dataset()

lc_prevaccine_end_date = date(2021, 9, 1)

lc_dx = long_covid_events_during(study_start_date, lc_prevaccine_end_date)

# long covid code
first_lc_dx = lc_dx.sort_by(clinical_events.date).first_for_patient()

add_common_variables(dataset, first_lc_dx.date, lc_prevaccine_end_date, population=first_lc_dx.exists_for_patient())

# add specfic variables
dataset.first_lc_dx = first_lc_dx.date
dataset.lc_dx_vacc_gap = (dataset.date_last_vacc - first_lc_dx.date).days
