# Explanation: 
# These covariates will be added to the matched datasets, so the final set.population 
# codes will be removed later when the importing CSV file function is enable.

# local variables for defining covariates
from datetime import date
from databuilder.ehrql import Dataset, days, years,  case, when
from databuilder.tables.beta.tpp import (
    patients, addresses, appointments, vaccinations,
    practice_registrations, clinical_events,
    sgss_covid_all_tests, ons_deaths, hospital_admissions,
)

from databuilder.codes import CTV3Code, DMDCode, ICD10Code, SNOMEDCTCode
import codelists
from codelists import lc_codelists_combined
from variables import (
    hospitalisation_diagnosis_matches,
    clinical_ctv3_matches, 
    create_sequential_variables,
)

study_start_date = date(2020, 11, 1)
study_end_date = date(2023, 1, 31)

# age 
age = (study_start_date - patients.date_of_birth).years

# current registration
registration = practice_registrations \
    .where(practice_registrations.start_date <= study_start_date - days(90))\
    .except_where(practice_registrations.end_date <= study_start_date) \
    .sort_by(practice_registrations.start_date).last_for_patient()

registrations_number = practice_registrations \
    .where(practice_registrations.start_date <= study_start_date - days(90))\
    .except_where(practice_registrations.end_date <= study_start_date) \
    .sort_by(practice_registrations.start_date) \
    .count_for_patient()

# Registration more than a year 
registration_1y = practice_registrations \
    .where(practice_registrations.start_date <= study_start_date - days(365))\
    .except_where(practice_registrations.end_date <= study_start_date) \
    .sort_by(practice_registrations.start_date).last_for_patient()

registrations_number_1y = practice_registrations \
    .where(practice_registrations.start_date <= study_start_date - days(365))\
    .except_where(practice_registrations.end_date <= study_start_date) \
    .sort_by(practice_registrations.start_date) \
    .count_for_patient()

# Had non zero GP visits in previous year:
ever_visit_gp_1y = clinical_events.where(clinical_events.date >= (study_start_date - days(365))) \
    .where(clinical_events.date <= study_start_date) \
    .sort_by(clinical_events.date) \
    .last_for_patient()# had ever visited a GP in the previous year 

# long covid diagnoses
lc_dx = clinical_events.where(clinical_events.snomedct_code.is_in(lc_codelists_combined)) \
    .where(clinical_events.date >= study_start_date) \
    .where(clinical_events.date <= study_end_date) \
    .sort_by(clinical_events.date) \
    .first_for_patient()# had lc dx and dx dates
lc_dx_date = lc_dx.date.if_null_then(study_end_date)

# define end date: lc dx date +12 | death | derigistration | post COVID-19 syndrome resolved
one_year_after_start = lc_dx.date + days(365) 
death_date = ons_deaths.date.if_null_then(study_end_date)
end_reg_date = practice_registrations \
    .where(practice_registrations.start_date <= study_start_date - days(90))\
    .except_where(practice_registrations.end_date <= study_start_date) \
    .sort_by(practice_registrations.start_date) \
    .last_for_patient().end_date.if_null_then(study_end_date)

# The first recorded lc cure date
lc_cure = clinical_events.where(clinical_events.snomedct_code ==  SNOMEDCTCode("1326351000000108")) \
    .sort_by(clinical_events.date) \
    .first_for_patient()
lc_cure_date = lc_cure.date.if_null_then(study_end_date)


# covid tests
latest_test_before_diagnosis = sgss_covid_all_tests.where(sgss_covid_all_tests.is_positive) \
    .except_where(sgss_covid_all_tests.specimen_taken_date >= lc_dx.date - days(90)) \
    .sort_by(sgss_covid_all_tests.specimen_taken_date) \
    .last_for_patient()
# # only need the diagnostic month for sensitivity analysis matching

# Demographic: ethnicity
## Ethnicity 
ethnicity = (clinical_events.where(clinical_events.ctv3_code.is_in(codelists.ethnicity))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .ctv3_code.to_category(codelists.ethnicity)
)
## IMD
# # 1. drop the start date records after index date
# # 2. sort the date, keep the latest
imd = (addresses.except_where(addresses.start_date > study_start_date)
    .sort_by(addresses.start_date)
    .last_for_patient().imd_rounded
)
## BMI
bmi_record = (
    clinical_events.where(
        clinical_events.snomedct_code.is_in(
            [SNOMEDCTCode("60621009"), SNOMEDCTCode("846931000000101")]
        )
    )
    # Exclude out-of-range values
    .where((clinical_events.numeric_value > 4.0) & (clinical_events.numeric_value < 200.0))
    # Exclude measurements taken when patient was younger than 16
    .where(clinical_events.date >= patients.date_of_birth + years(16))
    .sort_by(clinical_events.date)
    .last_for_patient()
)

