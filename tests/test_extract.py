import pytest
from lib.mock_backend import CTV3Events, MockBackend, RegistrationHistory
from lib.util import extract

from cohortextractor import table


@pytest.mark.integration
def test_pick_a_single_value(database, setup_test_database):
    input_data = [
        RegistrationHistory(PatientId=1),
        CTV3Events(PatientId=1, EventCode="xyz"),
    ]
    setup_test_database(input_data)

    class Cohort:
        code = table("clinical_events").first_by("patient_id").get("code")

    expected = [{"patient_id": 1, "code": "xyz"}]

    actual = extract(Cohort, MockBackend, database)
    assert actual == expected
