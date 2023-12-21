from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.query_engines.in_memory_database import InMemoryDatabase
from ehrql.query_model.introspection import get_table_nodes
from ehrql.utils.orm_utils import orm_classes_from_tables, table_has_one_row_per_patient


UNEXPECTED_IN_POPULATION = "unexpected-in-population"
UNEXPECTED_NOT_IN_POPULATION = "unexpected-not-in-population"
UNEXPECTED_VALUE = "unexpected-value"


def validate(variable_definitions, test_data):
    """Given some input data, validates that the given variables produce the given
    expected output.

    test_data contains two parts: data for each patient to be inserted into the
    database, and the expected values in the dataset for each patient.

    For instance:

        test_data = {
            1: {
                "patients": {"date_of_birth": date(1999, 12, 31)},
                "events": [],
                "expected_in_population": False,
            },
            2: {
                "patients": {"date_of_birth": date(2010, 1, 1)},
                "events": [{"date": date(2020, 1, 1), "code": "11111111"}],
                "expected_columns": {
                    "has_matching_event": True,
                },
            },
        }

    This indicates that two rows should be inserted into the patients table (one for
    each patient), and one row should be inserted into the events table (for patient 2).

    This also indicates that patient 1 should not be in the dataset, and that patient 2
    should be, with True in the "has_matching_event" column.

    Returns a dict mapping IDs of patients with unexpected data in the dataset, to
    details of the unexpected data.

    See tests/unit/test_assurance.py for more examples.
    """

    # Create objects to insert into database
    table_nodes = get_table_nodes(*variable_definitions.values())
    orm_classes = orm_classes_from_tables(table_nodes)
    input_data = []
    for patient_id, patient in test_data.items():
        for orm_class in orm_classes.values():
            if table_has_one_row_per_patient(orm_class.__table__):
                records = [patient[orm_class.__tablename__]]
            else:
                records = patient[orm_class.__tablename__]
            input_data.extend([orm_class(patient_id=patient_id, **r) for r in records])

    # Insert test objects into database
    database = InMemoryDatabase()
    database.setup(input_data)

    # Query the database
    engine = InMemoryQueryEngine(database)
    query_results = {
        row.patient_id: row._asdict()
        for row in engine.get_results(variable_definitions)
    }

    # Validate results of query
    return {
        patient_id: validation_result
        for patient_id, patient in test_data.items()
        if (validation_result := validate_patient(patient_id, patient, query_results))
    }


def validate_patient(patient_id, patient, results):
    if patient.get("expected_in_population", True):
        if patient_id not in results:
            return {"type": UNEXPECTED_NOT_IN_POPULATION}
        expected = patient["expected_columns"]
        actual = results[patient_id]
        unexpected_values = [
            {"column": k, "expected": expected[k], "actual": actual[k]}
            for k, v in expected.items()
            if expected[k] != actual[k]
        ]
        if unexpected_values:
            return {"type": UNEXPECTED_VALUE, "details": unexpected_values}
    else:
        if patient_id in results:
            return {"type": UNEXPECTED_IN_POPULATION}


def present(validation_results):
    if validation_results:
        lines = [f"Found errors with {len(validation_results)} patient(s)"]
        for patient_id, result in validation_results.items():
            if result["type"] == UNEXPECTED_IN_POPULATION:
                lines.append(
                    f" * Patient {patient_id} was unexpectedly in the population"
                )
            elif result["type"] == UNEXPECTED_NOT_IN_POPULATION:
                lines.append(
                    f" * Patient {patient_id} was unexpectedly not in the population"
                )
            elif result["type"] == UNEXPECTED_VALUE:
                lines.append(f" * Patient {patient_id} had unexpected value(s)")
                for detail in result["details"]:
                    lines.append(
                        f"   * for column {detail['column']}, expected {detail['expected']}, got {detail['actual']}"
                    )
            else:
                assert False, result["type"]

        return "\n".join(lines)
    else:
        return "All OK!"
