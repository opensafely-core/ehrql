from ehrql.query_model.table_schema import Constraint


def get_dummy_data_constraints(table_name, column_name):
    # Does not distinguish between core / tpp tables of the same name
    return {
        "practice_registrations": {
            # There are more practices in the UK, but for dummy data 1000 seems to be enough
            "practice_pseudo_id": [Constraint.ClosedRange(0, 999)],
        }
    }.get(table_name, {}).get(column_name, [])
