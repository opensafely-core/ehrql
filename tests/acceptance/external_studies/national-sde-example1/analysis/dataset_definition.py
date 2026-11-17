from ehrql import create_dataset, codelist_from_csv, case, when
from ehrql.tables.nationalsde import patients, artificial_hes_apc_2425
import datetime

from ehrql import claim_permissions

claim_permissions("event_level_data")


diagnosis_codes = codelist_from_csv(
    # "codelists/icd10_heart_codes.csv",
    "tests/acceptance/external_studies/national-sde-example1/codelists/icd10_heart_codes.csv",
    column="code",
    category_column="description",
)
elective_admission_methods = ["11", "12", "13"]
emergency_admission_methods = [
    "21",
    "22",
    "23",
    "24",
    "25",
    "28",
    "2A",
    "2B",
    "2C",
    "2D",
]

dataset = create_dataset()
admissions = artificial_hes_apc_2425.where(artificial_hes_apc_2425.fde == 1).where(
    artificial_hes_apc_2425.diag_4_01.is_in(diagnosis_codes)
)
elective_admissions = admissions.where(
    admissions.admimeth.is_in(elective_admission_methods)
)
emergency_admissions = admissions.where(
    admissions.admimeth.is_in(emergency_admission_methods)
)
dataset.define_population(
    elective_admissions.exists_for_patient() | emergency_admissions.exists_for_patient()
)


dataset.add_event_table(
    "elective_admissions",
    # if we were using hospital_admissions (outlined in backend/databricks), we
    # could probably add a column like hes_year="2024-25" & this could be like:
    # year=elective_admissions.hes_year
    year=case(when(elective_admissions.procodet != "").then("2024-25")),
    provider_code=elective_admissions.procodet,
    hospital_code=elective_admissions.sitetret,
    primary_diagnosis_code=elective_admissions.diag_4_01,
    primary_diagnosis_description=elective_admissions.diag_4_01.to_category(
        diagnosis_codes
    ),
)

dataset.add_event_table(
    "emergency_admissions",
    # if we were using hospital_admissions (outlined in backend/databricks), we
    # could probably add a column like hes_year="2024-25" & this could be like:
    # year=elective_admissions.hes_year
    year=case(when(elective_admissions.procodet != "").then("2024-25")),
    provider_code=emergency_admissions.procodet,
    hospital_code=emergency_admissions.sitetret,
    primary_diagnosis_code=emergency_admissions.diag_4_01,
    primary_diagnosis_description=emergency_admissions.diag_4_01.to_category(
        diagnosis_codes
    ),
)