bmi = bmi_record.numeric_value
bmi_date = bmi_record.date


# Clinical factors:
# 1. Previous hospitalized due to COVID (only look at hospitalisation before the index date)
# previous_covid_hos = (hospitalisation_diagnosis_matches(hospital_admissions, codelists.hosp_covid)
#     .where(hospital_admissions.admission_date < index_date)
#     .sort_by(hospital_admissions.admission_date)
#     .first_for_patient()
# )
# Mental issues:
mental_health_issues = clinical_ctv3_matches(clinical_events, codelists.mental_health_all)

# Respiratory condition: only include asthma
asthma = clinical_ctv3_matches(clinical_events, codelists.asthma)
copd = clinical_ctv3_matches(clinical_events, codelists.copd)

# the number of Covid-19 vaccinations doses (any vaccine) before the index date
# vaccine dose: at least one dose/one dose/two dose/three doses or more

# c19_vaccine_number = (vaccinations
#     .where(vaccinations.date < index_date)
#     .where(vaccinations.target_disease == "SARS-2 CORONAVIRUS")
# 	.count_for_patient()
# )


# level of multimorbidity ------

# Non-haematological cancer
# Haematological cancer 1

# * need to saperate the heamatological cancers
## Cancer: 
# ## Cancer diagnosed from GP records
cancer_all = clinical_ctv3_matches(clinical_events, codelists.cancer_all_combined__codelist) 

# Organ transplant
organ_transplant = clinical_ctv3_matches(clinical_events, codelists.organ_transplant_code)

# Chronic cardiac disease
chronic_cardiac_disease = clinical_ctv3_matches(clinical_events, codelists.chronic_cardiac_diseases_code)

# Chronic liver disease
chronic_liver_disease = clinical_ctv3_matches(clinical_events, codelists.chronic_liver_disease_code)

# Stroke or dementia
stroke = clinical_ctv3_matches(clinical_events, codelists.stroke_code)
dementia = clinical_ctv3_matches(clinical_events, codelists.dementia_code)

# Other neurological condition 
other_neuro_diseases = clinical_ctv3_matches(clinical_events, codelists.other_neuro_code)
# Rheumatoid arthritis
# Systemic lupus erythematosus 
# Psoriasis
ra_sle_psoriasis = clinical_ctv3_matches(clinical_events, codelists.ra_sle_psoriasis_code)

# Other immunosuppressive conditions 
# #  asplenia
asplenia = clinical_ctv3_matches(clinical_events, codelists.asplenia_code)

# # HIV
hiv = clinical_ctv3_matches(clinical_events, codelists.hiv_code)

# # Aplastic anemia
aplastic_anemia = clinical_ctv3_matches(clinical_events, codelists.aplastic_anemia_code)

# # permanent immunosuppression
permanent_immune_suppress = clinical_ctv3_matches(clinical_events, codelists.permanent_immune_suppress_code)

# # temporary immunosuppression
temporary_immune_suppress = clinical_ctv3_matches(clinical_events, codelists.temporary_immune_suppress_code)


# The following codes will be removed later when the importing CSV file function is ready. 
# Use these codes to test this is working. 

# dataset = Dataset()
# dataset.define_population((age>= 18) & (age <=100) & (registrations_number == 1))
# dataset.reg_and_visit_gp_1y = registration_1y.exists_for_patient() & ever_visit_gp_1y.exists_for_patient() & (registrations_number_1y==1) 
# dataset.ethnicity = ethnicity
# dataset.imd = imd
# dataset.bmi = bmi
# dataset.bmi_date = bmi_date
# dataset.cov_cancer = cancer_all.exists_for_patient()
# dataset.cov_mental_health = mental_health_issues.exists_for_patient()
# dataset.cov_asthma = asthma.exists_for_patient() & ~copd.exists_for_patient()
# dataset.cov_organ_transplant = organ_transplant.exists_for_patient()
# dataset.cov_chronic_cardiac_disease = chronic_cardiac_disease.exists_for_patient()
# dataset.cov_chronic_liver_disease = chronic_liver_disease.exists_for_patient()
# dataset.cov_stroke_dementia = stroke.exists_for_patient() | dementia.exists_for_patient()
# dataset.cov_other_neuro_diseases = other_neuro_diseases.exists_for_patient()
# dataset.cov_ra_sle_psoriasis = ra_sle_psoriasis.exists_for_patient()
# dataset.cov_asplenia = asplenia.exists_for_patient()
# dataset.cov_hiv = hiv.exists_for_patient()
# dataset.cov_aplastic_anemia = aplastic_anemia.exists_for_patient()
# dataset.cov_permanent_immune_suppress = permanent_immune_suppress.exists_for_patient()
# dataset.cov_temporary_immune_suppress = temporary_immune_suppress.exists_for_patient()