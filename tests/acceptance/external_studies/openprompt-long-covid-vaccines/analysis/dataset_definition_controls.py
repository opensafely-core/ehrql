from databuilder.ehrql import Dataset

from variable_lib import long_covid_events_during
from datasets import add_common_variables, study_start_date, study_end_date

dataset = Dataset()

lc_code_any = long_covid_events_during(study_start_date, study_end_date)

# work out the end date
add_common_variables(dataset, study_start_date, study_end_date,
                     population=~lc_code_any.exists_for_patient())  # filters to those without a lc_dx code

# add specfic variables ???
