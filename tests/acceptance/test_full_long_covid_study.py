from datetime import date, datetime

import pytest
from codelists import (
    any_long_covid_code,
    any_primary_care_code,
    covid_codes,
    ethnicity_codes,
    long_covid_diagnostic_codes,
    post_viral_fatigue_codes,
)
from lib.tpp_schema import (
    apcs,
    event,
    negative_test,
    organisation,
    patient,
    positive_test,
    registration,
)
from lib.util import extract

from cohortextractor import categorise, codelist, table
from cohortextractor.backends import TPPBackend


pandemic_start = "2020-02-01"
index_date = "2020-11-01"
bmi_code = "22K.."


class Cohort:

    # Population
    # Patients registered on 2020-11-01
    _registrations = table("practice_registrations").date_in_range(index_date)
    _current_registrations = _registrations.latest("date_end")
    population = _registrations.exists()
    practice_id = _current_registrations.get("pseudo_id")

    # COVID infection
    sgss_first_positive_test_date = (
        table("sgss_sars_cov_2").filter(positive_result=True).earliest().get("date")
    )

    primary_care_covid_first_date = (
        table("clinical_events")
        .filter("code", is_in=any_primary_care_code)
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
        "code", is_in=any_long_covid_code
    )
    long_covid = _long_covid_table.exists()
    first_long_covid_date = _long_covid_table.earliest().get("date")
    first_long_covid_code = _long_covid_table.earliest().get("code")

    # Demographics
    # Age
    # _age = table("patients").age_as_of(index_date)
    # _age_categories = {
    #     "0-17": _age < 18,
    #     "18-24": _age >= 18 & _age < 25,
    #     "25-34": _age >= 25 & _age < 35,
    #     "35-44": _age >= 35 & _age < 45,
    #     "45-54": _age >= 45 & _age < 55,
    #     "55-69": _age >= 55 & _age < 70,
    #     "70-79": _age >= 70 & _age < 80,
    #     "80+": _age >= 80,
    # }
    # age_group = categorise(_age_categories, default="missing")

    # Sex
    sex = table("patients").get("sex")

    # Region
    region = _current_registrations.get("nuts1_region_name")

    # IMD - TODO syntax TBC
    # _imd_value = (
    #     table("patient_address").date_in_range(index_date).last_by(
    #       "date_start", "date_end", "has_postcode", "patientaddress_id"
    #     )
    # )
    # _imd_groups = {
    #     "1": (_imd_value >= 1) & (_imd_value < (32844 * 1 / 5)),
    #     "2": (_imd_value >= 32844 * 1 / 5) & (_imd_value < (32844 * 2 / 5)),
    #     "3": (_imd_value >= 32844 * 2 / 5) & (_imd_value < (32844 * 3 / 5)),
    #     "4": (_imd_value >= 32844 * 3 / 5) & (_imd_value < (32844 * 4 / 5)),
    #     "5": (_imd_value >= 32844 * 4 / 5) & (_imd_value < 32844),
    # }
    # imd = categorise(_imd_groups, default="0")

    # Ethnicity
    ethnicity = (
        table("clinical_events")
        .filter("code", is_in=ethnicity_codes)
        .filter("date", on_or_before=index_date)
        .latest()
        .get("code")
    )

    # Clinical variables
    # Latest recorded BMI
    _bmi_value = (
        table("clinical_events").filter(code=bmi_code).latest().get("numeric_value")
    )
    _bmi_groups = {
        "Obese I (30-34.9)": (_bmi_value >= 30) & (_bmi_value < 35),
        "Obese II (35-39.9)": (_bmi_value >= 35) & (_bmi_value < 40),
        "Obese III (40+)": (_bmi_value >= 40) & (_bmi_value < 100)
        # set maximum to avoid any impossibly extreme values being classified as obese
    }
    bmi = categorise(_bmi_groups, default="Not obese")
    # Previous COVID
    _previous_covid_categories = {
        "COVID positive": (
            sgss_first_positive_test_date | primary_care_covid_first_date
        )
        & ~hospital_covid_first_date,
        "COVID hospitalised": hospital_covid_first_date,
    }
    previous_covid = categorise(_previous_covid_categories, default="No COVID code")


# Add the long covid and post viral code count variables
for target_codelist in [long_covid_diagnostic_codes, post_viral_fatigue_codes]:
    for code in target_codelist.codes:
        variable_def = (
            table("clinical_events")
            .filter("code", is_in=codelist([code], target_codelist.system))
            .filter("date", on_or_after=pandemic_start)
            .count("code")
        )
        setattr(Cohort, f"{target_codelist.system}_{code}", variable_def)


@pytest.mark.integration
def test_cohort(database, setup_tpp_database):
    setup_tpp_database(
        organisation(organisation_id=1, region="South"),
        *patient(
            1,
            "F",
            registration(
                start_date="2001-01-01", end_date="2026-06-26", organisation_id=1
            ),
            positive_test(specimen_date="2020-05-05"),
            # excluded by picking the earliest result
            positive_test(specimen_date="2020-06-06"),
            # excluded by being a negative result
            negative_test(specimen_date="2020-04-04"),
            # primary care covid
            event(code="Y228e", date="2020-07-07"),  # covid diagnosis
            event(code="Y23f7", date="2020-07-02"),  # positive covid test
            event(code="Y20fc", date="2020-07-09"),  # covid sequelae
            apcs(codes="U071", admission_date="2020-08-08"),  # covid virus identified
            event(code="1325031000000108", date="2020-09-01"),  # long covid referral
            event(code="1325091000000109", date="2020-09-09"),  # long covid assessment
            event(
                code="1325161000000102", date="2020-09-09"
            ),  # long covid diagnostic code
            event(
                code="1325161000000102", date="2020-10-10"
            ),  # long covid diagnostic code
            event(code="51771007", date="2020-10-01"),  # post-viral events
            event(code="51771007", date="2020-11-01"),  # post-viral events
            event(code="Y9930", date="2020-09-09"),  # ethnicity
            event(code="22K..", date="2020-09-09", numeric_value=34.1),  # BMI
        ),
        # excluded by registration date
        *patient(2, "M", registration(start_date="2001-01-01", end_date="2002-02-02")),
    )

    assert extract(Cohort, TPPBackend, database) == [
        dict(
            patient_id=1,
            sex="F",
            practice_id=1,
            region="South",
            sgss_first_positive_test_date=date(2020, 5, 5),
            primary_care_covid_first_date=datetime(2020, 7, 2),
            hospital_covid_first_date=date(2020, 8, 8),
            long_covid=1,
            first_long_covid_date=datetime(2020, 9, 1),
            first_long_covid_code="1325031000000108",
            ethnicity="Y9930",
            bmi="Obese I (30-34.9)",
            snomed_1325161000000102=2,
            snomed_1325181000000106=None,
            snomed_51771007=2,
            snomed_266226000=None,
            snomed_272038003=None,
            previous_covid="COVID hospitalised",
        )
    ]
