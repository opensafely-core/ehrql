from datetime import date

import pytest
import sqlalchemy

from databuilder.backends.tpp import TPPBackend
from databuilder.tables.beta import tpp
from tests.lib.tpp_schema import (
    APCS,
    EC,
    APCS_Der,
    CodedEvent,
    CodedEventSnomed,
    EC_Diagnosis,
    HealthCareWorker,
    MedicationDictionary,
    MedicationIssue,
    ONSDeaths,
    Organisation,
    Patient,
    PatientAddress,
    PotentialCareHomeAddress,
    RegistrationHistory,
    SGSS_AllTests_Negative,
    SGSS_AllTests_Positive,
    Vaccination,
    VaccinationReference,
)


@pytest.fixture
def select_all(mssql_database):
    def _select_all(table, *input_data):
        mssql_database.setup(*input_data)
        qm_table = table.qm_node
        sql_table = TPPBackend().get_table_expression(qm_table.name, qm_table.schema)
        columns = [column.label(column.key) for column in sql_table.columns]
        query = sqlalchemy.select(*columns)
        with mssql_database.engine().connect() as connection:
            results = connection.execute(query)
            return [dict(row) for row in results]

    return _select_all


def test_patients(select_all):
    results = select_all(
        tpp.patients,
        Patient(Patient_ID=1, DateOfBirth="2020-01-01", Sex="M"),
        Patient(Patient_ID=2, DateOfBirth="2020-01-01", Sex="F"),
        Patient(Patient_ID=3, DateOfBirth="2020-01-01", Sex="I"),
        Patient(Patient_ID=4, DateOfBirth="2020-01-01", Sex="U"),
        Patient(Patient_ID=5, DateOfBirth="2020-01-01", Sex=""),
        Patient(
            Patient_ID=6, DateOfBirth="2000-01-01", Sex="M", DateOfDeath="2020-01-01"
        ),
        Patient(
            Patient_ID=7, DateOfBirth="2000-01-01", Sex="M", DateOfDeath="9999-12-31"
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "date_of_birth": date(2020, 1, 1),
            "sex": "male",
            "date_of_death": None,
        },
        {
            "patient_id": 2,
            "date_of_birth": date(2020, 1, 1),
            "sex": "female",
            "date_of_death": None,
        },
        {
            "patient_id": 3,
            "date_of_birth": date(2020, 1, 1),
            "sex": "intersex",
            "date_of_death": None,
        },
        {
            "patient_id": 4,
            "date_of_birth": date(2020, 1, 1),
            "sex": "unknown",
            "date_of_death": None,
        },
        {
            "patient_id": 5,
            "date_of_birth": date(2020, 1, 1),
            "sex": "unknown",
            "date_of_death": None,
        },
        {
            "patient_id": 6,
            "date_of_birth": date(2000, 1, 1),
            "sex": "male",
            "date_of_death": date(2020, 1, 1),
        },
        {
            "patient_id": 7,
            "date_of_birth": date(2000, 1, 1),
            "sex": "male",
            "date_of_death": None,
        },
    ]


def test_vaccinations(select_all):
    results = select_all(
        tpp.vaccinations,
        Patient(Patient_ID=1),
        VaccinationReference(VaccinationName_ID=10, VaccinationContent="foo"),
        VaccinationReference(VaccinationName_ID=10, VaccinationContent="bar"),
        Vaccination(
            Patient_ID=1,
            Vaccination_ID=123,
            VaccinationDate="2020-01-01T14:00:00",
            VaccinationName="baz",
            VaccinationName_ID=10,
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "vaccination_id": 123,
            "date": date(2020, 1, 1),
            "target_disease": "foo",
            "product_name": "baz",
        },
        {
            "patient_id": 1,
            "vaccination_id": 123,
            "date": date(2020, 1, 1),
            "target_disease": "bar",
            "product_name": "baz",
        },
    ]


def test_practice_registrations(select_all):
    results = select_all(
        tpp.practice_registrations,
        Patient(Patient_ID=1),
        Organisation(Organisation_ID=2, STPCode="abc", Region="def"),
        RegistrationHistory(
            Patient_ID=1,
            StartDate=date(2010, 1, 1),
            EndDate=date(2020, 1, 1),
            Organisation_ID=2,
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "start_date": date(2010, 1, 1),
            "end_date": date(2020, 1, 1),
            "practice_pseudo_id": 2,
            "practice_stp": "abc",
            "practice_nuts1_region_name": "def",
        }
    ]


def test_ons_deaths(select_all):
    results = select_all(
        tpp.ons_deaths,
        Patient(Patient_ID=1),
        ONSDeaths(Patient_ID=1, dod="2022-01-01", ICD10001="abc", ICD10002="def"),
    )
    assert results == [
        {
            "patient_id": 1,
            "date": date(2022, 1, 1),
            "cause_of_death_01": "abc",
            "cause_of_death_02": "def",
            "cause_of_death_03": None,
            **{f"cause_of_death_{i:02d}": None for i in range(4, 16)},
        }
    ]


