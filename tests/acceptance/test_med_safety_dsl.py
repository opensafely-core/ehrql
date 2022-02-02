from databuilder.tables import (
    clinical_events,
    hospital_admissions,
    patient_demographics,
    practice_registrations,
)
from tests.lib.tpp_schema import organisation, patient, registration, snomed_event

from .codelists import (
    gib_admissions_codelist,
    oral_nsaid_codelist,
    placeholder_admissions_codelist,
    ppi_codelist,
)

# The following codes are used by APC (Admitted Patient Care), the national dataset for
# hospital admissions. They are specific to this dataset, so we don't represent them as
# a codelist. For more information, see:
# * https://docs.opensafely.org/dataset-apc/#admission_method
# * https://datadictionary.nhs.uk/attributes/admission_method.html
EMERGENCY_ADMISSION_CODES = [
    "21",  # Emergency Admission: Emergency Care Department or dental casualty department of the Health Care Provider
    "22",  # Emergency Admission: GENERAL PRACTITIONER: after a request for immediate admission has been made direct to a Hospital Provider, i.e. not through a Bed bureau, by a GENERAL PRACTITIONER or deputy
    "23",  # Emergency Admission: Bed bureau
    "24",  # Emergency Admission: Consultant Clinic, of this or another Health Care Provider
    "25",  # Emergency Admission: Admission via Mental Health Crisis Resolution Team
    "2A",  # Emergency Admission: Emergency Care Department of another provider where the PATIENT  had not been admitted
    "2B",  # Emergency Admission: Transfer of an admitted PATIENT from another Hospital Provider in an emergency
    "2D",  # Emergency Admission: Other emergency admission
    "28",  # Emergency Admission: Other means, examples are:
    # - admitted from the Emergency Care Department of another provider where they had not been admitted
    # - transfer of an admitted PATIENT from another Hospital Provider in an emergency
    # - baby born at home as intended
]


