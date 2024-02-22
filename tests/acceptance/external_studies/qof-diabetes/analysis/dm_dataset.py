from ehrql import (
    create_dataset,
    years,
    months,
    days,
)
from ehrql.tables.tpp import (
    clinical_events,
    patients,
    practice_registrations,
)

# Diabetes mellitus variable library
# Business Rules for Quality and Outcomes Framework (QOF) 2021/22 (Version 46)
# Clinical data extraction criteria
from variable_lib_helper import (
    first_matching_event,
    last_matching_event,
    age_as_of,
    practice_registration_as_of,
    get_events_on_or_between,
)

import codelists


# Define a dataset including all variables needed for the diabetes mellitus (dm)
def make_dm_dataset(index_date):
    # Instantiate dataset
    dataset = create_dataset()

    # Extract prior events for further use in variable definitions below
    prior_events = clinical_events.where(
        clinical_events.date.is_on_or_before(index_date)
    )

    # Field number: 2
    # REG_DAT: The most recent date that the patient registered for GMS, where
    # this registration occurred on or before the achievement date.
    dataset.reg_dat = practice_registration_as_of(index_date).start_date

    # Field number: 3
    # REG_DAT: The first occurrence of the patient deregistering from GMS
    # following the latest GMS registration.
    dataset.dereg_dat = practice_registration_as_of(dataset.reg_dat).end_date

    # Field number: 4
    # PAT_AGE: The age of the patient in full years at the achievement date.
    dataset.pat_age = age_as_of(index_date)

    # Field number: 5
    # DM_DAT: Date of the first diabetes diagnosis up to and including the
    # achievement date.
    dataset.dm_dat = first_matching_event(prior_events, codelists.dm_cod).date

    # Field number: 6
    # DMLAT_DAT: Date of the most recent diabetes diagnosis up to and
    # including the achievement date.
    dataset.dmlat_dat = last_matching_event(prior_events, codelists.dm_cod).date

    # Field number: 7
    # DMRES_DAT: Date of the most recent diabetes diagnosis resolved code
    # recorded after the most recent diabetes diagnosis and up to and
    # including the achievement date.
    dataset.dmres_dat = last_matching_event(prior_events, codelists.dmres_cod).date

    # Field number: 8
    # DMMAX_DAT: Date of the most recent maximum tolerated diabetes treatment
    # code up to and including the achievement date.
    dataset.dmmax_dat = last_matching_event(prior_events, codelists.dmmax_cod).date

    # Field number: 9
    # IFCCHBA_DAT: Date of the most recent IFCC HbA1c monitoring range code up
    # to and including the achievement date.
    dataset.ifcchba_dat = last_matching_event(prior_events, codelists.ifcchbam_cod).date

    # Field number: 10
    # IFCCHBA_VAL: The IFCC HbA1c value associated with the most recent IFCC
    # HbA1c monitoring range recording.
    dataset.ifcchba_val = last_matching_event(
        prior_events, codelists.ifcchbam_cod
    ).numeric_value

    # Field number: 11
    # SERFRUC_DAT: Date of the most recent serum fructosamine code recorded up
    # to and including the achievement date.
    dataset.serfruc_dat = last_matching_event(prior_events, codelists.serfruc_cod).date

    # Field number: 35
    # BLDTESTDEC_DAT: Date the patient most recently chose not to receive a
    # blood test up to and including the achievement date.
    dataset.bldtestdec_dat = last_matching_event(
        prior_events, codelists.bldtestdec_cod
    ).date

    # Field number: 43
    # DMINVITE1_DAT: Date of the earliest invitation for a diabetes review on
    # or after the quality service start date and up to and including the
    # achievement date.
    dminvite_events = get_events_on_or_between(
        clinical_events,
        codelists.dminvite_cod,
        index_date - years(1),
        index_date,
    )
    dataset.dminvite1_dat = (
        dminvite_events.sort_by(dminvite_events.date).first_for_patient().date
    )

    # Field number: 44
    # DMINVITE2_DAT: Date of the earliest invitation for a diabetes review
    # recorded at least 7 days after the first invitation and up to and
    # including the achievement date.
    dminvite2_events = dminvite_events.where(
        dminvite_events.date.is_after(dataset.dminvite1_dat + days(7))
    )
    dataset.dminvite2_dat = (
        dminvite2_events.sort_by(dminvite2_events.date).first_for_patient().date
    )

    # Field number: 45
    # DMPCADEC_DAT: Date the patient most recently chose not to receive
    # diabetes quality indicator care up to and including the achievement date.
    dataset.dmpcadec_dat = last_matching_event(
        prior_events, codelists.dmpcadec_cod
    ).date

    # Field number: 46
    # DMPCAPU_DAT: Most recent date that diabetes quality indicator care was
    # deemed unsuitable for the patient up to and including the achievement
    # date.
    dataset.dmpcapu_dat = last_matching_event(prior_events, codelists.dmpcapu_cod).date

    # Field number: 55
    # MODFRAIL_DAT: Date of the most recent moderate frailty diagnosis up to and
    # including the achievement date.
    dataset.modfrail_dat = last_matching_event(
        prior_events, codelists.modfrail_cod
    ).date

    # Field number: 59
    # SEVFRAIL_DAT: Date of the most recent severe frailty diagnosis up to and
    # including the achievement date.
    dataset.sevfrail_dat = last_matching_event(
        prior_events, codelists.sevfrail_cod
    ).date

    # Field number: 66
    # FRAILLAT_DAT: The date of the latest frailty diagnosis up to and
    # including the achievement date.
    mildmodsev_frail_cod = (
        codelists.mildfrail_cod + codelists.modfrail_cod + codelists.sevfrail_cod
    )
    dataset.fraillat_dat = last_matching_event(prior_events, mildmodsev_frail_cod).date

    return dataset


