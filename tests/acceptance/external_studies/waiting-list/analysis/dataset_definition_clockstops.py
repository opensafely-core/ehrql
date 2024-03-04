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
        & wl_clockstops.referral_to_treatment_period_start_date.is_on_or_before(wl_clockstops.referral_to_treatment_period_end_date)
        & wl_clockstops.week_ending_date.is_on_or_between("2021-05-01", "2022-04-30")
        & wl_clockstops.waiting_list_type.is_in(["IRTT","ORTT","PTLO","PTLI","RTTO","RTTI"])
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

# RTT waiting list start date and end date
dataset.rtt_start_date = last_clockstops.referral_to_treatment_period_start_date
dataset.rtt_end_date = last_clockstops.referral_to_treatment_period_end_date
dataset.wait_time = (dataset.rtt_end_date - dataset.rtt_start_date).days

# Other relevant columns
dataset.treatment_function = last_clockstops.activity_treatment_function_code
dataset.waiting_list_type = last_clockstops.waiting_list_type
dataset.priority_type = last_clockstops.priority_type_code
dataset.admitted = (last_clockstops.waiting_list_type.is_in(["IRTT","PTLI","RTTI"]))
dataset.ortho_surgery = (last_clockstops.activity_treatment_function_code.is_in(["110","111"]))

#### Censoring dates ####

# Registered 6 months before WL start
registrations = practice_registrations.where(
        practice_registrations.start_date.is_on_or_before(dataset.rtt_start_date - days(182))
    ).for_patient_on(dataset.rtt_start_date)

dataset.reg_end_date = registrations.end_date
dataset.dod = patients.date_of_death
dataset.end_date = minimum_of(dataset.reg_end_date, dataset.dod, dataset.rtt_end_date + days(182))

# Flag if censored before WL end date
dataset.censor_before_rtt_end = (dataset.end_date < dataset.rtt_end_date)

# Flag if censored before study end date (RTT end + 6 months)
dataset.censor_before_study_end = (dataset.end_date < dataset.rtt_end_date + days(182))


#### Medicines data ####

med_codes = {
    "opioid": codelists.opioid_codes,
    # "lo_opioid": codelists.lo_opioid_codes,
    # "med_opioid": codelists.med_opioid_codes,
    # "hi_opioid": codelists.hi_opioid_codes,
    "gabapentinoid": codelists.gabapentinoid_codes,
    "antidepressant": codelists.antidepressant_codes,
    "tca": codelists.tca_codes,
    "nsaid": codelists.nsaid_codes,
    "weak_opioid": codelists.weak_opioid_codes,
    "strong_opioid": codelists.strong_opioid_codes,
    "long_opioid": codelists.long_opioid_codes,
    "short_opioid": codelists.short_opioid_codes,
    }

for med, med_codelist in med_codes.items():

    med_events = medications.where(medications.dmd_code.is_in(med_codelist))

    # Number of prescriptions during waiting list (this time period is variable, will account for this later)
    wait_count_query = med_events.where(
            med_events.date.is_on_or_between(dataset.rtt_start_date, minimum_of(dataset.end_date, dataset.rtt_end_date))
        ).count_for_patient()
    dataset.add_column(f"{med}_wait_count", wait_count_query)

    # Any prescription during waiting list (this time period is variable, will account for this later)
    wait_any_query = med_events.where(
            med_events.date.is_on_or_between(dataset.rtt_start_date, minimum_of(dataset.end_date, dataset.rtt_end_date))
        ).exists_for_patient()
    dataset.add_column(f"{med}_wait_any", wait_any_query)


    # Number of prescriptions before waiting list
    pre_count_query = med_events.where(
            med_events.date.is_on_or_between(dataset.rtt_start_date - days(182), dataset.rtt_start_date - days(1))
        ).count_for_patient()
    dataset.add_column(f"{med}_pre_count", pre_count_query)
    
    # Any prescription before waiting list
    pre_any_query = med_events.where(
            med_events.date.is_on_or_between(dataset.rtt_start_date - days(182), dataset.rtt_start_date - days(1))
        ).exists_for_patient()
    dataset.add_column(f"{med}_pre_any", pre_any_query)


    # Number of prescriptions after waiting list
    post_count_query = med_events.where(
            med_events.date.is_on_or_between(dataset.rtt_end_date + days(1), minimum_of(dataset.rtt_end_date + days(182), dataset.end_date))
            & (dataset.end_date > dataset.rtt_end_date)
        ).count_for_patient()
    dataset.add_column(f"{med}_post_count", post_count_query)
    
    # Any prescription after waiting list
    post_any_query = med_events.where(
            med_events.date.is_on_or_between(dataset.rtt_end_date + days(1), minimum_of(dataset.rtt_end_date + days(182), dataset.end_date))
            & (dataset.end_date > dataset.rtt_end_date)
        ).exists_for_patient()
    dataset.add_column(f"{med}_post_any", post_any_query)


# Date of first prescription
dataset.first_opioid_date = med_events.where(
            med_events.dmd_code.is_in(codelists.opioid_codes)
            & med_events.date.is_on_or_between(dataset.rtt_start_date - days(365), minimum_of(dataset.end_date, dataset.rtt_end_date + days(182)))
        ).sort_by(
            med_events.date
        ).first_for_patient().date



#### Demographics ####

dataset.age = patients.age_on(dataset.rtt_start_date)
dataset.age_group = case(
        when(dataset.age < 40).then("18-39"),
        when(dataset.age < 50).then("40-49"),
        when(dataset.age < 60).then("50-59"),
        when(dataset.age < 70).then("60-69"),
        when(dataset.age < 80).then("70-79"),
        when(dataset.age >= 80).then("80+"),
        otherwise="Missing",
)
dataset.sex = patients.sex

