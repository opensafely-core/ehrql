from datetime import date, datetime
from pathlib import Path

import pytest

from databuilder import codelist
from databuilder.backends import TPPBackend
from databuilder.concepts.tables import (
    clinical_events,
    hospitalizations,
    patient_addresses,
    patients,
    registrations,
    sgss_sars_cov_2,
)
from databuilder.dsl import Cohort, categorise
from databuilder.validate_dummy_data import validate_dummy_data

from ..lib.tpp_schema import (
    apcs,
    ctv3_event,
    negative_test,
    organisation,
    patient,
    patient_address,
    positive_test,
    registration,
    snomed_event,
)
from ..lib.util import extract
from .codelists import (
    any_long_covid_code,
    any_primary_care_code,
    covid_codes,
    ethnicity_codes,
    post_viral_fatigue_codes,
)


def build_cohort():
    pandemic_start = "2020-02-01"
    index_date = "2020-11-01"
    bmi_code = codelist(["22K.."], system="ctv3")

    events = clinical_events
    addresses = patient_addresses

    cohort = Cohort()

    # Population
    # Patients registered on 2020-11-01
    registered = (
        registrations.filter(registrations.start_date <= index_date)
        .filter(
            (registrations.end_date >= index_date)
            | (registrations.end_date is not None)
        )
        .exists_for_patient()
    )
    cohort.set_population(registered)

    cohort.practice_id = (
        registrations.sort_by("date_end").last_for_patient().select_column("pseudo_id")
    )

    # COVID infection
    cohort.sgss_positive = (
        sgss_sars_cov_2.filter(sgss_sars_cov_2.positive_result is True)
        .sort_by(sgss_sars_cov_2.date)
        .first_for_patient()
        .select_column(sgss_sars_cov_2.date)
    )

    cohort.primary_care_covid = (
        events.filter(events.code in any_primary_care_code)
        .sort_by(events.date)
        .first_for_patient()
        .select_column(events.date)
    )

    cohort.hospital_covid = (
        hospitalizations.filter(hospitalizations.code in covid_codes)
        .sort_by(hospitalizations.date)
        .first_for_patient()
        .select_column(hospitalizations.date)
    )

    # Outcome
    long_covid_events = events.filter(events.code in any_long_covid_code)

    cohort.long_covid = long_covid_events.exists_for_patient()

    cohort.first_long_covid_date = (
        long_covid_events.sort_by(events.date)
        .first_for_patient()
        .select_column(events.date)
    )

    cohort.first_long_covid_code = (
        long_covid_events.sort_by(events.date)
        .first_for_patient()
        .select_column(events.code)
    )

    cohort.first_post_viral_fatigue_date = (
        events.filter(events.code in post_viral_fatigue_codes)
        .sort_by(events.date)
        .first_for_patient()
        .select_column(events.date)
    )

    # Demographics
    # Age
    age = (patients.select_column("age") - index_date).convert_to("years")
    age_categories = {
        "0-17": age < 18,
        "18-24": (age >= 18) & (age < 25),
        "25-34": (age >= 25) & (age < 35),
        "35-44": (age >= 35) & (age < 45),
        "45-54": (age >= 45) & (age < 55),
        "55-69": (age >= 55) & (age < 70),
        "70-79": (age >= 70) & (age < 80),
        "80+": age >= 80,
    }
    cohort.age_group = categorise(age_categories, default="missing")

    # Sex
    cohort.sex = patients.sort_by("patient_id").select_column("sex")

    # Region
    cohort.region = (
        registrations.sort_by("date_end")
        .last_for_patient()
        .select_column("nuts1_region_name")
    )

    # IMD
    imd = (
        addresses.filter(addresses.start_date <= index_date)
        .filter(addresses.end_date >= index_date)
        .sort_by(
            addresses.date_start,
            addresses.date_end,
            addresses.has_postcode,
            addresses.patientaddress_id,
        )
        .last_for_patient()
        .select_column(addresses.index_of_multiple_deprivation_rounded)
    )
    imd_groups = {
        "1": (imd >= 1) & (imd < (32844 * 1 / 5)),
        "2": (imd >= 32844 * 1 / 5) & (imd < (32844 * 2 / 5)),
        "3": (imd >= 32844 * 2 / 5) & (imd < (32844 * 3 / 5)),
        "4": (imd >= 32844 * 3 / 5) & (imd < (32844 * 4 / 5)),
        "5": (imd >= 32844 * 4 / 5) & (imd < 32844),
    }
    cohort.imd = categorise(imd_groups, default="0")

    # Ethnicity
    cohort.ethnicity = (
        events.filter(events.code in ethnicity_codes)
        .filter(events.date <= index_date)
        .sort_by(events.date)
        .last_for_patient()
        .select_column(events.code)
    )

    # Clinical variables
    # Latest recorded BMI
    bmi = (
        events.filter(events.code == bmi_code)
        .sort_by(events.date)
        .last_for_patient()
        .select_column("numeric_value")
    )
    bmi_groups = {
        "Obese I (30-34.9)": (bmi >= 30) & (bmi < 35),
        "Obese II (35-39.9)": (bmi >= 35) & (bmi < 40),
        "Obese III (40+)": (bmi >= 40) & (bmi < 100)
        # set maximum to avoid any impossibly extreme values being classified as obese
    }
    cohort.bmi = categorise(bmi_groups, default="Not obese")

    # Previous COVID
    previous_covid_categories = {
        "COVID positive": (
            (cohort.sgss_positive | cohort.primary_care_covid) & ~cohort.hospital_covid
        ),
        "COVID hospitalised": cohort.hospital_covid,
    }
    cohort.previous_covid = categorise(
        previous_covid_categories, default="No COVID code"
    )

    # Add the long covid and post viral code count variables
    for target_codelist in [any_long_covid_code, post_viral_fatigue_codes]:
        for code in target_codelist.codes:
            events_for_code = events.filter(
                events.code in codelist([code], target_codelist.system)
            ).filter(events.date >= pandemic_start)

            cohort.add_variable(
                f"{target_codelist.system}_{code}", events_for_code.count_for_patient()
            )

            cohort.add_variable(
                f"{target_codelist.system}_{code}_date",
                events_for_code.sort_by(events.date)
                .first_for_patient()
                .select_column(events.date),
            )

    return cohort


