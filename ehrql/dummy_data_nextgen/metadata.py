CHRONOLOGICAL_DATE_COLUMNS = {
    # Does not distinguish between core / tpp tables of the same name
    "addresses": ["start_date", "end_date"],
    "apcs": ["admission_date", "discharge_date"],
    "apcs_cost": ["admission_date", "discharge_date"],
    "appointments": ["booked_date", "start_date", "seen_date"],
    "ec_cost": ["ec_injury_date", "arrival_date", "ec_decision_to_admit_date"],
    **{
        op_table: ["referral_request_received_date", "appointment_date"]
        for op_table in ["opa", "opa_cost", "opa_diag", "opa_proc"]
    },
    "sgss_covid_all_tests": ["specimen_taken_date", "lab_report_date"],
    **{
        wl_table: [
            "referral_to_treatment_period_start_date",
            "referral_to_treatment_period_end_date",
        ]
        for wl_table in ["wl_clockstops", "wl_openpathways"]
    },
}
