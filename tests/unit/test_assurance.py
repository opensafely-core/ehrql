from datetime import date

from ehrql import Dataset
from ehrql.assurance import (
    UNEXPECTED_COLUMN,
    UNEXPECTED_IN_POPULATION,
    UNEXPECTED_NOT_IN_POPULATION,
    UNEXPECTED_OUTPUT_VALUE,
    UNEXPECTED_ROW_COUNT,
    UNEXPECTED_TEST_VALUE,
    present,
    validate,
)
from ehrql.codes import SNOMEDCTCode
from ehrql.tables import Constraint, EventFrame, PatientFrame, Series, table


@table
class patients(PatientFrame):
    date_of_birth = Series(
        date,
        constraints=[Constraint.FirstOfMonth(), Constraint.NotNull()],
    )
    sex = Series(
        str,
        constraints=[
            Constraint.Categorical(["female", "male", "intersex", "unknown"]),
            Constraint.NotNull(),
        ],
    )


@table
class events(EventFrame):
    date = Series(date)
    code = Series(SNOMEDCTCode, constraints=[Constraint.NotNull()])


dataset = Dataset()
dataset.define_population(patients.date_of_birth.is_on_or_after("2000-01-01"))
dataset.has_matching_event = events.where(
    events.code == SNOMEDCTCode("11111111")
).exists_for_patient()

valid_test_data = {
    # Correctly not expected in population
    1: {
        "patients": {"date_of_birth": date(1999, 12, 1)},
        "events": [],
        "expected_in_population": False,
    },
    # Incorrectly not expected in population
    2: {
        "patients": {"date_of_birth": date(2000, 1, 1)},
        "events": [],
        "expected_in_population": False,
    },
    # Incorrectly expected in population
    3: {
        "patients": {"date_of_birth": date(1999, 12, 1)},
        "events": [{"date": date(2020, 1, 1), "code": "11111111"}],
        "expected_columns": {
            "has_matching_event": True,
        },
    },
    # Has correct expected_columns
    4: {
        # Supply data as a single membered list rather than a dict to confirm these are
        # treated equivalently
        "patients": [
            {"date_of_birth": date(2010, 1, 1)},
        ],
        "events": [{"date": date(2020, 1, 1), "code": "11111111"}],
        "expected_columns": {
            "has_matching_event": True,
        },
    },
    # Has incorrect expected_columns
    5: {
        "patients": {"date_of_birth": date(2010, 1, 1)},
        "events": [{"date": date(2020, 1, 1), "code": "22222222"}],
        "expected_columns": {
            "has_matching_event": True,
        },
    },
}

invalid_test_data = {
    # Has date_of_birth value that does not meet NotNull constraint and sex value which
    # does not meet Categorical constraint
    1: {
        "patients": {"date_of_birth": None, "sex": "not-known"},
        "events": [
            # Has invalid NULL `code`
            {"date": date(2020, 1, 1), "code": None},
        ],
        "expected_in_population": False,
    },
    # Has date_of_birth value that does not meet FirstOfMonth constraint
    2: {
        "patients": {"date_of_birth": date(1990, 1, 2)},
        "events": [
            # Has extra column not present in the schema
            {"date": date(2020, 1, 1), "code": "11111111", "extra_column": 1},
        ],
        "expected_in_population": False,
    },
    3: {
        "patients": [
            {"date_of_birth": date(1990, 1, 1)},
            {"date_of_birth": date(1995, 1, 1)},
        ],
        "events": [],
        "expected_in_population": False,
    },
}

valid_and_invalid_test_data = {
    # Incorrectly not expected in population
    1: {
        "patients": {"date_of_birth": date(2000, 1, 1)},
        "events": [],
        "expected_in_population": False,
    },
    # Has date_of_birth value that does not meet FirstOfMonth constraint
    2: {
        "patients": {"date_of_birth": date(1990, 1, 2)},
        "events": [],
        "expected_in_population": False,
    },
}

expected_valid_data_validation_results = {
    "constraint_validation_errors": {},
    "test_validation_errors": {
        2: {"type": UNEXPECTED_IN_POPULATION},
        3: {"type": UNEXPECTED_NOT_IN_POPULATION},
        5: {
            "type": UNEXPECTED_OUTPUT_VALUE,
            "details": [
                {
                    "column": "has_matching_event",
                    "expected": True,
                    "actual": False,
                }
            ],
        },
    },
}


