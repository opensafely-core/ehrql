from databuilder import Measure
from databuilder.tables import clinical_events, practice_registrations
from tests.lib.tpp_schema import organisation, patient, registration, snomed_event

from .codelists import (
    alt_codelist,
    asthma_codelist,
    cholesterol_codelist,
    copd_codelist,
    hba1c_codelist,
    medication_review_codelist,
    qrisk_codelist,
    rbc_codelist,
    sodium_codelist,
    systolic_bp_codelist,
    tsh_codelist,
)


def test_sro_measures_study(cohort, subtest, database):
    setup_data(database)

    index_date = "2020-11-01"
    end_of_index_month = "2020-11-30"

    measures_codelists = {
        "medication_review": medication_review_codelist,
        "systolic_bp": systolic_bp_codelist,
        "qrisk": qrisk_codelist,
        "cholesterol": cholesterol_codelist,
        "alt": alt_codelist,
        "tsh": tsh_codelist,
        "rbc": rbc_codelist,
        "hba1c": hba1c_codelist,
        "sodium": sodium_codelist,
        "asthma": asthma_codelist,
        "copd": copd_codelist,
    }

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

        # TODO: The following would be nice
        # not_dead = patient_demographics.date_of_death == None

        # TODO: Does this work as we expect it to work?
        # not_dead = (
        #     patient_demographics.select_column(patient_demographics.date_of_death)
        #     == None  # noqa: E711
        # )

        # TODO: This does not work, because population.value is an instance of
        # Comparator
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

    with subtest("codelists"):
        for measure_name, target_codelist in measures_codelists.items():
            filtered_clinical_events = (
                clinical_events.filter(
                    clinical_events.code.is_in(target_codelist.codes)
                )
                .filter(clinical_events.date >= index_date)
                .filter(clinical_events.date <= end_of_index_month)
            )

            cohort.add_variable(
                measure_name, filtered_clinical_events.exists_for_patient()
            )

            # TODO: SortedEventFrame.exists_for_patient doesn't exist, so we can't
            # filter and sort together.
            sorted_clinical_events = filtered_clinical_events.sort_by(
                clinical_events.date
            )
            measure_event_code = f"{measure_name}_event_code"
            cohort.add_variable(
                measure_event_code,
                sorted_clinical_events.last_for_patient().select_column(
                    clinical_events.code
                ),
            )

        cohort.assert_results(
            medication_review=True,
            medication_review_event_code="394720003",
            systolic_bp=None,
            systolic_bp_event_code=None,
            qrisk=None,
            qrisk_event_code=None,
            cholesterol=None,
            cholesterol_event_code=None,
            alt=None,
            alt_event_code=None,
            tsh=None,
            tsh_event_code=None,
            rbc=None,
            rbc_event_code=None,
            hba1c=None,
            hba1c_event_code=None,
            sodium=None,
            sodium_event_code=None,
            asthma=True,
            asthma_event_code="394720003",
            copd=None,
            copd_event_code=None,
        )

    with subtest(
        "measures", missing_feature="Allow measures to be registered with a cohort"
    ):
        # https://app.shortcut.com/ebm-datalab/story/456/accommodate-measures-with-the-new-dsl
        measures = []
        for measure_name, target_codelist in measures_codelists.items():
            measures.extend(
                [
                    Measure(
                        id=measure_name,
                        cohort=cohort,
                        numerator=measure_name,
                        denominator="population",
                        group_by=["practice", measure_event_code],
                    ),
                    Measure(
                        id=f"{measure_name}_practice_only",
                        cohort=cohort,
                        numerator=measure_name,
                        denominator="population",
                        group_by=["practice"],
                    ),
                ]
            )
        # TODO: This function doesn't exist yet
        # register(cohort, measures)


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
            # medication review, asthma
            snomed_event(code="394720003", date="2020-11-01"),
        ),
    )
