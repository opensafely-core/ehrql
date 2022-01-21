from datetime import date, datetime

from databuilder import codelist
from databuilder.dsl import categorise
from databuilder.tables import (
    clinical_events,
    covid_test_results,
    hospitalizations,
    patient_addresses,
    patient_demographics,
    practice_registrations,
)
from tests.lib.tpp_schema import (
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

from .codelists import (
    any_long_covid_code,
    any_primary_care_code,
    covid_codes,
    ethnicity_codes,
    post_viral_fatigue_codes,
)


# TODO: This test is excluded from code coverage because there are so many lines skipped due to missing features. Once
# all the features are implemented it should be reinstated.
def test_long_covid_study(cohort, subtest, database):
    setup_data(database)

    pandemic_start = "2020-02-01"
    index_date = "2020-11-01"
    bmi_code = codelist(["22K.."], system="ctv3")

    with subtest("population"):
        registered = (
            practice_registrations.filter(
                practice_registrations.date_start <= index_date
            )
            .filter(
                # TODO: reinstate this correct version once Predicates support logic operations
                # (practice_registrations.date_end >= index_date) | (practice_registrations.date_end != None)
                practice_registrations.date_end
                >= index_date
            )
            .exists_for_patient()
        )
        cohort.set_population(registered)

    with subtest(
        "practice_id", missing_feature="add practice ids to practice registrations"
    ):
        cohort.practice_id = (
            practice_registrations.sort_by(practice_registrations.date_end)
            .last_for_patient()
            .select_column(practice_registrations.practice_id)
        )
        cohort.assert_results(practice_id=1)

    with subtest("covid_diagnoses"):
        cohort.sgss_positive = (
            covid_test_results.filter(covid_test_results.positive_result.is_true())
            .sort_by(covid_test_results.date)
            .first_for_patient()
            .select_column(covid_test_results.date)
        )

        cohort.primary_care_covid = (
            clinical_events.filter(clinical_events.code.is_in(any_primary_care_code))
            .sort_by(clinical_events.date)
            .first_for_patient()
            .select_column(clinical_events.date)
        )

        cohort.hospital_covid = (
            hospitalizations.filter(hospitalizations.code.is_in(covid_codes))
            .sort_by(hospitalizations.date)
            .first_for_patient()
            .select_column(hospitalizations.date)
        )

        cohort.assert_results(
            sgss_positive=date(2020, 5, 5),
            primary_care_covid=datetime(2020, 7, 2),
            hospital_covid=date(2020, 8, 8),
        )

    with subtest("covid_categories", missing_feature="null checking for dates"):
        previous_covid_categories = {
            "COVID positive": (cohort.sgss_positive != None)  # noqa: E711
            | (cohort.primary_care_covid != None)  # noqa: E711
            & ~cohort.hospital_covid,
            "COVID hospitalised": cohort.hospital_covid,
        }
        cohort.previous_covid = (
            categorise(previous_covid_categories, default="No COVID code"),
        )
        cohort.assert_results(previous_covid="COVID hospitalised")

    with subtest("long_covid"):
        long_covid = clinical_events.filter(
            clinical_events.code.is_in(any_long_covid_code)
        )

        cohort.long_covid = long_covid.exists_for_patient()

        cohort.first_long_covid_date = (
            long_covid.sort_by(clinical_events.date)
            .first_for_patient()
            .select_column(clinical_events.date)
        )

        cohort.first_long_covid_code = (
            long_covid.sort_by(clinical_events.date)
            .first_for_patient()
            .select_column(clinical_events.code)
        )
        cohort.assert_results(
            long_covid=1,
            first_long_covid_date=datetime(2020, 9, 1),
            first_long_covid_code="1325031000000108",
        )

    with subtest("post_viral_fatigue"):
        post_viral_fatigue = clinical_events.filter(
            clinical_events.code.is_in(post_viral_fatigue_codes)
        )

        cohort.post_viral_fatigue = post_viral_fatigue.exists_for_patient()

        cohort.first_first_post_viral_fatigue_date = (
            post_viral_fatigue.sort_by(clinical_events.date)
            .first_for_patient()
            .select_column(clinical_events.date)
        )

        cohort.assert_results(
            post_viral_fatigue=1,
            first_first_post_viral_fatigue_date=datetime(2020, 10, 1),
        )

    with subtest("age_group"):
        age = (
            index_date
            - patient_demographics.select_column(patient_demographics.date_of_birth)
        ).convert_to_years()
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
        cohort.assert_results(age_group="25-34")

    with subtest("sex", missing_feature="sex in patient demographics table"):
        cohort.sex = patient_demographics.select_column(patient_demographics.sex)
        cohort.assert_results(sex="F")

    with subtest("region"):
        cohort.region = (
            practice_registrations.sort_by(practice_registrations.date_end)
            .last_for_patient()
            .select_column(practice_registrations.nuts1_region_name)
        )
        cohort.assert_results(region="South")

    with subtest("imd"):
        imd = (
            patient_addresses.filter(patient_addresses.date_start <= index_date)
            .filter(patient_addresses.date_end >= index_date)
            .sort_by(
                patient_addresses.date_start,
                patient_addresses.date_end,
                patient_addresses.has_postcode,
                patient_addresses.patientaddress_id,
            )
            .last_for_patient()
            .select_column(patient_addresses.index_of_multiple_deprivation_rounded)
        )
        imd_groups = {
            "1": (imd >= 1) & (imd < (32844 * 1 / 5)),
            "2": (imd >= 32844 * 1 / 5) & (imd < (32844 * 2 / 5)),
            "3": (imd >= 32844 * 2 / 5) & (imd < (32844 * 3 / 5)),
            "4": (imd >= 32844 * 3 / 5) & (imd < (32844 * 4 / 5)),
            "5": (imd >= 32844 * 4 / 5) & (imd < 32844),
        }
        cohort.imd = categorise(imd_groups, default="0")
        cohort.assert_results(imd="2")

    with subtest("ethnicity"):
        cohort.ethnicity = (
            clinical_events.filter(clinical_events.code.is_in(ethnicity_codes))
            .filter(clinical_events.date <= index_date)
            .sort_by(clinical_events.date)
            .last_for_patient()
            .select_column(clinical_events.code)
        )
        cohort.assert_results(ethnicity="Y9930")

    with subtest("bmi", missing_feature="numeric comparisons on float series"):
        bmi = (
            clinical_events.filter(clinical_events.code.is_in(bmi_code))
            .sort_by(clinical_events.date)
            .last_for_patient()
            .select_column(clinical_events.numeric_value)
        )
        bmi_groups = {
            "Obese I (30-34.9)": (bmi >= 30) & (bmi < 35),
            "Obese II (35-39.9)": (bmi >= 35) & (bmi < 40),
            "Obese III (40+)": (bmi >= 40) & (bmi < 100),
        }
        cohort.bmi_group = categorise(bmi_groups, default="Not obese")
        cohort.assert_results(bmi_group="Obese I (30-34.9)")

    with subtest("codelists"):
        for target_codelist in [any_long_covid_code, post_viral_fatigue_codes]:
            for code in target_codelist.codes:
                events_for_code = clinical_events.filter(
                    clinical_events.code.is_in(codelist([code], target_codelist.system))
                ).filter(clinical_events.date >= pandemic_start)

                cohort.add_variable(
                    f"{target_codelist.system}_{code}",
                    events_for_code.count_for_patient(),
                )

                cohort.add_variable(
                    f"{target_codelist.system}_{code}_date",
                    events_for_code.sort_by(clinical_events.date)
                    .first_for_patient()
                    .select_column(clinical_events.date),
                )

        cohort.assert_results(
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
        )


def setup_data(database):
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