expected_invalid_data_validation_results = {
    "constraint_validation_errors": {
        1: [
            {
                "type": UNEXPECTED_TEST_VALUE,
                "table": "events",
                "details": [
                    {
                        "column": "code",
                        "constraint": "Constraint.NotNull()",
                        "value": "None",
                    },
                ],
            },
            {
                "type": UNEXPECTED_TEST_VALUE,
                "table": "patients",
                "details": [
                    {
                        "column": "date_of_birth",
                        "constraint": "Constraint.NotNull()",
                        "value": "None",
                    },
                    {
                        "column": "sex",
                        "constraint": "Constraint.Categorical(values=('female', 'male', 'intersex', 'unknown'))",
                        "value": "not-known",
                    },
                ],
            },
        ],
        2: [
            {
                "type": UNEXPECTED_COLUMN,
                "table": "events",
                "details": {
                    "invalid": ["extra_column"],
                    "valid": ["date", "code"],
                },
            },
            {
                "type": UNEXPECTED_TEST_VALUE,
                "table": "patients",
                "details": [
                    {
                        "column": "date_of_birth",
                        "constraint": "Constraint.FirstOfMonth()",
                        "value": "1990-01-02",
                    }
                ],
            },
        ],
        3: [
            {
                "type": UNEXPECTED_ROW_COUNT,
                "table": "patients",
                "details": {"rows": 2},
            },
        ],
    },
    "test_validation_errors": {},
}

expected_valid_and_invalid_data_validation_results = {
    "constraint_validation_errors": {
        2: [
            {
                "type": UNEXPECTED_TEST_VALUE,
                "table": "patients",
                "details": [
                    {
                        "column": "date_of_birth",
                        "constraint": "Constraint.FirstOfMonth()",
                        "value": "1990-01-02",
                    }
                ],
            }
        ],
    },
    "test_validation_errors": {
        1: {"type": UNEXPECTED_IN_POPULATION},
    },
}


def test_valid_data_validate():
    assert (
        validate(dataset._compile(), valid_test_data)
        == expected_valid_data_validation_results
    )


def test_valid_data_present_with_errors():
    assert (
        present(expected_valid_data_validation_results).strip()
        == """
Validate test data: All OK!
Validate results: Found errors with 3 patient(s)
 * Patient 2 was unexpectedly in the population
 * Patient 3 was unexpectedly not in the population
 * Patient 5 had unexpected output value(s)
   * for column 'has_matching_event', expected 'True', got 'False'
    """.strip()
    )


def test_invalid_data_validate():
    assert (
        validate(dataset._compile(), invalid_test_data)
        == expected_invalid_data_validation_results
    )


def test_invalid_data_present_with_errors():
    assert (
        present(expected_invalid_data_validation_results).strip()
        == """
Validate test data: Found errors with 3 patient(s)
 * Patient 1 had 1 test data value(s) in table 'events' that did not meet the constraint(s)
   * for column 'code' with 'Constraint.NotNull()', got 'None'
 * Patient 1 had 2 test data value(s) in table 'patients' that did not meet the constraint(s)
   * for column 'date_of_birth' with 'Constraint.NotNull()', got 'None'
   * for column 'sex' with 'Constraint.Categorical(values=('female', 'male', 'intersex', 'unknown'))', got 'not-known'
 * Patient 2 had invalid columns in the test data for table 'events'
       invalid columns: 'extra_column'
     valid columns are: 'date', 'code'
 * Patient 2 had 1 test data value(s) in table 'patients' that did not meet the constraint(s)
   * for column 'date_of_birth' with 'Constraint.FirstOfMonth()', got '1990-01-02'
 * Patient 3 had 2 rows of test data for table 'patients' but this table accepts at most one row per patient
Validate results: All OK!
    """.strip()
    )


def test_valid_and_invalid_data_validate():
    assert (
        validate(dataset._compile(), valid_and_invalid_test_data)
        == expected_valid_and_invalid_data_validation_results
    )


def test_valid_and_invalid_data_present_with_errors():
    assert (
        present(expected_valid_and_invalid_data_validation_results).strip()
        == """
Validate test data: Found errors with 1 patient(s)
 * Patient 2 had 1 test data value(s) in table 'patients' that did not meet the constraint(s)
   * for column 'date_of_birth' with 'Constraint.FirstOfMonth()', got '1990-01-02'
Validate results: Found errors with 1 patient(s)
 * Patient 1 was unexpectedly in the population
    """.strip()
    )


def test_present_with_no_errors():
    validation_results_with_no_errors = {
        "constraint_validation_errors": {},
        "test_validation_errors": {},
    }
    assert (
        present(validation_results_with_no_errors).strip()
        == """
Validate test data: All OK!
Validate results: All OK!""".strip()
    )
