import pytest
from conftest import extract
from lib.tpp_schema import Base, Events, Patient, RegistrationHistory

from cohortextractor import table
from cohortextractor.backends.tpp import TPPBackend


@pytest.fixture
def setup_tpp_database(setup_test_database):
    def setup(data):
        setup_test_database(data, base=Base)

    yield setup


@pytest.mark.integration
def test_pick_a_single_value(database, setup_tpp_database):
    setup_tpp_database(
        [
            Patient(Patient_ID=1),
            RegistrationHistory(Patient_ID=1),
            Events(Patient_ID=1, CTV3Code="Code1"),
        ]
    )

    class Cohort:
        code = table("clinical_events").get("code")

    expected = [{"patient_id": 1, "code": "Code1"}]

    actual = extract(Cohort, TPPBackend, database)
    assert actual == expected
