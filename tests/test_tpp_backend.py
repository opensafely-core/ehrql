from datetime import date, datetime

import pytest
from lib.tpp_schema import (
    Events,
    Patient,
    RegistrationHistory,
    SGSSNegativeTests,
    SGSSPositiveTests,
    apcs,
    patient,
    registration,
)
from lib.util import extract

from cohortextractor import table
from cohortextractor.backends.tpp import TPPBackend


@pytest.mark.integration
def test_basic_events_and_registration(database, setup_tpp_database):
    setup_tpp_database(
        Patient(Patient_ID=1),
        RegistrationHistory(Patient_ID=1),
        Events(Patient_ID=1, CTV3Code="Code1"),
    )

    class Cohort:
        code = table("clinical_events").get("code")

    assert extract(Cohort, TPPBackend, database) == [dict(patient_id=1, code="Code1")]


@pytest.mark.integration
def test_registration_dates(database, setup_tpp_database):
    setup_tpp_database(
        Patient(Patient_ID=1),
        RegistrationHistory(Patient_ID=1, StartDate="2001-01-01", EndDate="2012-12-12"),
    )

    class Cohort:
        _registrations = table("practice_registrations")
        arrived = _registrations.get("date_start")
        left = _registrations.get("date_end")

    assert extract(Cohort, TPPBackend, database) == [
        dict(patient_id=1, arrived=datetime(2001, 1, 1), left=datetime(2012, 12, 12))
    ]


@pytest.mark.integration
def test_covid_test_positive_result(database, setup_tpp_database):
    setup_tpp_database(
        Patient(Patient_ID=1),
        RegistrationHistory(Patient_ID=1, StartDate="2001-01-01", EndDate="2026-06-26"),
        SGSSPositiveTests(
            Patient_ID=1,
            Organism_Species_Name="SARS-CoV-2",
            Specimen_Date="2020-05-05",
        ),
    )

    class Cohort:
        date = (
            table("sgss_sars_cov_2").filter(positive_result=True).earliest().get("date")
        )

    assert extract(Cohort, TPPBackend, database) == [
        dict(patient_id=1, date=date(2020, 5, 5))
    ]


@pytest.mark.integration
def test_covid_test_negative_result(database, setup_tpp_database):
    setup_tpp_database(
        Patient(Patient_ID=1),
        RegistrationHistory(Patient_ID=1, StartDate="2001-01-01", EndDate="2026-06-26"),
        SGSSNegativeTests(
            Patient_ID=1,
            Organism_Species_Name="SARS-CoV-2",
            Specimen_Date="2020-05-05",
        ),
    )

    class Cohort:
        date = (
            table("sgss_sars_cov_2")
            .filter(positive_result=False)
            .earliest()
            .get("date")
        )

    assert extract(Cohort, TPPBackend, database) == [
        dict(patient_id=1, date=date(2020, 5, 5))
    ]


@pytest.mark.integration
def test_patients_table(database, setup_tpp_database):
    setup_tpp_database(
        Patient(Patient_ID=1, Sex="F", DateOfBirth="1950-01-01"),
        RegistrationHistory(Patient_ID=1, StartDate="2001-01-01", EndDate="2026-06-26"),
    )

    class Cohort:
        _patients = table("patients")
        sex = _patients.get("sex")
        dob = _patients.get("date_of_birth")

    assert extract(Cohort, TPPBackend, database) == [
        dict(patient_id=1, sex="F", dob=date(1950, 1, 1))
    ]


@pytest.mark.integration
def test_hospitalization_table(database, setup_tpp_database):
    setup_tpp_database(
        *patient(1, "M", registration("2001-01-01", "2026-06-26"), apcs("2020-12-12"))
    )

    class Cohort:
        admission = table("hospitalizations").get("date")

    assert extract(Cohort, TPPBackend, database) == [
        dict(patient_id=1, admission=date(2020, 12, 12))
    ]
