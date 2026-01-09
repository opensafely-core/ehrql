import pytest

from ehrql import Dataset
from ehrql.dummy_data_nextgen.generator import DummyDataGenerator
from ehrql.tables.core import practice_registrations
from ehrql.tables.tpp import (
    addresses,
    apcs,
    apcs_cost,
    appointments,
    ec_cost,
    opa,
    opa_cost,
    opa_diag,
    opa_proc,
    sgss_covid_all_tests,
    wl_clockstops,
    wl_openpathways,
)


@pytest.mark.parametrize(
    "table,earlier_date_col_name,later_date_col_name",
    [
        (practice_registrations, "start_date", "end_date"),
        (addresses, "start_date", "end_date"),
        (apcs, "admission_date", "discharge_date"),
        (apcs_cost, "admission_date", "discharge_date"),
        (appointments, "booked_date", "start_date"),
        (appointments, "start_date", "seen_date"),
        (ec_cost, "arrival_date", "ec_decision_to_admit_date"),
        (ec_cost, "ec_injury_date", "arrival_date"),
        (
            opa,
            "referral_request_received_date",
            "appointment_date",
        ),
        (
            opa_cost,
            "referral_request_received_date",
            "appointment_date",
        ),
        (
            opa_diag,
            "referral_request_received_date",
            "appointment_date",
        ),
        (
            opa_proc,
            "referral_request_received_date",
            "appointment_date",
        ),
        (sgss_covid_all_tests, "specimen_taken_date", "lab_report_date"),
        (
            wl_clockstops,
            "referral_to_treatment_period_start_date",
            "referral_to_treatment_period_end_date",
        ),
        (
            wl_openpathways,
            "referral_to_treatment_period_start_date",
            "referral_to_treatment_period_end_date",
        ),
    ],
)
def test_dummy_data_generator_with_one_date_constrainted_to_be_before_another(
    table, earlier_date_col_name, later_date_col_name
):
    dataset = Dataset()
    dataset.define_population(table.exists_for_patient())

    last_event = table.sort_by(getattr(table, earlier_date_col_name)).last_for_patient()
    last_event_earlier_date = getattr(last_event, earlier_date_col_name)
    last_event_later_date = getattr(last_event, later_date_col_name)
    dataset.is_valid = last_event_earlier_date <= last_event_later_date

    variable_definitions = dataset._compile()
    generator = DummyDataGenerator(variable_definitions)
    generator.population_size = 10
    generator.batch_size = 5
    results = list(generator.get_results())

    # We might want to mix in some invalid results in the future?
    assert set(r.is_valid for r in results).issubset({True, None})
