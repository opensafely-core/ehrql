from ehrql.tables import Constraint


def get_dummy_data_constraints(table_name, column_name):
    # Does not distinguish between core / tpp tables of the same name
    # Annotations are symmetric to be agnostic to order of generation
    return {
        "practice_registrations": {
            "start_date": [Constraint.RelatedToOther("end_date", "<=")],
            "end_date": [Constraint.RelatedToOther("start_date", ">=")],
        },
        "addresses": {
            "start_date": [Constraint.RelatedToOther("end_date", "<=")],
            "end_date": [Constraint.RelatedToOther("start_date", ">=")],
        },
        "apcs": {
            "admission_date": [Constraint.RelatedToOther("discharge_date", "<=")],
            "discharge_date": [Constraint.RelatedToOther("admission_date", ">=")],
        },
        "apcs_cost": {
            "admission_date": [Constraint.RelatedToOther("discharge_date", "<=")],
            "discharge_date": [Constraint.RelatedToOther("admission_date", ">=")],
        },
        "appointments": {
            "booked_date": [Constraint.RelatedToOther("start_date", "<=")],
            "start_date": [Constraint.RelatedToOther("booked_date", ">=")],
        },
        "ec_cost": {
            "arrival_date": [
                Constraint.RelatedToOther("ec_decision_to_admit_date", "<=")
            ],
            "ec_decision_to_admit_date": [
                Constraint.RelatedToOther("arrival_date", ">=")
            ],
        },
        **{
            op_table: {
                "referral_request_received_date": [
                    Constraint.RelatedToOther("appointment_date", "<=")
                ],
                "appointment_date": [
                    Constraint.RelatedToOther("referral_request_received_date", ">=")
                ],
            }
            for op_table in ["opa", "opa_cost", "opa_diag", "opa_proc"]
        },
        "sgss_covid_all_tests": {
            "specimen_taken_date": [Constraint.RelatedToOther("lab_report_date", "<=")],
            "lab_report_date": [Constraint.RelatedToOther("specimen_taken_date", ">=")],
        },
        **{
            wl_table: {
                "referral_to_treatment_period_start_date": [
                    Constraint.RelatedToOther(
                        "referral_to_treatment_period_end_date", "<="
                    )
                ],
                "referral_to_treatment_period_end_date": [
                    Constraint.RelatedToOther(
                        "referral_to_treatment_period_start_date", ">="
                    )
                ],
            }
            for wl_table in ["wl_clockstops", "wl_openpathways"]
        },
    }.get(table_name, {}).get(column_name, [])
