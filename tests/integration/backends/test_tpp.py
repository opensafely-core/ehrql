from datetime import date

import pytest
import sqlalchemy

from ehrql.backends.tpp import TPPBackend
from ehrql.query_language import BaseFrame
from ehrql.tables.beta import tpp
from tests.lib.tpp_schema import (
    APCS,
    EC,
    APCS_Der,
    Appointment,
    CodedEvent,
    CodedEvent_SNOMED,
    CustomMedicationDictionary,
    EC_Diagnosis,
    HealthCareWorker,
    Household,
    HouseholdMember,
    ISARIC_New,
    MedicationDictionary,
    MedicationIssue,
    ONS_CIS_New,
    ONS_Deaths,
    OpenPROMPT,
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


REGISTERED_TABLES = set()


# This slightly odd way of supplying the table object to the test function makes the
# tests introspectable in such a way that we can confirm that every table in the module
# is covered by a test
def register_test_for(table):
    def annotate_test_function(fn):
        REGISTERED_TABLES.add(table)
        fn._table = table
        return fn

    return annotate_test_function


@pytest.fixture
def select_all(request, mssql_database):
    try:
        ql_table = request.function._table
    except AttributeError:  # pragma: no cover
        raise RuntimeError(
            f"Function '{request.function.__name__}' needs the "
            f"`@register_test_for(table)` decorator applied"
        )

    qm_table = ql_table.qm_node
    sql_table = TPPBackend().get_table_expression(qm_table.name, qm_table.schema)
    columns = [
        # Using `type_coerce(..., None)` like this strips the type information from the
        # SQLAlchemy column meaning we get back the type that the column actually is in
        # database, not the type we've told SQLAlchemy it is.
        sqlalchemy.type_coerce(column, None).label(column.key)
        for column in sql_table.columns
    ]
    select_all_query = sqlalchemy.select(*columns)

    def _select_all(*input_data):
        mssql_database.setup(*input_data)
        with mssql_database.engine().connect() as connection:
            results = connection.execute(select_all_query)
            return [row._asdict() for row in results]

    return _select_all


@register_test_for(tpp.patients)
def test_patients(select_all):
    results = select_all(
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


@register_test_for(tpp.vaccinations)
def test_vaccinations(select_all):
    results = select_all(
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


@register_test_for(tpp.practice_registrations)
def test_practice_registrations(select_all):
    results = select_all(
        Patient(Patient_ID=1),
        Organisation(Organisation_ID=2, STPCode="abc", Region="def"),
        Organisation(Organisation_ID=3, STPCode="", Region=""),
        RegistrationHistory(
            Patient_ID=1,
            StartDate=date(2010, 1, 1),
            EndDate=date(2020, 1, 1),
            Organisation_ID=2,
        ),
        RegistrationHistory(
            Patient_ID=1,
            StartDate=date(2020, 1, 1),
            EndDate=date(2030, 1, 1),
            Organisation_ID=3,
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
        },
        {
            "patient_id": 1,
            "start_date": date(2020, 1, 1),
            "end_date": date(2030, 1, 1),
            "practice_pseudo_id": 3,
            "practice_stp": None,
            "practice_nuts1_region_name": None,
        },
    ]


@register_test_for(tpp.ons_deaths)
def test_ons_deaths(select_all):
    results = select_all(
        Patient(Patient_ID=1),
        ONS_Deaths(
            Patient_ID=1,
            dod="2022-01-01",
            Place_of_occurrence="Care Home",
            ICD10001="abc",
            ICD10002="def",
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "date": date(2022, 1, 1),
            "place": "Care Home",
            "cause_of_death_01": "abc",
            "cause_of_death_02": "def",
            "cause_of_death_03": None,
            **{f"cause_of_death_{i:02d}": None for i in range(4, 16)},
        }
    ]


@register_test_for(tpp.clinical_events)
def test_clinical_events(select_all):
    results = select_all(
        Patient(Patient_ID=1),
        CodedEvent(
            Patient_ID=1,
            ConsultationDate="2020-10-20T14:30:05",
            CTV3Code="xyz",
            NumericValue=0.5,
        ),
        CodedEvent_SNOMED(
            Patient_ID=1,
            ConsultationDate="2020-11-21T09:30:00",
            ConceptID="ijk",
            NumericValue=1.5,
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
            "numeric_value": 1.5,
        },
    ]


@register_test_for(tpp.medications)
@pytest.mark.parametrize(
    "dictionary_class", [MedicationDictionary, CustomMedicationDictionary]
)
def test_medications(select_all, dictionary_class):
    results = select_all(
        Patient(Patient_ID=1),
        dictionary_class(MultilexDrug_ID="abc", DMD_ID="xyz"),
        MedicationIssue(
            Patient_ID=1, ConsultationDate="2020-05-15T10:10:10", MultilexDrug_ID="abc"
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "date": date(2020, 5, 15),
            "dmd_code": "xyz",
        }
    ]


@register_test_for(tpp.medications)
def test_medications_prefer_dictionary_to_custom_dictionary(select_all):
    results = select_all(
        Patient(Patient_ID=1),
        MedicationDictionary(MultilexDrug_ID="abc", DMD_ID="xyz"),
        CustomMedicationDictionary(MultilexDrug_ID="abc", DMD_ID="def"),
        MedicationIssue(
            Patient_ID=1, ConsultationDate="2020-05-15T10:10:10", MultilexDrug_ID="abc"
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "date": date(2020, 5, 15),
            "dmd_code": "xyz",
        }
    ]


@register_test_for(tpp.addresses)
def test_addresses(select_all):
    results = select_all(
        Patient(Patient_ID=1),
        PatientAddress(
            Patient_ID=1,
            PatientAddress_ID=2,
            StartDate="2000-01-01T10:10:00",
            EndDate="2010-01-01T10:00:00",
            AddressType=3,
            RuralUrbanClassificationCode=4,
            ImdRankRounded=1000,
            MSOACode="NPC",
        ),
        PatientAddress(
            Patient_ID=1,
            PatientAddress_ID=3,
            StartDate="2010-01-01T10:10:00",
            EndDate="2020-01-01T10:10:00",
            AddressType=3,
            RuralUrbanClassificationCode=4,
            ImdRankRounded=2000,
            MSOACode="",
        ),
        PatientAddress(
            Patient_ID=1,
            PatientAddress_ID=4,
            StartDate="2010-01-01T10:10:00",
            EndDate="2020-01-01T10:10:00",
            AddressType=3,
            RuralUrbanClassificationCode=4,
            ImdRankRounded=2000,
            MSOACode="L001",
        ),
        PotentialCareHomeAddress(
            PatientAddress_ID=4,
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
            "msoa_code": None,
            "has_postcode": False,
            "care_home_is_potential_match": False,
            "care_home_requires_nursing": None,
            "care_home_does_not_require_nursing": None,
        },
        {
            "patient_id": 1,
            "address_id": 4,
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


@register_test_for(tpp.sgss_covid_all_tests)
def test_sgss_covid_all_tests(select_all):
    results = select_all(
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


@register_test_for(tpp.occupation_on_covid_vaccine_record)
def test_occupation_on_covid_vaccine_record(select_all):
    results = select_all(
        Patient(Patient_ID=1),
        HealthCareWorker(Patient_ID=1),
    )
    assert results == [{"patient_id": 1, "is_healthcare_worker": True}]


@register_test_for(tpp.emergency_care_attendances)
def test_emergency_care_attendances(select_all):
    results = select_all(
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


@register_test_for(tpp.hospital_admissions)
def test_hospital_admissions(select_all):
    results = select_all(
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
        APCS_Der(
            APCS_Ident=2,
            Spell_PbR_CC_Day="5",
            Spell_Primary_Diagnosis="A1;B1",
        ),
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
            "primary_diagnoses": "A1;B1",
        }
    ]


@register_test_for(tpp.appointments)
def test_appointments(select_all):
    results = select_all(
        Patient(Patient_ID=1),
        Appointment(
            Patient_ID=1,
            BookedDate="2021-01-01T09:00:00",
            StartDate="2021-01-01T09:00:00",
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "booked_date": date(2021, 1, 1),
            "start_date": date(2021, 1, 1),
        },
    ]


@register_test_for(tpp.household_memberships_2020)
def test_household_memberships_2020(select_all):
    results = select_all(
        Patient(Patient_ID=1),
        Household(
            Household_ID=123,
            HouseholdSize=5,
        ),
        HouseholdMember(
            Patient_ID=1,
            Household_ID=123,
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "household_pseudo_id": 123,
            "household_size": 5,
        },
    ]


@register_test_for(tpp.ons_cis)
def test_ons_cis(select_all):
    results = select_all(
        Patient(Patient_ID=1),
        ONS_CIS_New(
            Patient_ID=1,
            visit_date=date(2021, 10, 20),
            visit_num=1,
            last_linkage_dt=date(2022, 8, 15),
            nhs_data_share=1,
            imd_decile_E=1,
            imd_quartile_E=1,
            rural_urban=1,
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "visit_date": date(2021, 10, 20),
            "visit_num": 1,
            "is_opted_out_of_nhs_data_share": True,
            "last_linkage_dt": date(2022, 8, 15),
            "imd_decile_e": 1,
            "imd_quartile_e": 1,
            "rural_urban": 1,
        },
    ]


@register_test_for(tpp.isaric_raw)
def test_isaric_raw_dates(select_all):
    isaric_patient_keys = frozenset(tpp.isaric_raw.qm_node.schema.column_names)

    # Test date extraction with all valid date strings.
    patient_1 = dict.fromkeys(isaric_patient_keys, None)
    patient_1 |= {
        "Patient_ID": 1,
        "covid19_vaccined": "2021-02-01",
        "covid19_vaccine2d": "2021-04-01",
        "cestdat": "2022-01-01",
        "hostdat": "2022-01-07",
        "hostdat_transfer": "2022-01-10",
        "dsstdat": "2022-01-05",
        "dsstdtc": "2022-01-20",
    }
    patient_1_results = dict.fromkeys(isaric_patient_keys, None)
    patient_1_results |= {
        "patient_id": 1,
        "covid19_vaccined": date(2021, 2, 1),
        "covid19_vaccine2d": date(2021, 4, 1),
        "cestdat": date(2022, 1, 1),
        "hostdat": date(2022, 1, 7),
        "hostdat_transfer": date(2022, 1, 10),
        "dsstdat": date(2022, 1, 5),
        "dsstdtc": date(2022, 1, 20),
    }
    # Test date extraction with all "NA" strings as dates..
    patient_2 = dict.fromkeys(isaric_patient_keys, None)
    patient_2 |= {
        "Patient_ID": 2,
        "covid19_vaccined": "NA",
        "covid19_vaccine2d": "NA",
        "cestdat": "NA",
        "hostdat": "NA",
        "hostdat_transfer": "NA",
        "dsstdat": "NA",
        "dsstdtc": "NA",
    }
    patient_2_results = dict.fromkeys(isaric_patient_keys, None)
    patient_2_results |= {
        "patient_id": 2,
    }
    # Test date extraction with a mixture of valid and "NA" date strings.
    patient_3 = dict.fromkeys(isaric_patient_keys, None)
    patient_3 |= {
        "Patient_ID": 3,
        "covid19_vaccined": "NA",
        "covid19_vaccine2d": "2021-04-01",
        "cestdat": "NA",
        "hostdat": "2022-01-07",
        "hostdat_transfer": "NA",
        "dsstdat": "2022-01-05",
        "dsstdtc": "NA",
    }
    patient_3_results = dict.fromkeys(isaric_patient_keys, None)
    patient_3_results |= {
        "patient_id": 3,
        "covid19_vaccine2d": date(2021, 4, 1),
        "hostdat": date(2022, 1, 7),
        "dsstdat": date(2022, 1, 5),
    }
    results = select_all(
        Patient(Patient_ID=1),
        Patient(Patient_ID=2),
        Patient(Patient_ID=3),
        ISARIC_New(
            **patient_1,
        ),
        ISARIC_New(
            **patient_2,
        ),
        ISARIC_New(
            **patient_3,
        ),
    )
    assert results == [
        patient_1_results,
        patient_2_results,
        patient_3_results,
    ]


@register_test_for(tpp.isaric_raw)
def test_isaric_raw_clinical_variables(select_all):
    isaric_patient_keys = frozenset(tpp.isaric_raw.qm_node.schema.column_names)

    patient_1 = dict.fromkeys(isaric_patient_keys, None)
    patient_1 |= {
        "Patient_ID": 1,
        "chrincard": "YES",
        "hypertension_mhyn": "YES",
        "chronicpul_mhyn": "YES",
        "asthma_mhyn": "YES",
        "renal_mhyn": "YES",
        "mildliver": "YES",
        "modliv": "YES",
        "chronicneu_mhyn": "YES",
        "malignantneo_mhyn": "YES",
        "chronichaemo_mhyn": "YES",
        "aidshiv_mhyn": "YES",
        "obesity_mhyn": "YES",
        "diabetescom_mhyn": "YES",
        "diabetes_mhyn": "YES",
        "rheumatologic_mhyn": "YES",
        "dementia_mhyn": "YES",
        "malnutrition_mhyn": "YES",
    }
    patient_1_results = dict.fromkeys(isaric_patient_keys, None)
    patient_1_results |= {
        "patient_id": 1,
        "chrincard": "YES",
        "hypertension_mhyn": "YES",
        "chronicpul_mhyn": "YES",
        "asthma_mhyn": "YES",
        "renal_mhyn": "YES",
        "mildliver": "YES",
        "modliv": "YES",
        "chronicneu_mhyn": "YES",
        "malignantneo_mhyn": "YES",
        "chronichaemo_mhyn": "YES",
        "aidshiv_mhyn": "YES",
        "obesity_mhyn": "YES",
        "diabetescom_mhyn": "YES",
        "diabetes_mhyn": "YES",
        "rheumatologic_mhyn": "YES",
        "dementia_mhyn": "YES",
        "malnutrition_mhyn": "YES",
    }
    patient_2 = dict.fromkeys(isaric_patient_keys, None)
    patient_2 |= {
        "Patient_ID": 2,
        "chrincard": "NO",
        "hypertension_mhyn": "NO",
        "chronicpul_mhyn": "NO",
        "asthma_mhyn": "NO",
        "renal_mhyn": "NO",
        "mildliver": "NO",
        "modliv": "NO",
        "chronicneu_mhyn": "NO",
        "malignantneo_mhyn": "NO",
        "chronichaemo_mhyn": "NO",
        "aidshiv_mhyn": "NO",
        "obesity_mhyn": "NO",
        "diabetescom_mhyn": "NO",
        "diabetes_mhyn": "NO",
        "rheumatologic_mhyn": "NO",
        "dementia_mhyn": "NO",
        "malnutrition_mhyn": "NO",
    }
    patient_2_results = dict.fromkeys(isaric_patient_keys, None)
    patient_2_results |= {
        "patient_id": 2,
        "chrincard": "NO",
        "hypertension_mhyn": "NO",
        "chronicpul_mhyn": "NO",
        "asthma_mhyn": "NO",
        "renal_mhyn": "NO",
        "mildliver": "NO",
        "modliv": "NO",
        "chronicneu_mhyn": "NO",
        "malignantneo_mhyn": "NO",
        "chronichaemo_mhyn": "NO",
        "aidshiv_mhyn": "NO",
        "obesity_mhyn": "NO",
        "diabetescom_mhyn": "NO",
        "diabetes_mhyn": "NO",
        "rheumatologic_mhyn": "NO",
        "dementia_mhyn": "NO",
        "malnutrition_mhyn": "NO",
    }
    patient_3 = dict.fromkeys(isaric_patient_keys, None)
    patient_3 |= {
        "Patient_ID": 3,
        "chrincard": "Unknown",
        "hypertension_mhyn": "Unknown",
        "chronicpul_mhyn": "Unknown",
        "asthma_mhyn": "Unknown",
        "renal_mhyn": "Unknown",
        "mildliver": "Unknown",
        "modliv": "Unknown",
        "chronicneu_mhyn": "Unknown",
        "malignantneo_mhyn": "Unknown",
        "chronichaemo_mhyn": "Unknown",
        "aidshiv_mhyn": "Unknown",
        "obesity_mhyn": "Unknown",
        "diabetescom_mhyn": "Unknown",
        "diabetes_mhyn": "Unknown",
        "rheumatologic_mhyn": "Unknown",
        "dementia_mhyn": "Unknown",
        "malnutrition_mhyn": "Unknown",
    }
    patient_3_results = dict.fromkeys(isaric_patient_keys, None)
    patient_3_results |= {
        "patient_id": 3,
        "chrincard": "Unknown",
        "hypertension_mhyn": "Unknown",
        "chronicpul_mhyn": "Unknown",
        "asthma_mhyn": "Unknown",
        "renal_mhyn": "Unknown",
        "mildliver": "Unknown",
        "modliv": "Unknown",
        "chronicneu_mhyn": "Unknown",
        "malignantneo_mhyn": "Unknown",
        "chronichaemo_mhyn": "Unknown",
        "aidshiv_mhyn": "Unknown",
        "obesity_mhyn": "Unknown",
        "diabetescom_mhyn": "Unknown",
        "diabetes_mhyn": "Unknown",
        "rheumatologic_mhyn": "Unknown",
        "dementia_mhyn": "Unknown",
        "malnutrition_mhyn": "Unknown",
    }
    patient_4 = dict.fromkeys(isaric_patient_keys, None)
    patient_4 |= {
        "Patient_ID": 4,
        "chrincard": "NA",
        "hypertension_mhyn": "NA",
        "chronicpul_mhyn": "NA",
        "asthma_mhyn": "NA",
        "renal_mhyn": "NA",
        "mildliver": "NA",
        "modliv": "NA",
        "chronicneu_mhyn": "NA",
        "malignantneo_mhyn": "NA",
        "chronichaemo_mhyn": "NA",
        "aidshiv_mhyn": "NA",
        "obesity_mhyn": "NA",
        "diabetescom_mhyn": "NA",
        "diabetes_mhyn": "NA",
        "rheumatologic_mhyn": "NA",
        "dementia_mhyn": "NA",
        "malnutrition_mhyn": "NA",
    }
    patient_4_results = dict.fromkeys(isaric_patient_keys, None)
    patient_4_results |= {
        "patient_id": 4,
        "chrincard": "NO",
        "hypertension_mhyn": "NO",
        "chronicpul_mhyn": "NO",
        "asthma_mhyn": "NO",
        "renal_mhyn": "NO",
        "mildliver": "NO",
        "modliv": "NO",
        "chronicneu_mhyn": "NO",
        "malignantneo_mhyn": "NO",
        "chronichaemo_mhyn": "NO",
        "aidshiv_mhyn": "NO",
        "obesity_mhyn": "NO",
        "diabetescom_mhyn": "NO",
        "diabetes_mhyn": "NO",
        "rheumatologic_mhyn": "NO",
        "dementia_mhyn": "NO",
        "malnutrition_mhyn": "NO",
    }
    patient_5 = dict.fromkeys(isaric_patient_keys, None)
    patient_5 |= {
        "Patient_ID": 5,
        "chrincard": "YES",
        "hypertension_mhyn": "NO",
        "chronicpul_mhyn": "Unknown",
        "asthma_mhyn": "NA",
        "renal_mhyn": "YES",
        "mildliver": "NO",
        "modliv": "Unknown",
        "chronicneu_mhyn": "NA",
        "malignantneo_mhyn": "YES",
        "chronichaemo_mhyn": "NO",
        "aidshiv_mhyn": "Unknown",
        "obesity_mhyn": "NA",
        "diabetescom_mhyn": "YES",
        "diabetes_mhyn": "NO",
        "rheumatologic_mhyn": "Unknown",
        "dementia_mhyn": "NA",
        "malnutrition_mhyn": "YES",
    }
    patient_5_results = dict.fromkeys(isaric_patient_keys, None)
    patient_5_results |= {
        "patient_id": 5,
        "chrincard": "YES",
        "hypertension_mhyn": "NO",
        "chronicpul_mhyn": "Unknown",
        "asthma_mhyn": "NO",
        "renal_mhyn": "YES",
        "mildliver": "NO",
        "modliv": "Unknown",
        "chronicneu_mhyn": "NO",
        "malignantneo_mhyn": "YES",
        "chronichaemo_mhyn": "NO",
        "aidshiv_mhyn": "Unknown",
        "obesity_mhyn": "NO",
        "diabetescom_mhyn": "YES",
        "diabetes_mhyn": "NO",
        "rheumatologic_mhyn": "Unknown",
        "dementia_mhyn": "NO",
        "malnutrition_mhyn": "YES",
    }
    patient_6 = dict.fromkeys(isaric_patient_keys, None)
    patient_6 |= {
        "Patient_ID": 6,
        "diabetes_type_mhyn": "No",
        "smoking_mhyn": "Yes",
    }
    patient_6_results = dict.fromkeys(isaric_patient_keys, None)
    patient_6_results |= {
        "patient_id": 6,
        "diabetes_type_mhyn": "No",
        "smoking_mhyn": "Yes",
    }
    patient_7 = dict.fromkeys(isaric_patient_keys, None)
    patient_7 |= {
        "Patient_ID": 7,
        "diabetes_type_mhyn": "1",
        "smoking_mhyn": "Never Smoked",
    }
    patient_7_results = dict.fromkeys(isaric_patient_keys, None)
    patient_7_results |= {
        "patient_id": 7,
        "diabetes_type_mhyn": "1",
        "smoking_mhyn": "Never Smoked",
    }
    patient_8 = dict.fromkeys(isaric_patient_keys, None)
    patient_8 |= {
        "Patient_ID": 8,
        "diabetes_type_mhyn": "2",
        "smoking_mhyn": "Former Smoker",
    }
    patient_8_results = dict.fromkeys(isaric_patient_keys, None)
    patient_8_results |= {
        "patient_id": 8,
        "diabetes_type_mhyn": "2",
        "smoking_mhyn": "Former Smoker",
    }
    patient_8 = dict.fromkeys(isaric_patient_keys, None)
    patient_8 |= {
        "Patient_ID": 8,
        "diabetes_type_mhyn": "N/K",
        "smoking_mhyn": "N/K",
    }
    patient_8_results = dict.fromkeys(isaric_patient_keys, None)
    patient_8_results |= {
        "patient_id": 8,
        "diabetes_type_mhyn": "N/K",
        "smoking_mhyn": "N/K",
    }
    patient_9 = dict.fromkeys(isaric_patient_keys, None)
    patient_9 |= {
        "Patient_ID": 9,
        "diabetes_type_mhyn": "N/K",
        "smoking_mhyn": "N/K",
    }
    patient_9_results = dict.fromkeys(isaric_patient_keys, None)
    patient_9_results |= {
        "patient_id": 9,
        "diabetes_type_mhyn": "N/K",
        "smoking_mhyn": "N/K",
    }
    results = select_all(
        Patient(Patient_ID=1),
        Patient(Patient_ID=2),
        Patient(Patient_ID=3),
        Patient(Patient_ID=4),
        Patient(Patient_ID=5),
        Patient(Patient_ID=6),
        Patient(Patient_ID=7),
        Patient(Patient_ID=8),
        Patient(Patient_ID=9),
        ISARIC_New(
            **patient_1,
        ),
        ISARIC_New(
            **patient_2,
        ),
        ISARIC_New(
            **patient_3,
        ),
        ISARIC_New(
            **patient_4,
        ),
        ISARIC_New(
            **patient_5,
        ),
        ISARIC_New(
            **patient_6,
        ),
        ISARIC_New(
            **patient_7,
        ),
        ISARIC_New(
            **patient_8,
        ),
        ISARIC_New(
            **patient_9,
        ),
    )
    assert results == [
        patient_1_results,
        patient_2_results,
        patient_3_results,
        patient_4_results,
        patient_5_results,
        patient_6_results,
        patient_7_results,
        patient_8_results,
        patient_9_results,
    ]


@register_test_for(tpp.open_prompt)
def test_open_prompt(select_all):
    results = select_all(
        OpenPROMPT(
            Patient_ID=1,
            CodedEvent_ID="00000",
            CodeSystemId=0,  # SNOMED CT
            ConceptId="100000",
            ConsultationDate="2023-01-01",
            Consultation_ID=1,
            NumericValue=1.0,
        ),
        OpenPROMPT(
            Patient_ID=2,
            CodedEvent_ID="Y0000",
            CodeSystemId=2,  # CTV3 "Y"
            ConceptId="Y0000",
            ConsultationDate="2023-01-01",
            Consultation_ID=2,
            NumericValue=1.0,
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "ctv3_code": "00000",
            "snomedct_code": "100000",
            "consultation_date": date(2023, 1, 1),
            "consultation_id": 1,
            "numeric_value": 1.0,
        },
        {
            "patient_id": 2,
            "ctv3_code": "Y0000",
            "snomedct_code": None,
            "consultation_date": date(2023, 1, 1),
            "consultation_id": 2,
            "numeric_value": 1.0,
        },
    ]


def test_registered_tests_are_exhaustive():
    for name, table in vars(tpp).items():
        if not isinstance(table, BaseFrame):
            continue
        assert table in REGISTERED_TABLES, f"No test for {tpp.__name__}.{name}"
