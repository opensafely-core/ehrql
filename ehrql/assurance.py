from collections import defaultdict

from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.query_engines.in_memory_database import InMemoryDatabase
from ehrql.query_model.introspection import get_table_nodes
from ehrql.query_model.nodes import has_one_row_per_patient


UNEXPECTED_TEST_VALUE = "unexpected-test-value"
UNEXPECTED_COLUMN = "unexpected-column"
UNEXPECTED_ROW_COUNT = "unexpected-row-count"
UNEXPECTED_IN_POPULATION = "unexpected-in-population"
UNEXPECTED_NOT_IN_POPULATION = "unexpected-not-in-population"
UNEXPECTED_OUTPUT_VALUE = "unexpected-output-value"


class AssuranceTestError(Exception): ...


def validate(dataset, test_data):
    """Validates that the given test data
    (1) meet the constraints in the tables and
    (2) produce the given expected output.

    Returns two dictionaries mapping IDs of patients with details of
    (1) test data that did not meet the constraints of the tables and
    (2) unexpected data in the output dataset.

    For more see docs/how-to/test-dataset-definition.md
    """

    # Create objects to insert into database
    table_nodes = get_table_nodes(dataset)
    # Check tables in consistent order for easier testing
    table_nodes = sorted(table_nodes, key=lambda i: i.name)

    constraint_validation_errors = defaultdict(list)
    input_data = {table: [] for table in table_nodes}
    for patient_id, patient in test_data.items():
        for table in table_nodes:
            records = patient[table.name]
            # We treat directly supplied dict as being equivalent to a list with a
            # single member
            if isinstance(records, dict):
                records = [records]
            constraints_error = validate_constraints(records, table)
            constraint_validation_errors[patient_id].extend(constraints_error)
            column_names = table.schema.column_names
            input_data[table].extend(
                [(patient_id, *[r.get(c) for c in column_names]) for r in records]
            )

    # Discard any empty entries
    constraint_validation_errors = {
        k: v for k, v in constraint_validation_errors.items() if v
    }

    # Insert test objects into database
    database = InMemoryDatabase(input_data)

    # Query the database
    engine = InMemoryQueryEngine(database)
    query_results = {
        row.patient_id: row._asdict() for row in engine.get_results(dataset)
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
    unexpected_columns = []
    for record in records:
        for column, value in record.items():
            schema_column = table.schema.schema.get(column)
            if schema_column is None:
                unexpected_columns.append(column)
                continue
            for constraint in schema_column.constraints:
                is_valid = constraint.validate(value)
                if not is_valid:
                    unexpected_test_values.append(
                        {
                            "column": column,
                            "constraint": f"{constraint}",
                            "value": f"{value}",
                        }
                    )
    results = []
    if unexpected_test_values:
        results.append(
            {
                "type": UNEXPECTED_TEST_VALUE,
                "table": table.name,
                "details": unexpected_test_values,
            }
        )
    if unexpected_columns:
        results.append(
            {
                "type": UNEXPECTED_COLUMN,
                "table": table.name,
                "details": {
                    # De-duplicate while retaining order
                    "invalid": list(dict.fromkeys(unexpected_columns)),
                    "valid": list(table.schema.schema.keys()),
                },
            }
        )
    if has_one_row_per_patient(table) and len(records) > 1:
        results.append(
            {
                "type": UNEXPECTED_ROW_COUNT,
                "table": table.name,
                "details": {"rows": len(records)},
            }
        )
    return results


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
        for patient_id, results in constraint_validation_errors.items():
            for result in results:
                if result["type"] == UNEXPECTED_TEST_VALUE:
                    lines.append(
                        f" * Patient {patient_id} had {len(result['details'])} test data value(s) in table '{result['table']}' that did not meet the constraint(s)"
                    )
                    for detail in result["details"]:
                        lines.append(
                            f"   * for column '{detail['column']}' with '{detail['constraint']}', got '{detail['value']}'"
                        )
                elif result["type"] == UNEXPECTED_COLUMN:
                    lines.append(
                        f" * Patient {patient_id} had invalid columns in the test data for table '{result['table']}'\n"
                        f"       invalid columns: {', '.join(map(repr, result['details']['invalid']))}\n"
                        f"     valid columns are: {', '.join(map(repr, result['details']['valid']))}"
                    )
                elif result["type"] == UNEXPECTED_ROW_COUNT:
                    lines.append(
                        f" * Patient {patient_id} had {result['details']['rows']} rows of test data for table '{result['table']}' but this table accepts at most one row per patient"
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