def test_med_safety_study(cohort, subtest, database):
    setup_data(database)

    index_date = "2019-09-01"
    index_date_minus_3_months = "2019-06-01"

    with subtest("population"):
        filtered_practice_registrations = (
            practice_registrations.filter(
                practice_registrations.date_start <= index_date
            )
            # TODO: Reinstate the following when Predicates support logic operations
            # .filter(
            #     (practice_registrations.date_end >= index_date)
            #     | (practice_registrations.date_end != None)
            # )
            .filter(practice_registrations.date_end >= index_date)
        )

        is_registered = filtered_practice_registrations.exists_for_patient()

        # not_dead = (
        #     patient_demographics.select_column(patient_demographics.date_of_death)
        #     is not None
        # )

        # TODO: Missing feature: Arithmetic on BoolSeries
        # cohort.set_population(is_registered & not_dead)

        cohort.set_population(is_registered)

    with subtest(
        "practice_id", missing_feature="add practice ids to practice registrations"
    ):
        cohort.practice_id = (
            filtered_practice_registrations.sort_by(practice_registrations.date_end)
            .last_for_patient()
            .select_column(practice_registrations.practice_id)
        )
        cohort.assert_results(practice_id=1)

    with subtest("age"):
        cohort.age = (
            index_date
            - patient_demographics.select_column(patient_demographics.date_of_birth)
        ).convert_to_years()
        cohort.assert_results(age=65)

    with subtest("sex"):
        cohort.sex = patient_demographics.select_column(patient_demographics.sex)
        cohort.assert_results(sex="female")

    # Indicators
    # ==========

    # GIB01
    # -----
    with subtest("oral_nsaid"):
        cohort.oral_nsaid = (
            clinical_events.filter(clinical_events.code.is_in(oral_nsaid_codelist))
            .filter(clinical_events.date >= index_date_minus_3_months)
            .filter(clinical_events.date <= index_date)
            .exists_for_patient()
        )
        cohort.assert_results(oral_nsaid=True)

    with subtest("ppi"):
        cohort.ppi = (
            clinical_events.filter(clinical_events.code.is_in(ppi_codelist))
            .filter(clinical_events.date >= index_date_minus_3_months)
            .filter(clinical_events.date <= index_date)
            .exists_for_patient()
        )
        cohort.assert_results(ppi=True)

    with subtest("indicator_gib_risk", missing_feature="Arithmetic on BoolSeries"):
        at_gib_risk = cohort.oral_nsaid & (cohort.age >= 65)  # noqa: F841
        not_at_gib_risk = at_gib_risk & ~cohort.ppi  # noqa: F841

        # Why does the following numerator/denominator pair need to be commented out (to
        # avoid raising a TypeError) but the other two numerator/denominator pairs do
        # not?
        # cohort.indicator_gib_risk_numerator = not_at_gib_risk
        # cohort.indicator_gib_risk_denominator = at_gib_risk

        cohort.assert_results(indicator_gib_risk_numerator=None)
        cohort.assert_results(indicator_gib_risk_denominator=None)

    with subtest(
        "indicator_gib_num_admissions",
        missing_feature="Missing TPPBackend.hospital_admissions",
    ):
        # TPPBackend.hospitalizations exists but doesn't expose an admission_method
        # property. It's also not clear whether hospitalizations.code ==
        # hospital_admissions.primary_diagnosis.
        indicator_gib_num_admissions = (
            hospital_admissions.filter(
                hospital_admissions.primary_diagnosis.is_in(gib_admissions_codelist)
            )
            .filter(hospital_admissions.episode_is_finished is True)
            .filter(hospital_admissions.admission_date >= index_date_minus_3_months)
            .filter(hospital_admissions.admission_date <= index_date)
        )
        with subtest(
            "indicator_gib_num_admissions_admission_method",
            missing_feature="admission_method can contain alphanumeric codes, not just integers; it should be possible to query it with is_in",
        ):
            indicator_gib_num_admissions = indicator_gib_num_admissions.filter(
                hospital_admissions.admission_method.is_in(EMERGENCY_ADMISSION_CODES)
            )

        cohort.indicator_gib_num_admissions = (
            indicator_gib_num_admissions.count_for_patient()
        )
        cohort.assert_results(indicator_gib_num_admissions=None)

        cohort.indicator_gib_admission_numerator = (
            cohort.indicator_gib_risk_numerator
            & (cohort.indicator_gib_num_admissions > 0)
        )
        cohort.assert_results(indicator_gib_admission_numerator=None)

    # AKI01
    # -----
    with subtest("ras"):
        # In the v1 study definition, the variable passed to the equivalent of is_in,
        # below, is called a placeholder. However, it corresponds to the same underlying
        # codelist as oral_nsaid_codelist, which makes the following property identical
        # to cohort.oral_nsaid. We will retain it, despite the redundancy, because it
        # makes comparing the v1 study definition to the cohort easier.
        cohort.ras = (
            clinical_events.filter(clinical_events.code.is_in(oral_nsaid_codelist))
            .filter(clinical_events.date >= index_date_minus_3_months)
            .filter(clinical_events.date <= index_date)
            .exists_for_patient()
        )
        cohort.assert_results(ras=True)

    with subtest("diuretic"):
        # See above comment
        cohort.diuretic = (
            clinical_events.filter(clinical_events.code.is_in(oral_nsaid_codelist))
            .filter(clinical_events.date >= index_date_minus_3_months)
            .filter(clinical_events.date <= index_date)
            .exists_for_patient()
        )
        cohort.assert_results(diuretic=True)

    with subtest("indicator_aki_risk", missing_feature="Arithmetic on BoolSeries"):
        cohort.indicator_aki_risk_numerator = (
            cohort.oral_nsaid & cohort.ras & cohort.diuretic
        )
        cohort.indicator_aki_risk_denominator = (
            cohort.oral_nsaid | cohort.ras | cohort.diuretic
        )
        cohort.assert_results(indicator_aki_risk_numerator=None)
        cohort.assert_results(indicator_aki_risk_denominator=None)

    with subtest(
        "indicator_aki_num_admissions",
        missing_feature="Missing TPPBackend.hospital_admissions",
    ):
        # TPPBackend.hospitalizations exists but doesn't expose an admission_method
        # property. It's also not clear whether hospitalizations.code ==
        # hospital_admissions.primary_diagnosis.
        indicator_aki_num_admissions = (
            hospital_admissions.filter(
                hospital_admissions.primary_diagnosis.is_in(
                    placeholder_admissions_codelist
                )
            )
            .filter(hospital_admissions.episode_is_finished is True)
            .filter(hospital_admissions.admission_date >= index_date_minus_3_months)
            .filter(hospital_admissions.admission_date <= index_date)
        )
        with subtest(
            "indicator_aki_num_admissions_admission_method",
            missing_feature="admission_method can contain alphanumeric codes, not just integers; it should be possible to query it with is_in",
        ):
            indicator_aki_num_admissions = indicator_aki_num_admissions.filter(
                hospital_admissions.admission_method.is_in(EMERGENCY_ADMISSION_CODES)
            )

        cohort.indicator_aki_num_admissions = (
            indicator_aki_num_admissions.count_for_patient()
        )
        cohort.assert_results(indicator_aki_num_admissions=None)

        cohort.indicator_aki_admission_numerator = (
            cohort.indicator_aki_risk_numerator
            & (cohort.indicator_aki_num_admissions > 0)
        )
        cohort.assert_results(indicator_aki_admission_numerator=None)

    # PAIN01
    # ------
    with subtest("opioid"):
        # In the v1 study definition, the variable passed to the equivalent of is_in,
        # below, is called a placeholder. However, it corresponds to the same underlying
        # codelist as oral_nsaid_codelist, which makes the following property identical
        # to cohort.oral_nsaid. We will retain it, despite the redundancy, because it
        # makes comparing the v1 study definition to the cohort easier.
        cohort.opioid = (
            clinical_events.filter(clinical_events.code.is_in(oral_nsaid_codelist))
            .filter(clinical_events.date >= index_date_minus_3_months)
            .filter(clinical_events.date <= index_date)
            .exists_for_patient()
        )
        cohort.assert_results(opioid=True)

    with subtest("sedative"):
        # See above comment
        cohort.sedative = (
            clinical_events.filter(clinical_events.code.is_in(oral_nsaid_codelist))
            .filter(clinical_events.date >= index_date_minus_3_months)
            .filter(clinical_events.date <= index_date)
            .exists_for_patient()
        )
        cohort.assert_results(sedative=True)

    with subtest("indicator_pain_risk", missing_feature="Arithmetic on BoolSeries"):
        cohort.indicator_pain_risk_numerator = cohort.opioid & cohort.sedative
        cohort.indicator_pain_risk_denominator = cohort.opioid | cohort.sedative
        cohort.assert_results(indicator_pain_risk_numerator=None)
        cohort.assert_results(indicator_pain_risk_denominator=None)

    with subtest(
        "indicator_pain_num_admissions",
        missing_feature="Missing TPPBackend.hospital_admissions",
    ):
        # TPPBackend.hospitalizations exists but doesn't expose an admission_method
        # property. It's also not clear whether hospitalizations.code ==
        # hospital_admissions.primary_diagnosis.
        indicator_pain_num_admissions = (
            hospital_admissions.filter(
                hospital_admissions.primary_diagnosis.is_in(
                    placeholder_admissions_codelist
                )
            )
            .filter(hospital_admissions.episode_is_finished is True)
            .filter(hospital_admissions.admission_date >= index_date_minus_3_months)
            .filter(hospital_admissions.admission_date <= index_date)
        )
        with subtest(
            "indicator_pain_num_admissions_admission_method",
            missing_feature="admission_method can contain alphanumeric codes, not just integers; it should be possible to query it with is_in",
        ):
            indicator_pain_num_admissions.filter(
                hospital_admissions.admission_method.is_in(EMERGENCY_ADMISSION_CODES)
            )

        cohort.indicator_pain_num_admissions = (
            indicator_pain_num_admissions.count_for_patient()
        )
        cohort.assert_results(indicator_pain_num_admissions=None)

        cohort.indicator_pain_admission_numerator = (
            cohort.indicator_pain_risk_numerator
            & (cohort.indicator_pain_num_admissions > 0)
        )
        cohort.assert_results(indicator_pain_admission_numerator=None)


def setup_data(database):
    database.setup(
        organisation(organisation_id=1, region="South"),
        patient(
            1,
            "F",
            "1954-09-01",
            registration(
                start_date="2001-01-01", end_date="2026-06-26", organisation_id=1
            ),
            snomed_event(code="621911000001109", date="2019-06-01"),  # oral nsaid
            snomed_event(code="240811000001108", date="2019-09-01"),  # ppi
        ),
    )