# GMS reg status: Select patients who meet either of the criteria below:
# Registered for GMS prior to or on the achievement date and did not
# subsequently deregister from GMS (currently registered for GMS).
# Registered for GMS prior to or on the achievement date and subsequently
# deregistered from GMS after the achievement date (previously registered for
# GMS). (i.e. patients who were registered for GMS on the achievement date).
# TODO Note that this currently does not follow the qualifying criteria in
# the business rules for get_gms_registration_status. We do not check
# whether a practice has signed up for GMS. This is reflected in the
# current function name get_registration_status.
def get_registration_status(index_date):
    return practice_registration_as_of(index_date).exists_for_patient()


# DM REGISTER (DM_REG)
# DM_REG rule 1:
# Pass to the next rule all patients from the specified population who meet
# both of the criteria below:  Have a diabetes diagnosis in the patient record
# up to and including the achievement date. Latest diabetes diagnosis is not
# followed by a diabetes resolved code.
def get_dm_reg_r1(dataset):
    return (dataset.dmres_dat < dataset.dmlat_dat) | (
        dataset.dmlat_dat.is_not_null() & dataset.dmres_dat.is_null()
    )


# DM_REG rule 2:
# Reject patients passed to this rule who are aged under 17 years old on the
# achievement date.
def get_dm_reg_r2(dataset):
    return dataset.pat_age < 17


# INDICATORS DM020 and DM021
# DM020 (DM021) rule 1: Reject patients from the specified population whose
# latest frailty diagnosis is moderate or severe. Pass all remaining patients
# to the next rule.
def get_dm020_r1(dataset):
    return (dataset.fraillat_dat == dataset.sevfrail_dat) | (
        dataset.fraillat_dat == dataset.modfrail_dat
    )


# DM020 (DM021) rule 2: Select patients passed to this rule who meet both of
# the criteria below:
# - Have their latest IFCC-HbA1c of 58 (75) mmol/mol or less.
# - Have their latest IFCC-HbA1c reading was recorded in the 12 months leading
# up to and including the payment period end date.
def get_dm020_r2(dataset, index_date, ifcchba_cutoff_val):
    return (
        dataset.ifcchba_val.is_not_null()
        & (dataset.ifcchba_val <= ifcchba_cutoff_val)
        & dataset.ifcchba_dat.is_on_or_between(index_date - years(1), index_date)
    )


