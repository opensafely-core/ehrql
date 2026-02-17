################################################################################
# This script defines and extracts relevant variables for people with a completed
# RTT pathway from May 2021 - Apr 2022 regardless of treatment type/specialty
################################################################################


from ehrql import create_dataset, case, when, days, years, minimum_of
from ehrql.tables.tpp import (
    patients, 
    medications, 
    addresses,
    practice_registrations,
    clinical_events,
    wl_clockstops)

import codelists

dataset = create_dataset()
dataset.configure_dummy_data(population_size=10000)

#### Waiting list variables ####

# WL data - exclude rows with missing dates/dates outside study period/end date before start date
clockstops = wl_clockstops.where(
        wl_clockstops.referral_to_treatment_period_end_date.is_on_or_between("2021-05-01", "2022-04-30")
        & wl_clockstops.week_ending_date.is_on_or_between("2021-05-01", "2022-04-30")
    )

# Number of RTT pathways per person
dataset.count_rtt_rows = clockstops.count_for_patient()
dataset.count_rtt_start_date = clockstops.referral_to_treatment_period_start_date.count_distinct_for_patient()
dataset.count_patient_id = clockstops.pseudo_patient_pathway_identifier.count_distinct_for_patient()
dataset.count_organisation_id = clockstops.pseudo_organisation_code_patient_pathway_identifier_issuer.count_distinct_for_patient()
dataset.count_referral_id = clockstops.pseudo_referral_identifier.count_distinct_for_patient()


# Latest waiting list
#   Sort by IDs and start date to identify unique RTT pathways
last_clockstops = clockstops.sort_by(
        clockstops.referral_to_treatment_period_end_date,
        clockstops.referral_to_treatment_period_start_date,
        clockstops.pseudo_referral_identifier,
        clockstops.pseudo_patient_pathway_identifier,
        clockstops.pseudo_organisation_code_patient_pathway_identifier_issuer
    ).last_for_patient()

dataset.rtt_start_date = last_clockstops.referral_to_treatment_period_start_date
dataset.rtt_end_date = last_clockstops.referral_to_treatment_period_end_date


#### Censoring dates ####

# Registered 6 months before WL start
registrations = practice_registrations.spanning(
        dataset.rtt_start_date - days(182), dataset.rtt_end_date
    ).sort_by(
        practice_registrations.end_date
    ).last_for_patient()

reg_end_date = registrations.end_date
dod = patients.date_of_death
dataset.end_date = minimum_of(reg_end_date, dod, dataset.rtt_end_date + days(182))


#### Demographics ####

dataset.age = patients.age_on(dataset.rtt_start_date)
dataset.sex = patients.sex


#### DEFINE POPULATION ####

dataset.define_population(
    dataset.end_date.is_on_or_after(dataset.rtt_end_date)
    & registrations.exists_for_patient()
    & last_clockstops.exists_for_patient()
)
