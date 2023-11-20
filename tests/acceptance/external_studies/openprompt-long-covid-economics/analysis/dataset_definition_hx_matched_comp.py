import datetime
from databuilder.ehrql import Dataset, days, years
from databuilder.tables.beta.tpp import (
    patients, addresses, ons_deaths, sgss_covid_all_tests,
    practice_registrations, clinical_events,
)
from ehrql.query_language import table_from_file, PatientFrame, Series
from covariates import *

from hx_covariates import *
from variables import *
from ehrql import minimum_of
# import matched data

@table_from_file("output/matched_matches_historical.csv")
class matched_hx_comparator(PatientFrame):
    age = Series(int)
    sex = Series(str)
    lc_exp = Series(int)    
    region = Series(str)
    end_death = Series(date)
    end_deregist = Series(date)
    end_lc_cure = Series(date)    
    set_id = Series(int)
    lc_exposure = Series(int)
    index_date = Series(date)


dataset = Dataset()
dataset.define_population(
    (age >= 18)
    & matched_hx_comparator.exists_for_patient()
)

index_date = matched_hx_comparator.index_date

dataset.age = matched_hx_comparator.age
dataset.sex = matched_hx_comparator.sex
dataset.region = matched_hx_comparator.region
dataset.lc_dx = matched_hx_comparator.lc_exp
dataset.index_date = index_date 
dataset.exposure = matched_hx_comparator.lc_exposure

# Demographic covariates
dataset.ethnicity = (clinical_events.where(clinical_events.ctv3_code.is_in(codelists.ethnicity))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .ctv3_code.to_category(codelists.ethnicity)
)
dataset.imd = imd
dataset.bmi = bmi
dataset.bmi_date = bmi_date
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
dataset.end_death = matched_hx_comparator.end_death
dataset.end_deregist = matched_hx_comparator.end_deregist
dataset.end_lc_cure = matched_hx_comparator.end_lc_cure
dataset.end_date = minimum_of(dataset.end_death, dataset.end_deregist, dataset.end_lc_cure, study_end_date)
dataset.total_hx_drug_visit = total_hx_drug_visit # historical prescription visits

# Outcome visit
# Historical GP visits: 2019-3-1 to 2020-3-1
add_hx_gp_visits(dataset, num_months=1)
add_hx_gp_visits(dataset, num_months=2)
add_hx_gp_visits(dataset, num_months=3)
add_hx_gp_visits(dataset, num_months=4)
add_hx_gp_visits(dataset, num_months=5)
add_hx_gp_visits(dataset, num_months=6)
add_hx_gp_visits(dataset, num_months=7)
add_hx_gp_visits(dataset, num_months=8)
add_hx_gp_visits(dataset, num_months=9)
add_hx_gp_visits(dataset, num_months=10)
add_hx_gp_visits(dataset, num_months=11)
add_hx_gp_visits(dataset, num_months=12)


# GP visit after long COVID
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


# Hospital visits
# Historical admissions:
add_hx_hos_visits(dataset, num_months=1)
add_hx_hos_visits(dataset, num_months=2)
add_hx_hos_visits(dataset, num_months=3)
add_hx_hos_visits(dataset, num_months=4)
add_hx_hos_visits(dataset, num_months=5)
add_hx_hos_visits(dataset, num_months=6)
add_hx_hos_visits(dataset, num_months=7)
add_hx_hos_visits(dataset, num_months=8)
add_hx_hos_visits(dataset, num_months=9)
add_hx_hos_visits(dataset, num_months=10)
add_hx_hos_visits(dataset, num_months=11)
add_hx_hos_visits(dataset, num_months=12)


# Admission after index date:
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

# A&E visit
# Historical A&E visit
add_hx_ae_visits(dataset, num_months=1)
add_hx_ae_visits(dataset, num_months=2)
add_hx_ae_visits(dataset, num_months=3)
add_hx_ae_visits(dataset, num_months=4)
add_hx_ae_visits(dataset, num_months=5)
add_hx_ae_visits(dataset, num_months=6)
add_hx_ae_visits(dataset, num_months=7)
add_hx_ae_visits(dataset, num_months=8)
add_hx_ae_visits(dataset, num_months=9)
add_hx_ae_visits(dataset, num_months=10)
add_hx_ae_visits(dataset, num_months=11)
add_hx_ae_visits(dataset, num_months=12)


# A&E visit after index date:
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


# Outpatient visits
# Historical outpatient visits:
hx_outpatient_visit(dataset, num_months=1)
hx_outpatient_visit(dataset, num_months=2)
hx_outpatient_visit(dataset, num_months=3)
hx_outpatient_visit(dataset, num_months=4)
hx_outpatient_visit(dataset, num_months=5)
hx_outpatient_visit(dataset, num_months=6)
hx_outpatient_visit(dataset, num_months=7)
hx_outpatient_visit(dataset, num_months=8)
hx_outpatient_visit(dataset, num_months=9)
hx_outpatient_visit(dataset, num_months=10)
hx_outpatient_visit(dataset, num_months=11)
hx_outpatient_visit(dataset, num_months=12)


# Current outpatient visit after index date 
outpatient_visit(dataset, from_date=lc_dx.date, num_months=1, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=lc_dx.date, num_months=2, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=lc_dx.date, num_months=3, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=lc_dx.date, num_months=4, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=lc_dx.date, num_months=5, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=lc_dx.date, num_months=6, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=lc_dx.date, num_months=7, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=lc_dx.date, num_months=8, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=lc_dx.date, num_months=9, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=lc_dx.date, num_months=10, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=lc_dx.date, num_months=11, end_date=dataset.end_date)
outpatient_visit(dataset, from_date=lc_dx.date, num_months=12, end_date=dataset.end_date)


# Historical prescription visit
hx_monthly_drug_visit(dataset, 1)
hx_monthly_drug_visit(dataset, 2)
hx_monthly_drug_visit(dataset, 3)
hx_monthly_drug_visit(dataset, 4)
hx_monthly_drug_visit(dataset, 5)
hx_monthly_drug_visit(dataset, 6)
hx_monthly_drug_visit(dataset, 7)
hx_monthly_drug_visit(dataset, 8)
hx_monthly_drug_visit(dataset, 9)
hx_monthly_drug_visit(dataset, 10)
hx_monthly_drug_visit(dataset, 11)
hx_monthly_drug_visit(dataset, 12)


# Current prescription visit:
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


dataset.configure_dummy_data(population_size=10000)
