import pytest
from conftest import extract
from lib.tpp_schema import Patient, RegistrationHistory

from cohortextractor import table
from cohortextractor.backends import TPPBackend


pandemic_start = "2020-02-01"
registration_date = "2020-11-01"


class SimplifiedCohort:
    population = (
        table("practice_registrations").date_in_range(registration_date).exists()
    )

    # # COVID infection
    # _sgss_positives = table("sgss_sars_cov_2").filter(positive_result=True)
    # sgss_first_positive_test_date = _sgss_positives.earliest().get("date")

    # _primary_care_covid = (
    #     table("clinical_events").filter("code", is_in=covid_primary_care_code)
    # )
    # primary_care_covid_first_date = _primary_care_covid.earliest().get("date")

    # _hospital_covid = table("hospitalisation").filter("code", is_in=covid_codes)
    # hospital_covid_first_date = _hospital_covid.earliest().get("date")

    # # Outcome
    # _long_covid_table = (
    #     table("clinical_events").filter("code", is_in=long_covid_diagnostic_codes)
    # )
    # long_covid = _long_covid_table.exists()
    # first_long_covid_date = _long_covid_table.earliest().get("code")

    # # Demographics
    # _age_categories = {
    #     "0-17": "age < 18",
    #     "18-24": "age >= 18 AND age < 25",
    #     "25-34": "age >= 25 AND age < 35",
    #     "35-44": "age >= 35 AND age < 45",
    #     "45-54": "age >= 45 AND age < 55",
    #     "55-69": "age >= 55 AND age < 70",
    #     "70-79": "age >= 70 AND age < 80",
    #     "80+": "age >= 80",
    #     "missing": "DEFAULT",
    # }
    # age_group = (
    #     table("patients")
    #     .categorise("age", groups=_age_categories, reference=registration_date)
    # )
    # sex = table("patients").categorise("sex")


# # Add the Long covid code count variables
# for code in long_covid_diagnostic_codes:
#     variable_def = (
#         table("clinical_events")
#         .filter(code=codelist([code]))
#         .filter("date", on_or_before=pandemic_start)
#         .count("code")
#     )
#     setattr(SimplifiedCohort, f"snomed_{code}", variable_def)


@pytest.mark.integration
def test_simplified_cohort(database, setup_tpp_database):
    setup_tpp_database(
        [
            Patient(Patient_ID=1),
            RegistrationHistory(
                Patient_ID=1, StartDate="2001-01-01", EndDate="2026-06-26"
            ),
            Patient(Patient_ID=2),  # excluded by registration date
            RegistrationHistory(
                Patient_ID=2, StartDate="2001-01-01", EndDate="2002-02-02"
            ),
        ]
    )
    assert extract(SimplifiedCohort, TPPBackend, database) == [dict(patient_id=1)]
