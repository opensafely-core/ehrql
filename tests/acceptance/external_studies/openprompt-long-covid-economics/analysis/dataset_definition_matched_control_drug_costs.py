import datetime
from ehrql import Dataset, days, years
from ehrql.tables.beta.tpp import (
    patients, addresses, ons_deaths, sgss_covid_all_tests,
    practice_registrations, clinical_events,
    vaccinations,
)
from ehrql.query_language import table_from_file, PatientFrame, Series
from covariates import *
from variables import *
from ehrql import minimum_of
# Import matched data

@table_from_file("output/matched_matches_stp.csv")
class matched_matches(PatientFrame):
    age = Series(int)
    sex = Series(str)
    region = Series(str)
    registration_date = Series(date)
    long_covid_dx = Series(int)
    long_covid_dx_date= Series(date)
    end_death = Series(date)
    end_deregist = Series(date)
    end_lc_cure = Series(date)
    set_id = Series(int)
    exposure = Series(int)
    index_date = Series(date)


# Define dataset variables

dataset = Dataset()
dataset.define_population(
    (age >= 18)
    & matched_matches.exists_for_patient()
)
dataset.age = matched_matches.age
dataset.sex = matched_matches.sex
dataset.index_date = matched_matches.index_date
dataset.end_death = matched_matches.end_death
dataset.end_deregist = matched_matches.end_deregist
dataset.end_lc_cure = matched_matches.end_lc_cure
dataset.end_date = minimum_of(dataset.end_death, dataset.end_deregist, dataset.end_lc_cure, study_end_date)
dataset.exposure = matched_matches.exposure

# Add visits for any prescriptions:
total_drug_visit(dataset, dataset.index_date, end_date=dataset.end_date)

# Add drug prescription frequencies by BNF chapters 
# drugs: bnf ch1 : gi drugs
drug_1gi_number(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
drug_1gi_number(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
drug_1gi_number(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
drug_1gi_number(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
drug_1gi_number(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
drug_1gi_number(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
drug_1gi_number(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
drug_1gi_number(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
drug_1gi_number(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
drug_1gi_number(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
drug_1gi_number(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
drug_1gi_number(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)

# drugs: bnf ch2: cv drugs
drug_2cv_number(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
drug_2cv_number(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
drug_2cv_number(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
drug_2cv_number(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
drug_2cv_number(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
drug_2cv_number(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
drug_2cv_number(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
drug_2cv_number(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
drug_2cv_number(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
drug_2cv_number(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
drug_2cv_number(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
drug_2cv_number(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)


# drugs: bnf ch3 chest drugs
drug_3chest_number(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
drug_3chest_number(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
drug_3chest_number(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
drug_3chest_number(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
drug_3chest_number(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
drug_3chest_number(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
drug_3chest_number(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
drug_3chest_number(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
drug_3chest_number(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
drug_3chest_number(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
drug_3chest_number(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
drug_3chest_number(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)


# drugs: bnf ch4: cns
drug_4cns_number(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
drug_4cns_number(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
drug_4cns_number(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
drug_4cns_number(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
drug_4cns_number(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
drug_4cns_number(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
drug_4cns_number(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
drug_4cns_number(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
drug_4cns_number(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
drug_4cns_number(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
drug_4cns_number(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
drug_4cns_number(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)


# drugs: bnf ch5: infectious
drug_5inf_number(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
drug_5inf_number(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
drug_5inf_number(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
drug_5inf_number(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
drug_5inf_number(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
drug_5inf_number(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
drug_5inf_number(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
drug_5inf_number(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
drug_5inf_number(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
drug_5inf_number(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
drug_5inf_number(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
drug_5inf_number(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)


# drugs: bnf ch6: metabolism drugs
drug_6meta_number(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
drug_6meta_number(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
drug_6meta_number(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
drug_6meta_number(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
drug_6meta_number(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
drug_6meta_number(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
drug_6meta_number(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
drug_6meta_number(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
drug_6meta_number(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
drug_6meta_number(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
drug_6meta_number(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
drug_6meta_number(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)


# drugs: bnf ch7 GYN drugs
drug_7gyn_number(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
drug_7gyn_number(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
drug_7gyn_number(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
drug_7gyn_number(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
drug_7gyn_number(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
drug_7gyn_number(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
drug_7gyn_number(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
drug_7gyn_number(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
drug_7gyn_number(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
drug_7gyn_number(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
drug_7gyn_number(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
drug_7gyn_number(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)


# drugs: bnf ch8 cancer drugs
drug_8cancer_number(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
drug_8cancer_number(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
drug_8cancer_number(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
drug_8cancer_number(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
drug_8cancer_number(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
drug_8cancer_number(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
drug_8cancer_number(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
drug_8cancer_number(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
drug_8cancer_number(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
drug_8cancer_number(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
drug_8cancer_number(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
drug_8cancer_number(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)


# drugs: bnf ch9 nutrition
drug_9diet_number(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
drug_9diet_number(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
drug_9diet_number(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
drug_9diet_number(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
drug_9diet_number(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
drug_9diet_number(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
drug_9diet_number(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
drug_9diet_number(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
drug_9diet_number(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
drug_9diet_number(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
drug_9diet_number(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
drug_9diet_number(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)


# drugs: bnf ch10 muscle
drug_10muscle_number(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
drug_10muscle_number(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
drug_10muscle_number(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
drug_10muscle_number(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
drug_10muscle_number(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
drug_10muscle_number(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
drug_10muscle_number(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
drug_10muscle_number(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
drug_10muscle_number(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
drug_10muscle_number(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
drug_10muscle_number(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
drug_10muscle_number(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)

# drugs: bnf ch11 eyes
drug_11eye_number(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
drug_11eye_number(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
drug_11eye_number(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
drug_11eye_number(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
drug_11eye_number(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
drug_11eye_number(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
drug_11eye_number(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
drug_11eye_number(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
drug_11eye_number(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
drug_11eye_number(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
drug_11eye_number(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
drug_11eye_number(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)


# drugs: bnf ch12 ent
drug_12ent_number(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
drug_12ent_number(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
drug_12ent_number(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
drug_12ent_number(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
drug_12ent_number(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
drug_12ent_number(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
drug_12ent_number(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
drug_12ent_number(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
drug_12ent_number(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
drug_12ent_number(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
drug_12ent_number(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
drug_12ent_number(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)


# drugs: bnf ch13 skin
drug_13skin_number(dataset, dataset.index_date, num_months=1, end_date=dataset.end_date)
drug_13skin_number(dataset, dataset.index_date, num_months=2, end_date=dataset.end_date)
drug_13skin_number(dataset, dataset.index_date, num_months=3, end_date=dataset.end_date)
drug_13skin_number(dataset, dataset.index_date, num_months=4, end_date=dataset.end_date)
drug_13skin_number(dataset, dataset.index_date, num_months=5, end_date=dataset.end_date)
drug_13skin_number(dataset, dataset.index_date, num_months=6, end_date=dataset.end_date)
drug_13skin_number(dataset, dataset.index_date, num_months=7, end_date=dataset.end_date)
drug_13skin_number(dataset, dataset.index_date, num_months=8, end_date=dataset.end_date)
drug_13skin_number(dataset, dataset.index_date, num_months=9, end_date=dataset.end_date)
drug_13skin_number(dataset, dataset.index_date, num_months=10, end_date=dataset.end_date)
drug_13skin_number(dataset, dataset.index_date, num_months=11, end_date=dataset.end_date)
drug_13skin_number(dataset, dataset.index_date, num_months=12, end_date=dataset.end_date)

dataset.configure_dummy_data(population_size=30000)
