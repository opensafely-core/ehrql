from ehrql.tables import Constraint


def get_dummy_data_constraints(table_name, column_name):
    # Annotations are symmetric to be agnostic to order of generation
    return {
        "annotated_events": {
            "date_start": [Constraint.RelatedToOther("date_end", "<=")],
            "date_end": [Constraint.RelatedToOther("date_start", ">=")],
        }
    }.get(table_name, {}).get(column_name, [])
