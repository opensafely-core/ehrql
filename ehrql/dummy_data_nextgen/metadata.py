from ehrql.query_model.table_schema import BaseConstraint, Constraint


class DummyDataConstraint(Constraint):
    class RelatedToOther(BaseConstraint):
        other: str
        relation: str

        @property
        def description(self):
            return f"Value must be {self.relation} value in column `{self.other}`"

        def validate(self, value, other_value):
            if value is None or other_value is None:
                return True
            match self.relation:
                case "<":
                    return value < other_value
                case "<=":
                    return value <= other_value
                case "==":
                    return value == other_value
                case "!=":
                    return value != other_value
                case ">=":
                    return value >= other_value
                case ">":
                    return value > other_value
                case _:
                    assert False, f"Unknown relation '{self.relation}'"

        def filter_values(self, values, other_value):
            return [v for v in values if self.validate(v, other_value)]


def get_dummy_data_constraints(table_name, column_name):
    # Does not distinguish between core / tpp tables of the same name
    # Date annotations are symmetric to be agnostic to order of generation
    return {
        "practice_registrations": {
            # There are more practices in the UK, but for dummy data 1000 seems to be enough
            "practice_pseudo_id": [Constraint.ClosedRange(0, 999)],
        },
        "addresses": {
            "start_date": [DummyDataConstraint.RelatedToOther("end_date", "<=")],
            "end_date": [DummyDataConstraint.RelatedToOther("start_date", ">=")],
        },
        "apcs": {
            "admission_date": [
                DummyDataConstraint.RelatedToOther("discharge_date", "<=")
            ],
            "discharge_date": [
                DummyDataConstraint.RelatedToOther("admission_date", ">=")
            ],
        },
        "apcs_cost": {
            "admission_date": [
                DummyDataConstraint.RelatedToOther("discharge_date", "<=")
            ],
            "discharge_date": [
                DummyDataConstraint.RelatedToOther("admission_date", ">=")
            ],
        },
        "appointments": {
            "booked_date": [DummyDataConstraint.RelatedToOther("start_date", "<=")],
            "start_date": [DummyDataConstraint.RelatedToOther("booked_date", ">=")],
        },
        "ec_cost": {
            "arrival_date": [
                DummyDataConstraint.RelatedToOther("ec_decision_to_admit_date", "<=")
            ],
            "ec_decision_to_admit_date": [
                DummyDataConstraint.RelatedToOther("arrival_date", ">=")
            ],
        },
        **{
            op_table: {
                "referral_request_received_date": [
                    DummyDataConstraint.RelatedToOther("appointment_date", "<=")
                ],
                "appointment_date": [
                    DummyDataConstraint.RelatedToOther(
                        "referral_request_received_date", ">="
                    )
                ],
            }
            for op_table in ["opa", "opa_cost", "opa_diag", "opa_proc"]
        },
        "sgss_covid_all_tests": {
            "specimen_taken_date": [
                DummyDataConstraint.RelatedToOther("lab_report_date", "<=")
            ],
            "lab_report_date": [
                DummyDataConstraint.RelatedToOther("specimen_taken_date", ">=")
            ],
        },
        **{
            wl_table: {
                "referral_to_treatment_period_start_date": [
                    DummyDataConstraint.RelatedToOther(
                        "referral_to_treatment_period_end_date", "<="
                    )
                ],
                "referral_to_treatment_period_end_date": [
                    DummyDataConstraint.RelatedToOther(
                        "referral_to_treatment_period_start_date", ">="
                    )
                ],
            }
            for wl_table in ["wl_clockstops", "wl_openpathways"]
        },
    }.get(table_name, {}).get(column_name, [])
