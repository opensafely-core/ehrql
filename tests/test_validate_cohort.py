import pytest

from databuilder import table
from databuilder.backends import DatabricksBackend, TPPBackend
from databuilder.main import validate

from .lib.mock_backend import MockBackend
from .lib.util import OldCohortWithPopulation


@pytest.mark.parametrize(
    "backend, column, expected_succeess",
    [
        (MockBackend, "date_of_birth", True),
        (MockBackend, "height", True),  # column exists in the mock backend only
        (TPPBackend, "date_of_birth", True),
        (TPPBackend, "height", False),
    ],
)
def test_validate_for_backends(backend, column, expected_succeess):
    class Cohort(OldCohortWithPopulation):
        code = table("patients").first_by("patient_id").get(column)

    if expected_succeess:
        results = validate(Cohort, backend(None))
        assert len(results) == 3
    else:
        with pytest.raises(KeyError, match=f"'{column}'"):
            validate(Cohort, backend(None))


def test_validate_databricks_backend():
    class Cohort:
        population = table("patients").exists()
        value = table("patients").first_by("patient_id").get("patient_id")

    results = validate(Cohort, DatabricksBackend(None))
    assert len(results) == 3


def test_validate_success():
    class Cohort(OldCohortWithPopulation):
        code = table("clinical_events").first_by("patient_id").get("code")

    results = validate(Cohort, MockBackend(None))

    # when the validation succeeds, the result is a list of the generated SQL queries
    assert len(results) == 3
    # The first 2 queries will build the temp tables to select
    # 1) the "code" variable from its base table (clinical_events)
    # 2) the patients from the practice_registrations table
    # 3rd query selects the results from the temp tables
    for query in results:
        # Jut check that the query strings look like SQL
        assert "SELECT" in str(query)
