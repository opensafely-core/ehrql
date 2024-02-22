###########################################################
# This script creates weekly opioid prescribing rates
#   in the 6 months pre-waiting list, during waiting list and 
#   6 months post-waiting list for people with a completed RTT pathway
#   for orthopaedic surgery only
###########################################################

from ehrql import INTERVAL, create_measures, weeks, days, minimum_of, years, when, case
from ehrql.tables.tpp import (
    patients, 
    practice_registrations,
    medications,
    clinical_events,
    addresses,
    wl_clockstops)

import codelists


##########

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--codelist")

args = parser.parse_args()

codelist_name = args.codelist
codelist = getattr(codelists, codelist_name)

##########


# WL data - exclude rows with missing dates/dates outside study period/end date before start date
last_clockstops = wl_clockstops.where(
        wl_clockstops.referral_to_treatment_period_end_date.is_on_or_between("2021-05-01", "2022-04-30")
        & wl_clockstops.referral_to_treatment_period_start_date.is_on_or_before(wl_clockstops.referral_to_treatment_period_end_date)
        & wl_clockstops.week_ending_date.is_on_or_between("2021-05-01", "2022-04-30")
        & wl_clockstops.waiting_list_type.is_in(["IRTT","ORTT","PTLO","PTLI","PLTI","RTTO","RTTI","PTL0","PTL1"])
    ).sort_by(
        wl_clockstops.referral_to_treatment_period_start_date,
        wl_clockstops.pseudo_referral_identifier,
        wl_clockstops.pseudo_patient_pathway_identifier,
        wl_clockstops.pseudo_organisation_code_patient_pathway_identifier_issuer
    ).last_for_patient()

routine = case(
    when(last_clockstops.priority_type_code == "routine").then("Routine"),
    when(last_clockstops.priority_type_code == "urgent").then("Urgent"),
    when(last_clockstops.priority_type_code == "two week wait").then("Urgent"),
    otherwise="Missing",
    )

admitted = (last_clockstops.waiting_list_type.is_in(["IRTT","PTLI","PLTI","RTTI","PTL1"]))


# RTT waiting list start date and end date
rtt_start_date = last_clockstops.referral_to_treatment_period_start_date
rtt_end_date = last_clockstops.referral_to_treatment_period_end_date


# Set artificial start/end date for running Measures
#   this is to standardise dates, as every person's 
#   start is different (and Measures works on calendar dates only)
tmp_date = "2000-01-01"

# All opioid prescriptions during study period
all_opioid_rx = medications.where(
                medications.dmd_code.is_in(codelists.opioid_codes)
                & medications.date.is_on_or_between(rtt_start_date - days(365), rtt_end_date + days(182))
            )

# Standardise Rx dates relative to RTT start date for prescribing during WL 
all_opioid_rx.tmp_wait_date = tmp_date + days((all_opioid_rx.date - rtt_start_date).days)

# Standardise Rx dates relative to RTT end date for post-WL prescribing
all_opioid_rx.tmp_post_date = tmp_date + days((all_opioid_rx.date - (rtt_end_date + days(1))).days)

# Standardise Rx dates relative to RTT start date for pre-WL prescribing 
all_opioid_rx.tmp_pre_date = tmp_date + days((all_opioid_rx.date - (rtt_start_date - days(182))).days)

### Prescribing variables for numerator ####

# Num Rx during waiting list (up to 1 year)
count_opioid_wait = all_opioid_rx.where(
                all_opioid_rx.dmd_code.is_in(codelist)
                & all_opioid_rx.tmp_wait_date.is_during(INTERVAL)
            ).count_for_patient()

# Num Rx post waiting list (up to 6 months)
count_opioid_post = all_opioid_rx.where(
                all_opioid_rx.dmd_code.is_in(codelist)
                & all_opioid_rx.tmp_post_date.is_during(INTERVAL)
            ).count_for_patient()

# Num Rx pre waiting list (up to 6 months)
count_opioid_pre = all_opioid_rx.where(
                all_opioid_rx.dmd_code.is_in(codelist)
                & all_opioid_rx.tmp_pre_date.is_during(INTERVAL)
            ).count_for_patient()


## Censoring date
registrations = practice_registrations.where(
        practice_registrations.start_date.is_on_or_before(rtt_start_date - days(182))
        & (practice_registrations.end_date.is_after(rtt_start_date) | practice_registrations.end_date.is_null())
    )

reg_end_date = registrations.sort_by(registrations.end_date).last_for_patient().end_date
end_date = minimum_of(reg_end_date, patients.date_of_death, rtt_end_date + days(182))

# Standardise end date relative to RTT start and end dates
tmp_end_date_rtt_start = tmp_date + days((end_date - rtt_start_date).days)
tmp_end_date_rtt_end = tmp_date + days((end_date - rtt_end_date).days)

# Standardise RTT end date to RTT start date
tmp_rtt_end = tmp_date + days((rtt_end_date - rtt_start_date).days)


## Cancer diagnosis in past 5 years 
cancer = clinical_events.where(
        clinical_events.snomedct_code.is_in(codelists.cancer_codes)
    ).where(
        clinical_events.date.is_on_or_between(rtt_start_date - years(5), rtt_start_date)
    ).exists_for_patient()