# DM020 (DM021) rule 3: Reject patients passed to this rule who did not have
# their IFCC-HbA1c recorded during the current service year but did have serum
# fructosamine recorded during the service year. Pass all remaining patients
# to the next rule.
def get_dm020_r3(dataset, index_date):
    return (
        (
            dataset.ifcchba_dat.is_null()
            | dataset.ifcchba_dat.is_on_or_before(index_date - years(1))
        )
        & dataset.serfruc_dat.is_not_null()
        & dataset.serfruc_dat.is_after(index_date - years(1))
    )


# DM020 (DM021) rule 4: Reject patients passed to this rule who are on maximum
# tolerated diabetes treatment in the 12 months leading up to and including
# the payment period end date. Pass all remaining patients to the next rule.
def get_dm020_r4(dataset, index_date):
    return dataset.dmmax_dat.is_not_null() & dataset.dmmax_dat.is_after(
        index_date - years(1)
    )


# DM020 (DM021) rule 5: Reject patients passed to this rule for whom diabetes
# quality indicator care was unsuitable in the 12 months leading up to and
# including the payment period end date. Pass all remaining patients to the
# next rule.
def get_dm020_r5(dataset, index_date):
    return dataset.dmpcapu_dat.is_not_null() & dataset.dmpcapu_dat.is_after(
        index_date - years(1)
    )


# DM020 (DM021) rule 6: Reject patients passed to this rule who chose not to
# receive a blood test in the 12 months leading up to and including the payment
# period end date. Pass all remaining patients to the next rule.
def get_dm020_r6(dataset, index_date):
    return dataset.bldtestdec_dat.is_not_null() & dataset.bldtestdec_dat.is_after(
        index_date - years(1)
    )


# DM020 (DM021) rule 7: Reject patients passed to this rule who chose not to
# receive diabetes quality indicator care in the 12 months leading up to and
# including the payment period end date. Pass all remaining patients to the
# next rule.
def get_dm020_r7(dataset, index_date):
    return dataset.dmpcadec_dat.is_not_null() & dataset.dmpcadec_dat.is_after(
        index_date - years(1)
    )


# DM020 (DM021) rule 8: Reject patients passed to this rule who meet either of
# the criteria below:
# - Latest IFCC-HbA1c recorded in the 12 months leading up to and including the
# payment period end date was above target levels (IFCC-HbA1c was above 58 (75)
# mmol/mol), and was followed by two invitations for diabetes monitoring.
# - Received two invitations for diabetes monitoring and had no IFCC-HbA1c
# recorded during the 12 months leading up to and including the achievement
# date.
def get_dm020_r8(dataset, index_date, ifcchba_cutoff_val):
    return (
        dataset.ifcchba_val.is_not_null()
        & (dataset.ifcchba_val > ifcchba_cutoff_val)
        & dataset.ifcchba_dat.is_not_null()
        & dataset.ifcchba_dat.is_on_or_between(index_date - years(1), index_date)
        & (dataset.dminvite1_dat > dataset.ifcchba_dat)
        & dataset.dminvite2_dat.is_not_null()
    ) | (
        (dataset.dminvite2_dat.is_not_null() & dataset.ifcchba_dat.is_null())
        | dataset.ifcchba_dat.is_on_or_before(index_date - years(1))
    )


# DM020 (DM021) rule 9: Reject patients passed to this rule whose diabetes
# diagnosis was in the 9 months leading up to and including the payment period
# end date.
def get_dm020_r9(dataset, index_date):
    return dataset.dm_dat.is_not_null() & dataset.dm_dat.is_after(
        index_date - months(9)
    )


# DM020 (DM021) rule 10: Reject patients passed to this rule who registered
# with the practice in the 9 months leading up to and including the payment
# period end date. Select the remaining patients.
def get_dm020_r10(dataset, index_date):
    return dataset.reg_dat.is_not_null() & dataset.reg_dat.is_after(
        index_date - months(9)
    )


# Copy identical rules
get_dm021_r1 = get_dm020_r1
get_dm021_r2 = get_dm020_r2
get_dm021_r3 = get_dm020_r3
get_dm021_r4 = get_dm020_r4
get_dm021_r5 = get_dm020_r5
get_dm021_r6 = get_dm020_r6
get_dm021_r7 = get_dm020_r7
get_dm021_r8 = get_dm020_r8
get_dm021_r9 = get_dm020_r9
get_dm021_r10 = get_dm020_r10
