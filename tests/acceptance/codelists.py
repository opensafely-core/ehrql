from pathlib import Path

from cohortextractor import codelist_from_csv, combine_codelists


def load_codelist(csv_file, system, column):
    return codelist_from_csv(
        Path(__file__).parent.parent.absolute()
        / "fixtures"
        / "long_covid_study"
        / "codelists"
        / csv_file,
        system=system,
        column=column,
    )


covid_codes = load_codelist(
    "opensafely-covid-identification.csv",
    "icd10",
    "icd10_code",
)


covid_primary_care_code = load_codelist(
    "opensafely-covid-identification-in-primary-care-probable-covid-clinical-code.csv",
    "ctv3",
    "CTV3ID",
)


covid_primary_care_positive_test = load_codelist(
    "opensafely-covid-identification-in-primary-care-probable-covid-positive-test.csv",
    "ctv3",
    "CTV3ID",
)


covid_primary_care_sequalae = load_codelist(
    "opensafely-covid-identification-in-primary-care-probable-covid-sequelae.csv",
    "ctv3",
    "CTV3ID",
)


any_primary_care_code = combine_codelists(
    covid_primary_care_code,
    covid_primary_care_positive_test,
    covid_primary_care_sequalae,
)


long_covid_diagnostic_codes = load_codelist(
    "opensafely-nice-managing-the-long-term-effects-of-covid-19.csv",
    "snomed",
    "code",
)


long_covid_referral_codes = load_codelist(
    "opensafely-referral-and-signposting-for-long-covid.csv",
    "snomed",
    "code",
)


long_covid_assessment_codes = load_codelist(
    "opensafely-assessment-instruments-and-outcome-measures-for-long-covid.csv",
    "snomed",
    "code",
)


any_long_covid_code = combine_codelists(
    long_covid_diagnostic_codes, long_covid_referral_codes, long_covid_assessment_codes
)


post_viral_fatigue_codes = load_codelist(
    "user-alex-walker-post-viral-syndrome.csv",
    "snomed",
    "code",
)


ethnicity_codes = load_codelist(
    "opensafely-ethnicity.csv",
    "ctv3",
    "Code",
)