### Grouping/stratification variables (Final list TBD) ###
prior_opioid_count = all_opioid_rx.where(
        all_opioid_rx.date.is_on_or_between(rtt_start_date - days(182), rtt_start_date - days(1))
    ).count_for_patient()

prior_opioid_rx = (prior_opioid_count >= 3)


# Demographics
age = patients.age_on(rtt_start_date)
# age_group = case(
#         when(age < 40).then("18-39"),
#         when(age < 50).then("40-49"),
#         when(age < 60).then("50-59"),
#         when(age < 70).then("60-69"),
#         when(age < 80).then("70-79"),
#         when(age >= 80).then("80+"),
#         otherwise="Missing",
# )

sex = patients.sex

# # IMD decile
# imd = addresses.for_patient_on(rtt_start_date).imd_rounded
# imd10 = case(
#         when((imd >= 0) & (imd < int(32844 * 1 / 10))).then("1 (most deprived)"),
#         when(imd < int(32844 * 2 / 10)).then("2"),
#         when(imd < int(32844 * 3 / 10)).then("3"),
#         when(imd < int(32844 * 4 / 10)).then("4"),
#         when(imd < int(32844 * 5 / 10)).then("5"),
#         when(imd < int(32844 * 6 / 10)).then("6"),
#         when(imd < int(32844 * 7 / 10)).then("7"),
#         when(imd < int(32844 * 8 / 10)).then("8"),
#         when(imd < int(32844 * 9 / 10)).then("9"),
#         when(imd >= int(32844 * 9 / 10)).then("10 (least deprived)"),
#         otherwise="Unknown"
# )

# # IMD quintile
# imd5 = case(
#         when((imd >= 0) & (imd < int(32844 * 1 / 5))).then("1 (most deprived)"),
#         when(imd < int(32844 * 2 / 5)).then("2"),
#         when(imd < int(32844 * 3 / 5)).then("3"),
#         when(imd < int(32844 * 4 / 5)).then("4"),
#         when(imd >= int(32844 * 4 / 5)).then("5 (least deprived)"),
#         otherwise="Unknown"
# )


######


measures = create_measures()


# Denominator 
denominator = (        
        # Adults with non-missing age/sex
        (age >= 18) 
        & (age < 110)
        & (sex.is_in(["male","female"]))

        # Registered for >6 months
        & registrations.exists_for_patient()

        # Orthopaedic surgery codes
        & last_clockstops.activity_treatment_function_code.is_in(["110","111"]) 

        # No cancer
        & ~cancer

        # Censoring date (death/deregistration) after start of waiting list
        & (end_date >= rtt_start_date)

        # Routine priority type
        & routine.is_in(["Routine"])

        # Admitted
        & admitted
    )



# Prescribing during WL
measures.define_measure(
    name="count_wait",
    numerator=count_opioid_wait,
    # Denominator = only include people whose RTT end date and study end date are after interval end date
    #   IOW, exclude people who are no longer on waiting list or have been censored
    denominator=denominator & (tmp_end_date_rtt_start > INTERVAL.end_date) & (tmp_rtt_end > INTERVAL.end_date),
    intervals=weeks(52).starting_on("2000-01-01")
    )

# Prescribing post WL
measures.define_measure(
    name="count_post",
    numerator=count_opioid_post,
    # Denominator = only include people whose RTT end date is after interval end date
    #   IOW, exclude people who have been censored
    denominator=denominator & (tmp_end_date_rtt_end > INTERVAL.end_date),
    intervals=weeks(26).starting_on("2000-01-01")
    )

# Prescribing pre WL
measures.define_measure(
    name="count_pre",
    numerator=count_opioid_pre,
    # Denominator = only include people whose RTT end date is after interval end date
    #   IOW, exclude people who have been censored
    denominator=denominator,
    intervals=weeks(26).starting_on("2000-01-01")
    )


##### By prior opioid prescribing #####

# Prescribing pre WL - stratified by prior opioid Rx
measures.define_measure(
    name="count_pre_prior",
    numerator=count_opioid_pre,
    denominator=denominator,
    intervals=weeks(26).starting_on("2000-01-01"),
    group_by={"prior_opioid_rx": prior_opioid_rx}
    )

# Prescribing during WL - stratified by prior opioid Rx
measures.define_measure(
    name="count_wait_prior",
    numerator=count_opioid_wait,
    denominator=denominator & (tmp_end_date_rtt_start > INTERVAL.end_date) & (tmp_rtt_end > INTERVAL.end_date),
    intervals=weeks(52).starting_on("2000-01-01"),
    group_by={"prior_opioid_rx": prior_opioid_rx}
    )

# Prescribing post WL - stratified by prior opioid Rx
measures.define_measure(
    name="count_post_prior",
    numerator=count_opioid_post,
    denominator=denominator & (tmp_end_date_rtt_end > INTERVAL.end_date),
    intervals=weeks(26).starting_on("2000-01-01"),
    group_by={"prior_opioid_rx": prior_opioid_rx}
    )