# IMD decile
imd = addresses.for_patient_on(dataset.rtt_start_date).imd_rounded
dataset.imd10 = case(
        when((imd >= 0) & (imd < int(32844 * 1 / 10))).then("1 (most deprived)"),
        when(imd < int(32844 * 2 / 10)).then("2"),
        when(imd < int(32844 * 3 / 10)).then("3"),
        when(imd < int(32844 * 4 / 10)).then("4"),
        when(imd < int(32844 * 5 / 10)).then("5"),
        when(imd < int(32844 * 6 / 10)).then("6"),
        when(imd < int(32844 * 7 / 10)).then("7"),
        when(imd < int(32844 * 8 / 10)).then("8"),
        when(imd < int(32844 * 9 / 10)).then("9"),
        when(imd >= int(32844 * 9 / 10)).then("10 (least deprived)"),
        otherwise="Unknown"
)

# IMD quintile
dataset.imd5 = case(
        when((imd >= 0) & (imd < int(32844 * 1 / 5))).then("1 (most deprived)"),
        when(imd < int(32844 * 2 / 5)).then("2"),
        when(imd < int(32844 * 3 / 5)).then("3"),
        when(imd < int(32844 * 4 / 5)).then("4"),
        when(imd >= int(32844 * 4 / 5)).then("5 (least deprived)"),
        otherwise="Unknown"
)

# Ethnicity 6 categories
ethnicity6 = clinical_events.where(
        clinical_events.snomedct_code.is_in(codelists.ethnicity_codes_6)
    ).where(
        clinical_events.date.is_on_or_before(dataset.rtt_start_date)
    ).sort_by(
        clinical_events.date
    ).last_for_patient().snomedct_code.to_category(codelists.ethnicity_codes_6)

dataset.ethnicity6 = case(
    when(ethnicity6 == "1").then("White"),
    when(ethnicity6 == "2").then("Mixed"),
    when(ethnicity6 == "3").then("South Asian"),
    when(ethnicity6 == "4").then("Black"),
    when(ethnicity6 == "5").then("Other"),
    when(ethnicity6 == "6").then("Not stated"),
    otherwise="Unknown"
)

# Ethnicity 16 categories
ethnicity16 = clinical_events.where(
        clinical_events.snomedct_code.is_in(codelists.ethnicity_codes_16)
    ).where(
        clinical_events.date.is_on_or_before(dataset.rtt_start_date)
    ).sort_by(
        clinical_events.date
    ).last_for_patient().snomedct_code.to_category(codelists.ethnicity_codes_16)

dataset.ethnicity16 = case(
    when(ethnicity16 == "1").then("White - British"),
    when(ethnicity16 == "2").then("White - Irish"),
    when(ethnicity16 == "3").then("White - Other"),
    when(ethnicity16 == "4").then("Mixed - White/Black Caribbean"),
    when(ethnicity16 == "5").then("Mixed - White/Black African"),
    when(ethnicity16 == "6").then("Mixed - White/Asian"),
    when(ethnicity16 == "7").then("Mixed - Other"),
    when(ethnicity16 == "8").then("Asian or Asian British - Indian"),
    when(ethnicity16 == "9").then("Asian or Asian British - Pakistani"),
    when(ethnicity16 == "10").then("Asian or Asian British - Bangladeshi"),
    when(ethnicity16 == "11").then("Asian or Asian British - Other"),
    when(ethnicity16 == "12").then("Black - Caribbean"),    
    when(ethnicity16 == "13").then("Black - African"),
    when(ethnicity16 == "14").then("Black - Other"),
    when(ethnicity16 == "15").then("Other - Chinese"),
    when(ethnicity16 == "16").then("Other - Other"),
    otherwise="Unknown"
)

dataset.region = practice_registrations.for_patient_on(dataset.rtt_start_date).practice_nuts1_region_name


#### Clinical characteristics ####

# Cancer diagnosis in past 5 years 
dataset.cancer = clinical_events.where(
        clinical_events.snomedct_code.is_in(codelists.cancer_codes)
    ).where(
        clinical_events.date.is_between_but_not_on(dataset.rtt_start_date - years(5), dataset.rtt_start_date)
    ).exists_for_patient()


# Comorbidities in past 5 years
clin_events_5yrs = clinical_events.where(
        clinical_events.date.is_on_or_between(dataset.rtt_start_date - years(5), dataset.rtt_start_date)
    )

comorb_codes = {
    "diabetes": codelists.diabetes_codes,
    "cardiac": codelists.cardiac_codes,
    "copd": codelists.copd_codes,
    "liver": codelists.liver_codes,
    "ckd": codelists.ckd_codes,
    "oa": codelists.osteoarthritis_codes,
    "ra": codelists.ra_codes,
    "depression": codelists.depression_codes,
    "anxiety": codelists.anxiety_codes,
    "smi": codelists.smi_codes,
    "oud": codelists.oud_codes
    }


for comorb, comorb_codelist in comorb_codes.items():
        
    if comorb in ["diabetes","cardiac","copd","liver","oa","ra"]:

        ctv3_query = clin_events_5yrs.where(
                clin_events_5yrs.ctv3_code.is_in(comorb_codelist)
            ).exists_for_patient()
        dataset.add_column(comorb, ctv3_query)

    else:

        snomed_query = clin_events_5yrs.where(
                clin_events_5yrs.snomedct_code.is_in(comorb_codelist)
            ).exists_for_patient()
        dataset.add_column(comorb, snomed_query)


#### DEFINE POPULATION ####

dataset.define_population(
    dataset.end_date.is_after(dataset.rtt_start_date)
    & registrations.exists_for_patient()
    & last_clockstops.exists_for_patient()
)