# when this xfail is removed, the file should be removed from coverage's omitted files
# in pyproject.toml
@pytest.mark.xfail
@pytest.mark.integration
def test_cohort(database):
    cohort = build_cohort()
    database.setup(
        organisation(organisation_id=1, region="South"),
        patient(
            1,
            "F",
            "1990-08-10",
            registration(
                start_date="2001-01-01", end_date="2026-06-26", organisation_id=1
            ),
            patient_address(
                start_date="2001-01-01",
                end_date="2026-06-26",
                imd=7000,
                msoa="E02000003",
            ),
            positive_test(specimen_date="2020-05-05"),
            # excluded by picking the earliest result
            positive_test(specimen_date="2020-06-06"),
            # excluded by being a negative result
            negative_test(specimen_date="2020-04-04"),
            # primary care covid
            ctv3_event(code="Y228e", date="2020-07-07"),  # covid diagnosis
            ctv3_event(code="Y23f7", date="2020-07-02"),  # positive covid test
            ctv3_event(code="Y20fc", date="2020-07-09"),  # covid sequelae
            apcs(codes="U071", admission_date="2020-08-08"),  # covid virus identified
            snomed_event(
                code="1325031000000108", date="2020-09-01"
            ),  # long covid referral
            snomed_event(
                code="1325091000000109", date="2020-09-09"
            ),  # long covid assessment
            snomed_event(
                code="1325161000000102", date="2020-09-09"
            ),  # long covid diagnostic code
            snomed_event(
                code="1325161000000102", date="2020-10-10"
            ),  # long covid diagnostic code
            snomed_event(code="51771007", date="2020-10-01"),  # post-viral events
            snomed_event(code="51771007", date="2020-11-01"),  # post-viral events
            ctv3_event(code="Y9930", date="2020-09-09"),  # ethnicity
            ctv3_event(code="22K..", date="2020-09-09", numeric_value=34.1),  # BMI
        ),
        # excluded by registration date
        patient(
            2,
            "M",
            "1990-1-1",
            registration(start_date="2001-01-01", end_date="2002-02-02"),
        ),
    )

    assert extract(cohort, TPPBackend, database) == [
        dict(
            patient_id=1,
            sex="F",
            age_group="25-34",
            practice_id=1,
            region="South",
            sgss_positive=date(2020, 5, 5),
            primary_care_covid=datetime(2020, 7, 2),
            hospital_covid=date(2020, 8, 8),
            long_covid=1,
            first_long_covid_date=datetime(2020, 9, 1),
            first_long_covid_code="1325031000000108",
            post_viral_fatigue=1,
            first_post_viral_fatigue_date=datetime(2020, 10, 1),
            ethnicity="Y9930",
            bmi="Obese I (30-34.9)",
            imd="2",
            snomed_1325161000000102=2,
            snomed_1325161000000102_date=datetime(2020, 9, 9),
            snomed_1325091000000109=1,
            snomed_1325091000000109_date=datetime(2020, 9, 9),
            snomed_1325031000000108=1,
            snomed_1325031000000108_date=datetime(2020, 9, 1),
            snomed_1325181000000106=None,
            snomed_1325181000000106_date=None,
            snomed_1325051000000101=None,
            snomed_1325051000000101_date=None,
            snomed_1325061000000103=None,
            snomed_1325061000000103_date=None,
            snomed_1325071000000105=None,
            snomed_1325071000000105_date=None,
            snomed_1325081000000107=None,
            snomed_1325081000000107_date=None,
            snomed_1325101000000101=None,
            snomed_1325101000000101_date=None,
            snomed_1325121000000105=None,
            snomed_1325121000000105_date=None,
            snomed_1325131000000107=None,
            snomed_1325131000000107_date=None,
            snomed_1325141000000103=None,
            snomed_1325141000000103_date=None,
            snomed_1325151000000100=None,
            snomed_1325151000000100_date=None,
            snomed_1325021000000106=None,
            snomed_1325021000000106_date=None,
            snomed_1325041000000104=None,
            snomed_1325041000000104_date=None,
            snomed_51771007=2,
            snomed_51771007_date=datetime(2020, 10, 1),
            snomed_266226000=None,
            snomed_266226000_date=None,
            snomed_272038003=None,
            snomed_272038003_date=None,
            previous_covid="COVID hospitalised",
        )
    ]


@pytest.mark.xfail
def test_validate_dummy_data():
    cohort = build_cohort()
    dummy_data_file = (
        Path(__file__).parent.parent
        / "fixtures"
        / "dummy_data"
        / "long_covid_dummy_data.csv"
    )
    validate_dummy_data(cohort, dummy_data_file, Path("output.csv"))
