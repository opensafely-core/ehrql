from datetime import date

from ehrql import Dataset
from ehrql.assurance import (
    UNEXPECTED_IN_POPULATION,
    UNEXPECTED_NOT_IN_POPULATION,
    UNEXPECTED_VALUE,
    present,
    validate,
)
from ehrql.codes import SNOMEDCTCode
from ehrql.query_language import compile
from ehrql.tables import EventFrame, PatientFrame, Series, table


@table
class patients(PatientFrame):
    date_of_birth = Series(date)


@table
class events(EventFrame):
    date = Series(date)
    code = Series(SNOMEDCTCode)


dataset = Dataset()
dataset.define_population(patients.date_of_birth.is_on_or_after("2000-01-01"))
dataset.has_matching_event = events.where(
    events.code == SNOMEDCTCode("11111111")
).exists_for_patient()

test_data = {
    # Correctly not expected in population
    1: {
        "patients": {"date_of_birth": date(1999, 12, 31)},
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
        "patients": {"date_of_birth": date(1999, 12, 31)},
        "events": [{"date": date(2020, 1, 1), "code": "11111111"}],
        "expected_columns": {
            "has_matching_event": True,
        },
    },
    # Has correct expected_columns
    4: {
        "patients": {"date_of_birth": date(2010, 1, 1)},
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

expected_validation_results = {
    2: {"type": UNEXPECTED_IN_POPULATION},
    3: {"type": UNEXPECTED_NOT_IN_POPULATION},
    5: {
        "type": UNEXPECTED_VALUE,
        "details": [
            {
                "column": "has_matching_event",
                "expected": True,
                "actual": False,
            }
        ],
    },
}


def test_validate():
    assert validate(compile(dataset), test_data) == expected_validation_results


def test_present_with_errors():
    assert (
        present(expected_validation_results).strip()
        == """
Found errors with 3 patient(s)
 * Patient 2 was unexpectedly in the population
 * Patient 3 was unexpectedly not in the population
 * Patient 5 had unexpected value(s)
   * for column has_matching_event, expected True, got False
    """.strip()
    )


def test_present_with_no_errors():
    assert present({}) == "All OK!"