def test_clinical_events(select_all):
    results = select_all(
        tpp.clinical_events,
        Patient(Patient_ID=1),
        CodedEvent(
            Patient_ID=1,
            ConsultationDate="2020-10-20T14:30:05",
            CTV3Code="xyz",
            NumericValue=0.5,
        ),
        CodedEventSnomed(
            Patient_ID=1,
            ConsultationDate="2020-11-21T09:30:00",
            ConceptID="ijk",
            NumericValue=1.2,
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "date": date(2020, 10, 20),
            "snomedct_code": None,
            "ctv3_code": "xyz",
            "numeric_value": 0.5,
        },
        {
            "patient_id": 1,
            "date": date(2020, 11, 21),
            "snomedct_code": "ijk",
            "ctv3_code": None,
            "numeric_value": 1.2,
        },
    ]


def test_medications(select_all):
    results = select_all(
        tpp.medications,
        Patient(Patient_ID=1),
        MedicationDictionary(MultilexDrug_ID="abc", DMD_ID="xyz"),
        MedicationIssue(
            Patient_ID=1, ConsultationDate="2020-05-15T10:10:10", MultilexDrug_ID="abc"
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "date": date(2020, 5, 15),
            "dmd_code": "xyz",
            "multilex_code": "abc",
        }
    ]


def test_addresses(select_all):
    results = select_all(
        tpp.addresses,
        Patient(Patient_ID=1),
        PatientAddress(
            Patient_ID=1,
            PatientAddress_ID=2,
            StartDate="2000-01-01",
            EndDate="2010-01-01",
            AddressType=3,
            RuralUrbanClassificationCode=4,
            ImdRankRounded=1000,
            MSOACode="NPC",
        ),
        PatientAddress(
            Patient_ID=1,
            PatientAddress_ID=3,
            StartDate="2010-01-01",
            EndDate="2020-01-01",
            AddressType=3,
            RuralUrbanClassificationCode=4,
            ImdRankRounded=2000,
            MSOACode="L001",
        ),
        PotentialCareHomeAddress(
            PatientAddress_ID=3,
            LocationRequiresNursing="Y",
            LocationDoesNotRequireNursing="N",
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "address_id": 2,
            "start_date": date(2000, 1, 1),
            "end_date": date(2010, 1, 1),
            "address_type": 3,
            "rural_urban_classification": 4,
            "imd_rounded": 1000,
            "msoa_code": None,
            "has_postcode": False,
            "care_home_is_potential_match": False,
            "care_home_requires_nursing": None,
            "care_home_does_not_require_nursing": None,
        },
        {
            "patient_id": 1,
            "address_id": 3,
            "start_date": date(2010, 1, 1),
            "end_date": date(2020, 1, 1),
            "address_type": 3,
            "rural_urban_classification": 4,
            "imd_rounded": 2000,
            "msoa_code": "L001",
            "has_postcode": True,
            "care_home_is_potential_match": True,
            "care_home_requires_nursing": True,
            "care_home_does_not_require_nursing": False,
        },
    ]


def test_sgss_covid_all_tests(select_all):
    results = select_all(
        tpp.sgss_covid_all_tests,
        Patient(Patient_ID=1),
        SGSS_AllTests_Positive(Patient_ID=1, Specimen_Date="2021-10-20"),
        SGSS_AllTests_Negative(Patient_ID=1, Specimen_Date="2021-11-20"),
    )
    assert results == [
        {
            "patient_id": 1,
            "specimen_taken_date": date(2021, 10, 20),
            "is_positive": True,
        },
        {
            "patient_id": 1,
            "specimen_taken_date": date(2021, 11, 20),
            "is_positive": False,
        },
    ]


def test_occupation_on_covid_vaccine_record(select_all):
    results = select_all(
        tpp.occupation_on_covid_vaccine_record,
        Patient(Patient_ID=1),
        HealthCareWorker(Patient_ID=1),
    )
    assert results == [{"patient_id": 1, "is_healthcare_worker": True}]


def test_emergency_care_attendances(select_all):
    results = select_all(
        tpp.emergency_care_attendances,
        Patient(Patient_ID=1),
        EC(
            Patient_ID=1,
            EC_Ident=2,
            Arrival_Date="2021-01-01",
            Discharge_Destination_SNOMED_CT="abc",
        ),
        EC_Diagnosis(EC_Ident=2, EC_Diagnosis_01="def", EC_Diagnosis_02="xyz"),
    )
    assert results == [
        {
            "patient_id": 1,
            "id": 2,
            "arrival_date": date(2021, 1, 1),
            "discharge_destination": "abc",
            "diagnosis_01": "def",
            "diagnosis_02": "xyz",
            "diagnosis_03": None,
            **{f"diagnosis_{i:02d}": None for i in range(4, 25)},
        }
    ]


def test_hospital_admissions(select_all):
    results = select_all(
        tpp.hospital_admissions,
        Patient(Patient_ID=1),
        APCS(
            Patient_ID=1,
            APCS_Ident=2,
            Admission_Date="2021-01-01",
            Discharge_Date="2021-01-10",
            Admission_Method="1A",
            Der_Diagnosis_All="123;456;789",
            Patient_Classification="X",
        ),
        APCS_Der(APCS_Ident=2, Spell_PbR_CC_Day="5"),
    )
    assert results == [
        {
            "patient_id": 1,
            "id": 2,
            "admission_date": date(2021, 1, 1),
            "discharge_date": date(2021, 1, 10),
            "admission_method": "1A",
            "all_diagnoses": "123;456;789",
            "patient_classification": "X",
            "days_in_critical_care": 5,
        }
    ]
