from ehrql.tables import Constraint


def get_dummy_data_column_generation_order(table_name):
    return {
        "practice_registrations": ["start_date", "end_date"],
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
    }.get(table_name, [])


def get_dummy_data_constraints(table_name, column_name):
    # Does not distinguish between core / tpp tables of the same name
    # Forward constraints only - generation order makes sure `other` is generated first
    return {
        "practice_registrations": {
            "end_date": [Constraint.RelatedToOther("start_date", ">=")],
        },
        "addresses": {
            "end_date": [Constraint.RelatedToOther("start_date", ">=")],
        },
        "apcs": {
            "discharge_date": [Constraint.RelatedToOther("admission_date", ">=")],
        },
        "apcs_cost": {
            "discharge_date": [Constraint.RelatedToOther("admission_date", ">=")],
        },
        "appointments": {
            # booked_date <= start_date <= seen_date is enforced by specifying column generation order
            "start_date": [
                Constraint.RelatedToOther("booked_date", ">="),
            ],
            "seen_date": [Constraint.RelatedToOther("start_date", ">=")],
        },
        "ec_cost": {
            # ecinjury_date <= arrival_date <= ec_decision_to_admit_date is enforced by specifying column generation order
            "arrival_date": [
                Constraint.RelatedToOther("ec_injury_date", ">="),
            ],
            "ec_decision_to_admit_date": [
                Constraint.RelatedToOther("arrival_date", ">=")
            ],
        },
        **{
            op_table: {
                "appointment_date": [
                    Constraint.RelatedToOther("referral_request_received_date", ">=")
                ],
            }
            for op_table in ["opa", "opa_cost", "opa_diag", "opa_proc"]
        },
        "sgss_covid_all_tests": {
            "lab_report_date": [Constraint.RelatedToOther("specimen_taken_date", ">=")],
        },
        **{
            wl_table: {
                "referral_to_treatment_period_end_date": [
                    Constraint.RelatedToOther(
                        "referral_to_treatment_period_start_date", ">="
                    )
                ],
            }
            for wl_table in ["wl_clockstops", "wl_openpathways"]
        },
    }.get(table_name, {}).get(column_name, [])
