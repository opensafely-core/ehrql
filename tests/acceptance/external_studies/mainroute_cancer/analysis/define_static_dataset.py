from ehrql import case, when, years, days, minimum_of, maximum_of
from ehrql.tables.core import patients, clinical_events
from ehrql.tables.tpp import ( 
    addresses,
    practice_registrations)

import codelists

from dataset_definition import make_dataset_lowerGI

index_date = "2018-03-23"
end_date = "2023-10-22"

dataset = make_dataset_lowerGI(index_date="2018-03-23", end_date="2023-10-22")

elig_cohort = dataset.entry_date.is_on_or_before(end_date) & dataset.exit_date.is_after(index_date) & patients.date_of_birth.is_not_null()

dataset.define_population(
    elig_cohort
)

dataset.period_entry = maximum_of(index_date, dataset.entry_date)
dataset.period_exit = minimum_of(end_date, dataset.exit_date)

dataset.follow_up_years = (dataset.period_exit - dataset.period_entry).years

dataset.colorectal_ca_diag = clinical_events.where(clinical_events.snomedct_code.is_in(codelists.colorectal_diagnosis_codes_snomed)
        ).where(
            clinical_events.date.is_on_or_between(index_date, end_date)
        ).exists_for_patient()

age = patients.age_on(dataset.entry_date)
dataset.age = age
dataset.age_group = case(
        when(age < 30).then("16-29"),
        when(age < 40).then("30-39"),
        when(age < 50).then("40-49"),
        when(age < 60).then("50-59"),
        when(age < 70).then("60-69"),
        when(age < 80).then("70-79"),
        when(age < 90).then("80-89"),
        when(age >= 90).then("90+"),
        otherwise="missing",
)

dataset.sex = patients.sex

imd = addresses.for_patient_on(dataset.entry_date).imd_rounded
dataset.imd5 = case(
        when((imd >=0) & (imd < int(32844 * 1 / 5))).then("1"),
        when(imd < int(32844 * 2 / 5)).then("2"),
        when(imd < int(32844 * 3 / 5)).then("3"),
        when(imd < int(32844 * 4 / 5)).then("4"),
        when(imd < int(32844 * 5 / 5)).then("5"),
        otherwise="unknown"
)

ethnicity6 = clinical_events.where(
        clinical_events.snomedct_code.is_in(codelists.ethnicity_codes_6)
    ).where(
        clinical_events.date.is_on_or_before(dataset.entry_date)
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

dataset.region = practice_registrations.for_patient_on(dataset.entry_date).practice_nuts1_region_name
