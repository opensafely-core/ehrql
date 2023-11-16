import datetime
from databuilder.ehrql import Dataset, days, years
from databuilder.tables.beta.tpp import (
    patients, addresses, 
    ons_deaths, 
    sgss_covid_all_tests,
    practice_registrations, 
    clinical_events,
    vaccinations,
)
from ehrql.query_language import table_from_file, PatientFrame, Series
from covariates import *
from variables import *
from ehrql import minimum_of

# import matched data

@table_from_file("output/matched_cases_stp.csv")
class matched_cases(PatientFrame):
    age = Series(int)
    sex = Series(str)
    region = Series(str)
    registration_date = Series(date)
    long_covid_dx = Series(int)
    long_covid_dx_date= Series(date)
    index_date = Series(date)
    end_death = Series(date)
    end_deregist = Series(date)
    end_lc_cure = Series(date)
    set_id = Series(int)
    exposure = Series(int)
    match_counts = Series(float)

# Define dataset variables

dataset = Dataset()
dataset.define_population(
    (age >= 18)
    & matched_cases.exists_for_patient()
)
dataset.age = matched_cases.age
dataset.sex = matched_cases.sex
dataset.region = matched_cases.region
dataset.registration_date = matched_cases.registration_date
dataset.long_covid_dx = matched_cases.long_covid_dx
dataset.long_covid_dx_date= matched_cases.long_covid_dx_date
dataset.index_date = matched_cases.index_date
dataset.end_death = matched_cases.end_death
dataset.end_deregist = matched_cases.end_deregist
dataset.end_lc_cure = matched_cases.end_lc_cure
dataset.end_date = minimum_of(dataset.end_death, dataset.end_deregist, dataset.end_lc_cure, study_end_date)
dataset.set_id = matched_cases.set_id
dataset.exposure = matched_cases.exposure
dataset.match_counts = matched_cases.match_counts

# Add previous covid hospitalisation
# 1. Previous hospitalized due to COVID (only look at hospitalisation before the index date)
previous_covid_hos = (hospitalisation_diagnosis_matches(hospital_admissions, codelists.hosp_covid)
    .where(hospital_admissions.admission_date < matched_cases.index_date)
    .sort_by(hospital_admissions.admission_date)
    .first_for_patient()
)

# Number of vaccines received before the index date and after study start date
all_vacc = vaccinations \
    .where(vaccinations.date < matched_cases.index_date) \
    .where(vaccinations.date > study_start_date) \
    .where(vaccinations.target_disease == "SARS-2 CORONAVIRUS") \
    .sort_by(vaccinations.date)

c19_vaccine_number = all_vacc.count_for_patient()  # some people may have more than one vaccine record on the same day.

create_sequential_variables(
    dataset,
    "covid_vacc_{n}_vacc_tab",
    num_variables=6,
    events=all_vacc,
    column="date"
)

# Calculate how many times does a person admit for more than a month
hospital_stay_more_30 = hospital_admissions \
    .where(hospital_admissions.admission_date >= matched_cases.index_date) \
    .where(hospital_admissions.admission_date <= study_end_date) \
    .where(hospital_admissions.discharge_date.is_on_or_after(hospital_admissions.discharge_date)) \
    .where(hospital_admissions.discharge_date.is_after(hospital_admissions.admission_date + days(30))) \
    .count_for_patient()

