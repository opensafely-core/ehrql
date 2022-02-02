from pathlib import Path

from databuilder import codelist, codelist_from_csv, combine_codelists


def load_codelist(csv_file, system, column):
    return codelist_from_csv(
        Path(__file__).parent.parent.absolute()
        / "fixtures"
        / "acceptance"
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


# SRO MEASURES

asthma_codelist = load_codelist(
    "opensafely-asthma-annual-review-qof.csv", "snomed", "code"
)

copd_codelist = load_codelist(
    "opensafely-chronic-obstructive-pulmonary-disease-copd-review-qof.csv",
    "snomed",
    "code",
)

qrisk_codelist = load_codelist(
    "opensafely-cvd-risk-assessment-score-qof.csv",
    "snomed",
    "code",
)

tsh_codelist = load_codelist(
    "opensafely-thyroid-stimulating-hormone-tsh-testing.csv",
    "snomed",
    "code",
)

alt_codelist = load_codelist(
    "opensafely-alanine-aminotransferase-alt-tests.csv",
    "snomed",
    "code",
)

cholesterol_codelist = load_codelist(
    "opensafely-cholesterol-tests.csv",
    "snomed",
    "code",
)

hba1c_codelist = load_codelist(
    "opensafely-glycated-haemoglobin-hba1c-tests.csv",
    "snomed",
    "code",
)

rbc_codelist = load_codelist(
    "opensafely-red-blood-cell-rbc-tests.csv",
    "snomed",
    "code",
)

sodium_codelist = load_codelist(
    "opensafely-sodium-tests-numerical-value.csv",
    "snomed",
    "code",
)

systolic_bp_codelist = load_codelist(
    "opensafely-systolic-blood-pressure-qof.csv",
    "snomed",
    "code",
)

medication_review_1 = load_codelist(
    "opensafely-care-planning-medication-review-simple-reference-set-nhs-digital.csv",
    "snomed",
    "code",
)

medication_review_2 = load_codelist(
    "nhsd-primary-care-domain-refsets-medrvw_cod.csv",
    "snomed",
    "code",
)

medication_review_codelist = combine_codelists(medication_review_1, medication_review_2)

oral_nsaid_codelist = load_codelist(
    "pincer-nsaid-23edd06e.csv",
    "snomed",
    "id",
)

ppi_codelist = load_codelist(
    "pincer-ppi-3cfd43a3.csv",
    "snomed",
    "id",
)

gib_admissions_codelist = load_codelist(
    "nhsbsa-adm-gastro-intestinal-bleed-5d4b7131.csv",
    "icd10",
    "code",
)

placeholder_admissions_codelist = codelist(
    ["K226", "K226", "K226", "K252", "K254", "K256", "K260", "K262", "K264", "K266"],
    system="icd10",
)
