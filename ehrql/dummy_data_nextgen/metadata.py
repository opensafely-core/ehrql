from ehrql.query_model.table_schema import Constraint


METADATA = {
    "practice_registrations": {
        "dummy_data_constraints": {
            "practice_pseudo_id": [Constraint.ClosedRange(0, 999)],
        },
    },
    "addresses": {
        "chronological_date_columns": ["start_date", "end_date"],
    },
    "apcs": {
        "chronological_date_columns": ["admission_date", "discharge_date"],
    },
    "apcs_cost": {
        "chronological_date_columns": ["admission_date", "discharge_date"],
    },
    "appointments": {
        "chronological_date_columns": [
            "booked_date",
            "start_date",
            "seen_date",
        ],
    },
    "ec_cost": {
        "chronological_date_columns": [
            "ec_injury_date",
            "arrival_date",
            "ec_decision_to_admit_date",
        ],
    },
    **{
        op_table: {
            "chronological_date_columns": [
                "referral_request_received_date",
                "appointment_date",
            ],
        }
        for op_table in ["opa", "opa_cost", "opa_diag", "opa_proc"]
    },
    "sgss_covid_all_tests": {
        "chronological_date_columns": [
            "specimen_taken_date",
            "lab_report_date",
        ],
    },
    **{
        wl_table: {
            "chronological_date_columns": [
                "referral_to_treatment_period_start_date",
                "referral_to_treatment_period_end_date",
            ],
        }
        for wl_table in ["wl_clockstops", "wl_openpathways"]
    },
}
