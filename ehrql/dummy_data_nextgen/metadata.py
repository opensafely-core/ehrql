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
    }.get(table_name, {}).get(column_name, [])
