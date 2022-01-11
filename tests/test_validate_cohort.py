import pytest

from databuilder.main import validate
from databuilder.query_model import Table

from .lib.contracts import Events
from .lib.mock_backend import MockBackend
from .lib.util import OldCohortWithPopulation


def test_validate_success():
    class Cohort(OldCohortWithPopulation):
        code = Table(Events).first_by("patient_id").get("code")

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


def test_validate_failure():
    class Cohort(OldCohortWithPopulation):
        code = Table(Events).first_by("patient_id").get("toad")

    with pytest.raises(KeyError, match="'toad'"):
        validate(Cohort, MockBackend(None))