dataset.covid_positive = latest_test_before_diagnosis.exists_for_patient()
dataset.covid_dx_month = latest_test_before_diagnosis.specimen_taken_date.to_first_of_month() # only need dx month
dataset.ethnicity = (clinical_events.where(clinical_events.ctv3_code.is_in(codelists.ethnicity))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .ctv3_code.to_category(codelists.ethnicity)
)
dataset.imd = imd
dataset.bmi = bmi
dataset.bmi_date = bmi_date
dataset.previous_covid_hosp = previous_covid_hos.exists_for_patient()
dataset.admit_over_1m_count = hospital_stay_more_30
dataset.cov_c19_vaccine_number = c19_vaccine_number
dataset.cov_cancer = cancer_all.exists_for_patient()
dataset.cov_mental_health = mental_health_issues.exists_for_patient()
dataset.cov_asthma = clinical_ctv3_matches(clinical_events, codelists.asthma).exists_for_patient() & ~clinical_ctv3_matches(clinical_events, codelists.copd).exists_for_patient()
dataset.cov_organ_transplant = organ_transplant.exists_for_patient()
dataset.cov_chronic_cardiac_disease = chronic_cardiac_disease.exists_for_patient()
dataset.cov_chronic_liver_disease = chronic_liver_disease.exists_for_patient()
dataset.cov_stroke_dementia = stroke.exists_for_patient() | dementia.exists_for_patient()
dataset.cov_other_neuro_diseases = other_neuro_diseases.exists_for_patient()
dataset.cov_ra_sle_psoriasis = ra_sle_psoriasis.exists_for_patient()
dataset.cov_asplenia = asplenia.exists_for_patient()
dataset.cov_hiv = hiv.exists_for_patient()
dataset.cov_aplastic_anemia = aplastic_anemia.exists_for_patient()
dataset.cov_permanent_immune_suppress = permanent_immune_suppress.exists_for_patient()
dataset.cov_temporary_immune_suppress = temporary_immune_suppress.exists_for_patient()
dataset.reg_and_visit_gp_1y = registration_1y.exists_for_patient() & ever_visit_gp_1y.exists_for_patient() & (registrations_number_1y==1) 

# Add outcomes: healthcare utilisation by months
# GP prescription visits:
monthly_drug_visit(dataset, dataset.index_date, num_months=1, end_date=study_end_date)
monthly_drug_visit(dataset, dataset.index_date, num_months=2, end_date=study_end_date)
monthly_drug_visit(dataset, dataset.index_date, num_months=3, end_date=study_end_date)
monthly_drug_visit(dataset, dataset.index_date, num_months=4, end_date=study_end_date)
monthly_drug_visit(dataset, dataset.index_date, num_months=5, end_date=study_end_date)
monthly_drug_visit(dataset, dataset.index_date, num_months=6, end_date=study_end_date)
monthly_drug_visit(dataset, dataset.index_date, num_months=7, end_date=study_end_date)
monthly_drug_visit(dataset, dataset.index_date, num_months=8, end_date=study_end_date)
monthly_drug_visit(dataset, dataset.index_date, num_months=9, end_date=study_end_date)
monthly_drug_visit(dataset, dataset.index_date, num_months=10, end_date=study_end_date)
monthly_drug_visit(dataset, dataset.index_date, num_months=11, end_date=study_end_date)
monthly_drug_visit(dataset, dataset.index_date, num_months=12, end_date=study_end_date)

# GP visit
add_visits(dataset, dataset.index_date, num_months=1, end_date= dataset.end_date)
add_visits(dataset, dataset.index_date, num_months=2, end_date= dataset.end_date)
add_visits(dataset, dataset.index_date, num_months=3, end_date= dataset.end_date)
add_visits(dataset, dataset.index_date, num_months=4, end_date= dataset.end_date)
add_visits(dataset, dataset.index_date, num_months=5, end_date= dataset.end_date)
add_visits(dataset, dataset.index_date, num_months=6, end_date= dataset.end_date)
add_visits(dataset, dataset.index_date, num_months=7, end_date= dataset.end_date)
add_visits(dataset, dataset.index_date, num_months=8, end_date= dataset.end_date)
add_visits(dataset, dataset.index_date, num_months=9, end_date= dataset.end_date)
add_visits(dataset, dataset.index_date, num_months=10, end_date= dataset.end_date)
add_visits(dataset, dataset.index_date, num_months=11, end_date= dataset.end_date)
add_visits(dataset, dataset.index_date, num_months=12, end_date= dataset.end_date)

