from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.query_engines.in_memory_database import InMemoryDatabase
from ehrql.query_model.introspection import get_table_nodes
from ehrql.utils.orm_utils import orm_classes_from_tables, table_has_one_row_per_patient


UNEXPECTED_TEST_VALUE = "unexpected-test-value"
UNEXPECTED_IN_POPULATION = "unexpected-in-population"
UNEXPECTED_NOT_IN_POPULATION = "unexpected-not-in-population"
UNEXPECTED_OUTPUT_VALUE = "unexpected-output-value"


def validate(variable_definitions, test_data):
    """Validates that the given test data
    (1) meet the constraints in the tables and
    (2) produce the given expected output.

    Returns two dictionaries mapping IDs of patients with details of
    (1) test data that did not meet the constraints of the tables and
    (2) unexpected data in the output dataset.

    For more see docs/how-to/test-dataset-definition.md
    """

    # Create objects to insert into database
    table_nodes = get_table_nodes(*variable_definitions.values())
    orm_classes = orm_classes_from_tables(table_nodes)
    nodes_by_table_name = {node.name: node for node in table_nodes}

    constraint_validation_errors = {}
    input_data = []
    for patient_id, patient in test_data.items():
        for orm_class in orm_classes.values():
            if table_has_one_row_per_patient(orm_class.__table__):
                records = [patient[orm_class.__tablename__]]
            else:
                records = patient[orm_class.__tablename__]
            table = nodes_by_table_name[orm_class.__tablename__]
            constraints_error = validate_constraints(records, table)
            if constraints_error:
                constraint_validation_errors[patient_id] = {
                    "type": UNEXPECTED_TEST_VALUE,
                    "details": constraints_error,
                }
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
    test_validation_errors = {
        patient_id: validation_result
        for patient_id, patient in test_data.items()
        if (validation_result := validate_patient(patient_id, patient, query_results))
    }
    return {
        "constraint_validation_errors": constraint_validation_errors,
        "test_validation_errors": test_validation_errors,
    }


def validate_constraints(records, table):
    unexpected_test_values = []
    for record in records:
        for column, value in record.items():
            constraints = table.schema.schema[column].constraints
            for constraint in constraints:
                is_valid = constraint.validate(value)
                if not is_valid:
                    unexpected_test_values.append(
                        {
                            "column": column,
                            "constraint": f"{constraint}",
                            "value": f"{value}",
                        }
                    )
    return unexpected_test_values


def validate_patient(patient_id, patient, results):
    if patient.get("expected_in_population", True):
        if patient_id not in results:
            return {"type": UNEXPECTED_NOT_IN_POPULATION}
        expected = patient["expected_columns"]
        actual = results[patient_id]
        unexpected_output_values = [
            {"column": k, "expected": expected[k], "actual": actual[k]}
            for k, v in expected.items()
            if expected[k] != actual[k]
        ]
        if unexpected_output_values:
            return {
                "type": UNEXPECTED_OUTPUT_VALUE,
                "details": unexpected_output_values,
            }
    else:
        if patient_id in results:
            return {"type": UNEXPECTED_IN_POPULATION}


def present(validation_results):
    def present_constraints(constraint_validation_errors):
        lines = []
        lines.append(
            f"Validate test data: Found errors with {len(constraint_validation_errors)} patient(s)"
        )
        for patient_id, result in constraint_validation_errors.items():
            if result["type"] == UNEXPECTED_TEST_VALUE:
                lines.append(
                    f" * Patient {patient_id} had {len(result['details'])} test data value(s) that did not meet the constraint(s)"
                )
                for detail in result["details"]:
                    lines.append(
                        f"   * for column '{detail['column']}' with '{detail['constraint']}', got '{detail['value']}'"
                    )
            else:
                assert False, result["type"]
        return "\n".join(lines)

    def present_results(test_validation_errors):
        lines = []
        lines.append(
            f"Validate results: Found errors with {len(test_validation_errors)} patient(s)"
        )
        for patient_id, result in test_validation_errors.items():
            if result["type"] == UNEXPECTED_IN_POPULATION:
                lines.append(
                    f" * Patient {patient_id} was unexpectedly in the population"
                )
            elif result["type"] == UNEXPECTED_NOT_IN_POPULATION:
                lines.append(
                    f" * Patient {patient_id} was unexpectedly not in the population"
                )
            elif result["type"] == UNEXPECTED_OUTPUT_VALUE:
                lines.append(f" * Patient {patient_id} had unexpected output value(s)")
                for detail in result["details"]:
                    lines.append(
                        f"   * for column '{detail['column']}', expected '{detail['expected']}', got '{detail['actual']}'"
                    )
            else:
                assert False, result["type"]
        return "\n".join(lines)

    if validation_results["constraint_validation_errors"]:
        lines_constraints = present_constraints(
            validation_results["constraint_validation_errors"]
        )
    else:
        lines_constraints = "Validate test data: All OK!"
    if validation_results["test_validation_errors"]:
        lines_results = present_results(validation_results["test_validation_errors"])
    else:
        lines_results = "Validate results: All OK!"

    return lines_constraints + "\n" + lines_results
