from datetime import date, datetime

import pytest
from codelists import covid_codes, covid_primary_care_code, long_covid_diagnostic_codes
from lib.tpp_schema import (
    apcs,
    event,
    negative_test,
    patient,
    positive_test,
    registration,
)
from lib.util import extract

from cohortextractor import categorise, codelist, table
from cohortextractor.backends import TPPBackend


pandemic_start = "2020-02-01"
registration_date = "2020-11-01"


class SimplifiedCohort:
    population = (
        table("practice_registrations").date_in_range(registration_date).exists()
    )

    # COVID infection
    sgss_first_positive_test_date = (
        table("sgss_sars_cov_2").filter(positive_result=True).earliest().get("date")
    )

    primary_care_covid_first_date = (
        table("clinical_events")
        .filter("code", is_in=covid_primary_care_code)
        .earliest()
        .get("date")
    )

    hospital_covid_first_date = (
        table("hospitalizations")
        .filter("code", is_in=covid_codes)
        .earliest()
        .get("date")
    )

    # Outcome
    _long_covid_table = table("clinical_events").filter(
        "code", is_in=long_covid_diagnostic_codes
    )
    long_covid = _long_covid_table.exists()
    first_long_covid_date = _long_covid_table.earliest().get("date")

    # Demographics
    _age = table("patients").age_as_of(registration_date)
    _age_categories = {
        "0-17": _age < 18,
        "18-24": (_age >= 18) & (_age < 25),
        "25-34": (_age >= 25) & (_age < 35),
        "35-44": (_age >= 35) & (_age < 45),
        "45-54": (_age >= 45) & (_age < 55),
        "55-69": (_age >= 55) & (_age < 70),
        "70-79": (_age >= 70) & (_age < 80),
        "80+": _age >= 80,
    }
    age_group = categorise(_age_categories, default="missing")
    sex = table("patients").get("sex")


# Add the Long covid code count variables
for code in long_covid_diagnostic_codes.codes:
    variable_def = (
        table("clinical_events")
        .filter("code", is_in=codelist([code], long_covid_diagnostic_codes.system))
        .filter("date", on_or_after=pandemic_start)
        .count("code")
    )
    setattr(
        SimplifiedCohort, f"{long_covid_diagnostic_codes.system}_{code}", variable_def
    )


@pytest.mark.integration
def test_simplified_cohort(database, setup_tpp_database):
    setup_tpp_database(
        *patient(
            1,
            "F",
            "1990-8-10",
            registration(start_date="2001-01-01", end_date="2026-06-26"),
            positive_test(specimen_date="2020-05-05"),
            # excluded by picking the earliest result
            positive_test(specimen_date="2020-06-06"),
            # excluded by being a negative result
            negative_test(specimen_date="2020-04-04"),
            event(code="Y228e", date="2020-07-07"),  # covid diagnosis
            apcs(codes="U071", admission_date="2020-08-08"),  # covid virus identified
            event(code="1325161000000102", date="2020-09-09"),  # post-covid syndrome
            event(code="1325161000000102", date="2020-10-10"),  # post-covid syndrome
        ),
        # excluded by registration date
        *patient(
            2,
            "M",
            "1990-1-1",
            registration(start_date="2001-01-01", end_date="2002-02-02"),
        ),
    )

    assert extract(SimplifiedCohort, TPPBackend, database) == [
        dict(
            patient_id=1,
            sex="F",
            age_group="25-34",
            sgss_first_positive_test_date=date(2020, 5, 5),
            primary_care_covid_first_date=datetime(2020, 7, 7),
            hospital_covid_first_date=date(2020, 8, 8),
            long_covid=1,
            first_long_covid_date=datetime(2020, 9, 9),
            snomed_1325161000000102=2,
            snomed_1325181000000106=None,
        )
    ]
