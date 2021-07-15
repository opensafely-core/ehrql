from datetime import datetime

import pytest
from conftest import extract
from lib.tpp_schema import Events, Patient, RegistrationHistory

from cohortextractor import table
from cohortextractor.backends.tpp import TPPBackend


@pytest.mark.integration
def test_basic_events_and_registration(database, setup_tpp_database):
    setup_tpp_database(
        [
            Patient(Patient_ID=1),
            RegistrationHistory(Patient_ID=1),
            Events(Patient_ID=1, CTV3Code="Code1"),
        ]
    )

    class Cohort:
        code = table("clinical_events").get("code")

    assert extract(Cohort, TPPBackend, database) == [dict(patient_id=1, code="Code1")]


@pytest.mark.integration
def test_registration_dates(database, setup_tpp_database):
    setup_tpp_database(
        [
            Patient(Patient_ID=1),
            RegistrationHistory(
                Patient_ID=1, StartDate="2001-01-01", EndDate="2012-12-12"
            ),
        ]
    )

    class Cohort:
        _registrations = table("practice_registrations")
        arrived = _registrations.get("date_start")
        left = _registrations.get("date_end")

    assert extract(Cohort, TPPBackend, database) == [
        dict(patient_id=1, arrived=datetime(2001, 1, 1), left=datetime(2012, 12, 12))
    ]