# Hospital admission
add_hos_visits(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
add_hos_visits(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
add_hos_visits(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
add_hos_visits(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
add_hos_visits(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
add_hos_visits(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
add_hos_visits(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
add_hos_visits(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
add_hos_visits(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
add_hos_visits(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
add_hos_visits(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
add_hos_visits(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)

# A&E
add_ae_visits(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
add_ae_visits(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
add_ae_visits(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
add_ae_visits(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
add_ae_visits(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
add_ae_visits(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
add_ae_visits(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
add_ae_visits(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
add_ae_visits(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
add_ae_visits(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
add_ae_visits(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
add_ae_visits(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)


# Outpatient visit
outpatient_visit(dataset, from_date=dataset.index_date, num_months=1, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=dataset.index_date, num_months=2, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=dataset.index_date, num_months=3, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=dataset.index_date, num_months=4, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=dataset.index_date, num_months=5, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=dataset.index_date, num_months=6, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=dataset.index_date, num_months=7, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=dataset.index_date, num_months=8, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=dataset.index_date, num_months=9, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=dataset.index_date, num_months=10, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=dataset.index_date, num_months=11, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=dataset.index_date, num_months=12, end_date=dataset.end_date)

# Hospital admission costs
cost_apc_fn(dataset, from_date=dataset.index_date, num_months=1, end_date=dataset.end_date)
cost_apc_fn(dataset, from_date=dataset.index_date, num_months=2, end_date=dataset.end_date)
cost_apc_fn(dataset, from_date=dataset.index_date, num_months=3, end_date=dataset.end_date)
cost_apc_fn(dataset, from_date=dataset.index_date, num_months=4, end_date=dataset.end_date)
cost_apc_fn(dataset, from_date=dataset.index_date, num_months=5, end_date=dataset.end_date)
cost_apc_fn(dataset, from_date=dataset.index_date, num_months=6, end_date=dataset.end_date)
cost_apc_fn(dataset, from_date=dataset.index_date, num_months=7, end_date=dataset.end_date)
cost_apc_fn(dataset, from_date=dataset.index_date, num_months=8, end_date=dataset.end_date)
cost_apc_fn(dataset, from_date=dataset.index_date, num_months=9, end_date=dataset.end_date)
cost_apc_fn(dataset, from_date=dataset.index_date, num_months=10, end_date=dataset.end_date)
cost_apc_fn(dataset, from_date=dataset.index_date, num_months=11, end_date=dataset.end_date)
cost_apc_fn(dataset, from_date=dataset.index_date, num_months=12, end_date=dataset.end_date)

# A&E visit costs
cost_er_fn(dataset, from_date=dataset.index_date, num_months=1, end_date=dataset.end_date)
cost_er_fn(dataset, from_date=dataset.index_date, num_months=2, end_date=dataset.end_date)
cost_er_fn(dataset, from_date=dataset.index_date, num_months=3, end_date=dataset.end_date)
cost_er_fn(dataset, from_date=dataset.index_date, num_months=4, end_date=dataset.end_date)
cost_er_fn(dataset, from_date=dataset.index_date, num_months=5, end_date=dataset.end_date)
cost_er_fn(dataset, from_date=dataset.index_date, num_months=6, end_date=dataset.end_date)
cost_er_fn(dataset, from_date=dataset.index_date, num_months=7, end_date=dataset.end_date)
cost_er_fn(dataset, from_date=dataset.index_date, num_months=8, end_date=dataset.end_date)
cost_er_fn(dataset, from_date=dataset.index_date, num_months=9, end_date=dataset.end_date)
cost_er_fn(dataset, from_date=dataset.index_date, num_months=10, end_date=dataset.end_date)
cost_er_fn(dataset, from_date=dataset.index_date, num_months=11, end_date=dataset.end_date)
cost_er_fn(dataset, from_date=dataset.index_date, num_months=12, end_date=dataset.end_date)

# Outpatient costs
cost_opa_fn(dataset, from_date=dataset.index_date, num_months=1, end_date=dataset.end_date)
cost_opa_fn(dataset, from_date=dataset.index_date, num_months=2, end_date=dataset.end_date)
cost_opa_fn(dataset, from_date=dataset.index_date, num_months=3, end_date=dataset.end_date)
cost_opa_fn(dataset, from_date=dataset.index_date, num_months=4, end_date=dataset.end_date)
cost_opa_fn(dataset, from_date=dataset.index_date, num_months=5, end_date=dataset.end_date)
cost_opa_fn(dataset, from_date=dataset.index_date, num_months=6, end_date=dataset.end_date)
cost_opa_fn(dataset, from_date=dataset.index_date, num_months=7, end_date=dataset.end_date)
cost_opa_fn(dataset, from_date=dataset.index_date, num_months=8, end_date=dataset.end_date)
cost_opa_fn(dataset, from_date=dataset.index_date, num_months=9, end_date=dataset.end_date)
cost_opa_fn(dataset, from_date=dataset.index_date, num_months=10, end_date=dataset.end_date)
cost_opa_fn(dataset, from_date=dataset.index_date, num_months=11, end_date=dataset.end_date)
cost_opa_fn(dataset, from_date=dataset.index_date, num_months=12, end_date=dataset.end_date)

dataset.configure_dummy_data(population_size=30000)
