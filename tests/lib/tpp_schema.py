# This file is auto-generated: DO NOT EDIT IT
#
# To rebuild run:
#
#   python tests/lib/update_tpp_schema.py build
#

from sqlalchemy import types as t
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    "Common base class to signal that models below belong to the same database"


# This table isn't included in the schema definition TPP provide for us because it isn't
# created or managed by TPP. Instead we create and populate this table ourselves,
# via a command in tpp-database-utils:
# [1]: https://github.com/opensafely-core/tpp-database-utils/blob/1c78b0777463ba73aa14abd52159a4398ff47ce7/tpp_database_utils/custom_medication_dictionary.py
class CustomMedicationDictionary(Base):
    __tablename__ = "CustomMedicationDictionary"
    # Because we don't have write privileges on the main TPP database schema this table
    # lives in our "temporary tables" database. To mimic this as closely as possible in
    # testing we create it in a separate schema from the other tables.
    __table_args__ = {"schema": "temp_tables.dbo"}

    _pk = mapped_column(t.Integer, primary_key=True)

    DMD_ID = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    MultilexDrug_ID = mapped_column(t.VARCHAR(767, collation="Latin1_General_CI_AS"))


class APCS(Base):
    __tablename__ = "APCS"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Administrative_Category = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Admission_Date = mapped_column(t.Date)
    Admission_Method = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Carer_Support_Indicator = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(6, collation="Latin1_General_CI_AS"))
    Der_Admit_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Diagnosis_All = mapped_column(t.VARCHAR(4000, collation="Latin1_General_CI_AS"))
    Der_Diagnosis_Count = mapped_column(t.Integer)
    Der_Dischg_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Financial_Year = mapped_column(t.VARCHAR(7, collation="Latin1_General_CI_AS"))
    Der_Procedure_All = mapped_column(t.VARCHAR(4000, collation="Latin1_General_CI_AS"))
    Der_Procedure_Count = mapped_column(t.Integer)
    Der_Pseudo_Patient_Pathway_ID = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Der_Spell_LoS = mapped_column(t.Integer)
    Discharge_Date = mapped_column(t.Date)
    Discharge_Destination = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Discharge_Method = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Duration_of_Elective_Wait = mapped_column(t.Integer)
    Ethnic_Group = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Hospital_Spell_Duration = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Patient_Classification = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Provider_Org_Code_Type = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Source_of_Admission = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Spell_Core_HRG_SUS = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Spell_HRG_Version_No_SUS = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )


class APCS_ARCHIVED(Base):
    __tablename__ = "APCS_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Administrative_Category = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Admission_Date = mapped_column(t.Date)
    Admission_Method = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Carer_Support_Indicator = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(6, collation="Latin1_General_CI_AS"))
    Der_Admit_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Diagnosis_All = mapped_column(t.VARCHAR(4000, collation="Latin1_General_CI_AS"))
    Der_Diagnosis_Count = mapped_column(t.Integer)
    Der_Dischg_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Financial_Year = mapped_column(t.VARCHAR(7, collation="Latin1_General_CI_AS"))
    Der_Procedure_All = mapped_column(t.VARCHAR(4000, collation="Latin1_General_CI_AS"))
    Der_Procedure_Count = mapped_column(t.Integer)
    Der_Pseudo_Patient_Pathway_ID = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Der_Spell_LoS = mapped_column(t.Integer)
    Discharge_Date = mapped_column(t.Date)
    Discharge_Destination = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Discharge_Method = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Duration_of_Elective_Wait = mapped_column(t.Integer)
    Ethnic_Group = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Hospital_Spell_Duration = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Patient_Classification = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Provider_Org_Code_Type = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Source_of_Admission = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Spell_Core_HRG_SUS = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Spell_HRG_Version_No_SUS = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )


class APCS_ARCHIVED_Old(Base):
    __tablename__ = "APCS_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Administrative_Category = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Admission_Date = mapped_column(t.Date)
    Admission_Method = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Carer_Support_Indicator = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(6, collation="Latin1_General_CI_AS"))
    Der_Admit_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Diagnosis_All = mapped_column(t.VARCHAR(4000, collation="Latin1_General_CI_AS"))
    Der_Diagnosis_Count = mapped_column(t.Integer)
    Der_Dischg_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Financial_Year = mapped_column(t.VARCHAR(7, collation="Latin1_General_CI_AS"))
    Der_Procedure_All = mapped_column(t.VARCHAR(4000, collation="Latin1_General_CI_AS"))
    Der_Procedure_Count = mapped_column(t.Integer)
    Der_Pseudo_Patient_Pathway_ID = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Der_Spell_LoS = mapped_column(t.Integer)
    Discharge_Date = mapped_column(t.Date)
    Discharge_Destination = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Discharge_Method = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Duration_of_Elective_Wait = mapped_column(t.Integer)
    Ethnic_Group = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Hospital_Spell_Duration = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Patient_Classification = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Provider_Org_Code_Type = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Source_of_Admission = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Spell_Core_HRG_SUS = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Spell_HRG_Version_No_SUS = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )


class APCS_Cost(Base):
    __tablename__ = "APCS_Cost"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    Tariff_Initial_Amount = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class APCS_Cost_ARCHIVED(Base):
    __tablename__ = "APCS_Cost_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    Tariff_Initial_Amount = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class APCS_Cost_ARCHIVED_Old(Base):
    __tablename__ = "APCS_Cost_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    Tariff_Initial_Amount = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class APCS_Cost_JRC20231009_LastFilesToContainAllHistoricalCostData(Base):
    __tablename__ = "APCS_Cost_JRC20231009_LastFilesToContainAllHistoricalCostData"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    Tariff_Initial_Amount = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class APCS_Cost_JRC20251022_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = "APCS_Cost_JRC20251022_BeforeOldFinancialYearDataRemoved"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    Tariff_Initial_Amount = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class APCS_Der(Base):
    __tablename__ = "APCS_Der"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Spell_Dominant_Procedure = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Spell_LoS = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Spell_Main_Specialty_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Spell_PbR_CC_Day = mapped_column(t.VARCHAR(4, collation="Latin1_General_CI_AS"))
    Spell_PbR_Rehab_Days = mapped_column(t.VARCHAR(4, collation="Latin1_General_CI_AS"))
    Spell_Primary_Diagnosis = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Spell_RE30_Admit_Type = mapped_column(
        t.VARCHAR(1, collation="Latin1_General_CI_AS")
    )
    Spell_RE30_Indicator = mapped_column(t.VARCHAR(1, collation="Latin1_General_CI_AS"))
    Spell_Secondary_Diagnosis = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Spell_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )


class APCS_Der_ARCHIVED(Base):
    __tablename__ = "APCS_Der_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Spell_Dominant_Procedure = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Spell_LoS = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Spell_Main_Specialty_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Spell_PbR_CC_Day = mapped_column(t.VARCHAR(4, collation="Latin1_General_CI_AS"))
    Spell_PbR_Rehab_Days = mapped_column(t.VARCHAR(4, collation="Latin1_General_CI_AS"))
    Spell_Primary_Diagnosis = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Spell_RE30_Admit_Type = mapped_column(
        t.VARCHAR(1, collation="Latin1_General_CI_AS")
    )
    Spell_RE30_Indicator = mapped_column(t.VARCHAR(1, collation="Latin1_General_CI_AS"))
    Spell_Secondary_Diagnosis = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Spell_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )


class APCS_Der_ARCHIVED_Old(Base):
    __tablename__ = "APCS_Der_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Spell_Dominant_Procedure = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Spell_LoS = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Spell_Main_Specialty_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Spell_PbR_CC_Day = mapped_column(t.VARCHAR(4, collation="Latin1_General_CI_AS"))
    Spell_PbR_Rehab_Days = mapped_column(t.VARCHAR(4, collation="Latin1_General_CI_AS"))
    Spell_Primary_Diagnosis = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Spell_RE30_Admit_Type = mapped_column(
        t.VARCHAR(1, collation="Latin1_General_CI_AS")
    )
    Spell_RE30_Indicator = mapped_column(t.VARCHAR(1, collation="Latin1_General_CI_AS"))
    Spell_Secondary_Diagnosis = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Spell_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )


class APCS_Der_JRC20231009_LastFilesToContainAllHistoricalCostData(Base):
    __tablename__ = "APCS_Der_JRC20231009_LastFilesToContainAllHistoricalCostData"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Spell_Dominant_Procedure = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Spell_LoS = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Spell_Main_Specialty_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Spell_PbR_CC_Day = mapped_column(t.VARCHAR(4, collation="Latin1_General_CI_AS"))
    Spell_PbR_Rehab_Days = mapped_column(t.VARCHAR(4, collation="Latin1_General_CI_AS"))
    Spell_Primary_Diagnosis = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Spell_RE30_Admit_Type = mapped_column(
        t.VARCHAR(1, collation="Latin1_General_CI_AS")
    )
    Spell_RE30_Indicator = mapped_column(t.VARCHAR(1, collation="Latin1_General_CI_AS"))
    Spell_Secondary_Diagnosis = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Spell_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )


class APCS_Der_JRC20251022_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = "APCS_Der_JRC20251022_BeforeOldFinancialYearDataRemoved"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Spell_Dominant_Procedure = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Spell_LoS = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Spell_Main_Specialty_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Spell_PbR_CC_Day = mapped_column(t.VARCHAR(4, collation="Latin1_General_CI_AS"))
    Spell_PbR_Rehab_Days = mapped_column(t.VARCHAR(4, collation="Latin1_General_CI_AS"))
    Spell_Primary_Diagnosis = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Spell_RE30_Admit_Type = mapped_column(
        t.VARCHAR(1, collation="Latin1_General_CI_AS")
    )
    Spell_RE30_Indicator = mapped_column(t.VARCHAR(1, collation="Latin1_General_CI_AS"))
    Spell_Secondary_Diagnosis = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Spell_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )


class APCS_JRC20231009_LastFilesToContainAllHistoricalCostData(Base):
    __tablename__ = "APCS_JRC20231009_LastFilesToContainAllHistoricalCostData"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Administrative_Category = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Admission_Date = mapped_column(t.Date)
    Admission_Method = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Carer_Support_Indicator = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(6, collation="Latin1_General_CI_AS"))
    Der_Admit_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Diagnosis_All = mapped_column(t.VARCHAR(4000, collation="Latin1_General_CI_AS"))
    Der_Diagnosis_Count = mapped_column(t.Integer)
    Der_Dischg_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Financial_Year = mapped_column(t.VARCHAR(7, collation="Latin1_General_CI_AS"))
    Der_Procedure_All = mapped_column(t.VARCHAR(4000, collation="Latin1_General_CI_AS"))
    Der_Procedure_Count = mapped_column(t.Integer)
    Der_Pseudo_Patient_Pathway_ID = mapped_column(t.BIGINT)
    Der_Spell_LoS = mapped_column(t.Integer)
    Discharge_Date = mapped_column(t.Date)
    Discharge_Destination = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Discharge_Method = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Duration_of_Elective_Wait = mapped_column(t.Integer)
    Ethnic_Group = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Hospital_Spell_Duration = mapped_column(t.Integer)
    Patient_Classification = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Provider_Org_Code_Type = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Source_of_Admission = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Spell_Core_HRG_SUS = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Spell_HRG_Version_No_SUS = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )


class APCS_JRC20251022_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = "APCS_JRC20251022_BeforeOldFinancialYearDataRemoved"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    APCS_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Administrative_Category = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Admission_Date = mapped_column(t.Date)
    Admission_Method = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Carer_Support_Indicator = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(6, collation="Latin1_General_CI_AS"))
    Der_Admit_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Diagnosis_All = mapped_column(t.VARCHAR(4000, collation="Latin1_General_CI_AS"))
    Der_Diagnosis_Count = mapped_column(t.Integer)
    Der_Dischg_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Financial_Year = mapped_column(t.VARCHAR(7, collation="Latin1_General_CI_AS"))
    Der_Procedure_All = mapped_column(t.VARCHAR(4000, collation="Latin1_General_CI_AS"))
    Der_Procedure_Count = mapped_column(t.Integer)
    Der_Pseudo_Patient_Pathway_ID = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Der_Spell_LoS = mapped_column(t.Integer)
    Discharge_Date = mapped_column(t.Date)
    Discharge_Destination = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Discharge_Method = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Duration_of_Elective_Wait = mapped_column(t.Integer)
    Ethnic_Group = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Hospital_Spell_Duration = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Patient_Classification = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Provider_Org_Code_Type = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Source_of_Admission = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Spell_Core_HRG_SUS = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Spell_HRG_Version_No_SUS = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )


class AllowedPatientsWithTypeOneDissent(Base):
    __tablename__ = "AllowedPatientsWithTypeOneDissent"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)


class Appointment(Base):
    __tablename__ = "Appointment"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Appointment_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ArrivedDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    BookedDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    EndDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    FinishedDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Organisation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    SeenDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    StartDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    Status = mapped_column(t.Integer, nullable=False, default=0)


class Appointment_BUILDING(Base):
    __tablename__ = "Appointment_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Appointment_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ArrivedDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    BookedDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    EndDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    FinishedDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Organisation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    SeenDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    StartDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    Status = mapped_column(t.Integer, nullable=False, default=0)


class BuildInfo(Base):
    __tablename__ = "BuildInfo"
    _pk = mapped_column(t.Integer, primary_key=True)

    BuildDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    BuildDesc = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    BuildNumber = mapped_column(t.Integer, nullable=False, default=0)


class BuildProgress(Base):
    __tablename__ = "BuildProgress"
    _pk = mapped_column(t.Integer, primary_key=True)

    BuildStart = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Duration = mapped_column(t.Integer, nullable=False, default=0)
    Event = mapped_column(
        t.VARCHAR(1350, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    EventEnd = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    EventStart = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )


class CPNS(Base):
    __tablename__ = "CPNS"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Age = mapped_column(t.Integer)
    CovidTestResult = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    DateOfAdmission = mapped_column(t.Date)
    DateOfDeath = mapped_column(t.Date)
    DateOfResult = mapped_column(t.Date)
    DateOfSwabbed = mapped_column(t.Date)
    Der_Ethnic_Category_Description = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Der_Latest_SUS_Attendance_Date_For_Ethnicity = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Der_Source_Dataset_For_Ethnicty = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    DetainedUnderMHAct = mapped_column(t.Boolean)
    HadLearningDisability = mapped_column(
        t.VARCHAR(10, collation="Latin1_General_CI_AS")
    )
    Id = mapped_column(t.BIGINT, nullable=False, default=0)
    LearningDisabilityType = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    LocationOfDeath = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    NHSworker = mapped_column(t.Boolean)
    NationalApproved = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    NationalApprovedDate = mapped_column(t.Date)
    OnDeathCertificateNotice = mapped_column(t.Boolean)
    OrganisationTypeLot = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    PreExistingCondition = mapped_column(
        t.VARCHAR(10, collation="Latin1_General_CI_AS")
    )
    PreExistingConditionList = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    ReceivedTreatmentForMentalHealth = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    RegionApproved = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    RegionCode = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    RegionName = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    RegionalApprovedDate = mapped_column(t.Date)
    RelativesAware = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Sex = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    TransferredFromAMentalHealthSetting = mapped_column(t.Boolean)
    TransferredFromLearningDisabilityAutismSetting = mapped_column(t.Boolean)
    TravelHistory = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    snapDate = mapped_column(t.Date)


class CTV3Dictionary(Base):
    __tablename__ = "CTV3Dictionary"
    _pk = mapped_column(t.Integer, primary_key=True)

    CTV3Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_BIN"), nullable=False, default=""
    )
    Description = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class CTV3Dictionary_BUILDING(Base):
    __tablename__ = "CTV3Dictionary_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    CTV3Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_BIN"), nullable=False, default=""
    )
    Description = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class CTV3Hierarchy(Base):
    __tablename__ = "CTV3Hierarchy"
    _pk = mapped_column(t.Integer, primary_key=True)

    ChildCTV3Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_BIN"), nullable=False, default=""
    )
    ChildCTV3Description = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    ChildToParentDistance = mapped_column(t.Integer, nullable=False, default=0)
    ParentCTV3Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_BIN"), nullable=False, default=""
    )
    ParentCTV3Description = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class CTV3Hierarchy_BUILDING(Base):
    __tablename__ = "CTV3Hierarchy_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    ChildCTV3Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_BIN"), nullable=False, default=""
    )
    ChildCTV3Description = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    ChildToParentDistance = mapped_column(t.Integer, nullable=False, default=0)
    ParentCTV3Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_BIN"), nullable=False, default=""
    )
    ParentCTV3Description = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class ClusterRandomisedTrial(Base):
    __tablename__ = "ClusterRandomisedTrial"
    _pk = mapped_column(t.Integer, primary_key=True)

    Organisation_ID = mapped_column(t.Integer)
    TrialArm = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    TrialNumber = mapped_column(t.Integer)


class ClusterRandomisedTrialDetail(Base):
    __tablename__ = "ClusterRandomisedTrialDetail"
    _pk = mapped_column(t.Integer, primary_key=True)

    Organisation_ID = mapped_column(t.Integer)
    Property = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    PropertyValue = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    TrialNumber = mapped_column(t.Integer)


class ClusterRandomisedTrialReference(Base):
    __tablename__ = "ClusterRandomisedTrialReference"
    _pk = mapped_column(t.Integer, primary_key=True)

    CPMSNumber = mapped_column(t.Integer)
    TrialDescription = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    TrialName = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    TrialNumber = mapped_column(t.Integer)


class CodeCountIndicator(Base):
    __tablename__ = "CodeCountIndicator"
    _pk = mapped_column(t.Integer, primary_key=True)

    CTV3Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_BIN"), nullable=False, default=""
    )
    CodeCountIndicator = mapped_column(t.Float)


class CodedEvent(Base):
    __tablename__ = "CodedEvent"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    CTV3Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_BIN"), nullable=False, default=""
    )
    CodedEvent_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ConsultationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Consultation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    NumericValue = mapped_column(t.REAL, nullable=False, default=0.0)


class CodedEventRange(Base):
    __tablename__ = "CodedEventRange"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.Integer, nullable=False, default=0)
    CodedEventRange_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    CodedEvent_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Comparator = mapped_column(t.SMALLINT, nullable=False, default=0)
    Consultation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    LowerBound = mapped_column(t.REAL, nullable=False, default=0.0)
    UpperBound = mapped_column(t.REAL, nullable=False, default=0.0)


class CodedEventRange_BUILDING(Base):
    __tablename__ = "CodedEventRange_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.Integer, nullable=False, default=0)
    CodedEventRange_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    CodedEvent_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Comparator = mapped_column(t.SMALLINT, nullable=False, default=0)
    Consultation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    LowerBound = mapped_column(t.REAL, nullable=False, default=0.0)
    UpperBound = mapped_column(t.REAL, nullable=False, default=0.0)


class CodedEvent_BUILDING(Base):
    __tablename__ = "CodedEvent_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    CTV3Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_BIN"), nullable=False, default=""
    )
    CodedEvent_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ConsultationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Consultation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    NumericValue = mapped_column(t.REAL, nullable=False, default=0.0)


class CodedEvent_SNOMED(Base):
    __tablename__ = "CodedEvent_SNOMED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    CodeSystemId = mapped_column(t.Integer, nullable=False, default=0)
    CodedEvent_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ConceptId = mapped_column(t.VARCHAR(50, collation="Latin1_General_BIN"))
    ConsultationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Consultation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    NumericValue = mapped_column(t.REAL, nullable=False, default=0.0)


class Consultation(Base):
    __tablename__ = "Consultation"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ConsultationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Consultation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Registration_ID = mapped_column(t.BIGINT, nullable=False, default=0)


class Consultation_BUILDING(Base):
    __tablename__ = "Consultation_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ConsultationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Consultation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Registration_ID = mapped_column(t.BIGINT, nullable=False, default=0)


class DataDictionary(Base):
    __tablename__ = "DataDictionary"
    _pk = mapped_column(t.Integer, primary_key=True)

    Code = mapped_column(t.VARCHAR(255, collation="Latin1_General_CI_AS"))
    Description = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Table = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Type = mapped_column(t.VARCHAR(255, collation="Latin1_General_CI_AS"))


class DataDictionary_BUILDING(Base):
    __tablename__ = "DataDictionary_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    Code = mapped_column(t.VARCHAR(255, collation="Latin1_General_CI_AS"))
    Description = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Table = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Type = mapped_column(t.VARCHAR(255, collation="Latin1_General_CI_AS"))


class DecisionSupportValue(Base):
    __tablename__ = "DecisionSupportValue"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.Integer)
    AlgorithmType = mapped_column(t.Integer)
    CalculationDateTime = mapped_column(t.DateTime)
    NumericValue = mapped_column(t.REAL)


class DecisionSupportValueReference(Base):
    __tablename__ = "DecisionSupportValueReference"
    _pk = mapped_column(t.Integer, primary_key=True)

    AlgorithmDescription = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    AlgorithmSourceLink = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    AlgorithmType = mapped_column(t.Integer)
    AlgorithmVersion = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))


class EC(Base):
    __tablename__ = "EC"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Arrival_Date = mapped_column(t.Date)
    Arrival_Time = mapped_column(t.Time)
    DQ_Chief_Complaint_Completed = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Chief_Complaint_Expected = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Chief_Complaint_Valid = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Completed = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Expected = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Valid = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Decision_To_Admit_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(6, collation="Latin1_General_CI_AS"))
    Der_EC_Diagnosis_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_EC_Investigation_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_EC_Treatment_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_Financial_Year = mapped_column(t.VARCHAR(7, collation="Latin1_General_CI_AS"))
    Discharge_Destination_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Arrival_Mode_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_AttendanceCategory = mapped_column(
        t.VARCHAR(1, collation="Latin1_General_CI_AS")
    )
    EC_Attendance_Source_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Chief_Complaint_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Decision_To_Admit_Date = mapped_column(t.Date)
    EC_Department_Type = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Injury_Date = mapped_column(t.Date)
    Ethnic_Category = mapped_column(t.VARCHAR(1, collation="Latin1_General_CI_AS"))
    SUS_Final_Price = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    SUS_HRG_Code = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    SUS_Tariff = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))


class ECDS(Base):
    __tablename__ = "ECDS"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Accessible_Information_Professional_Required_Code_Approved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Accessible_Information_Professional_Required_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    Accommodation_Status_Code_Approved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Accommodation_Status_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    Age_At_Arrival = mapped_column(t.BIGINT)
    Age_Range = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Age_at_CDS_Activity_Date = mapped_column(t.BIGINT)
    Arrival_Date = mapped_column(t.DateTime)
    Arrival_Mode_Approved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Arrival_Month = mapped_column(t.BIGINT)
    Arrival_Planned = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Arrival_Time = mapped_column(t.VARCHAR(8, collation="Latin1_General_CI_AS"))
    Attendance_Source_Organisation = mapped_column(
        t.VARCHAR(9, collation="Latin1_General_CI_AS")
    )
    CDS_Activity_Date = mapped_column(t.Date)
    CDS_Group_Indicator = mapped_column(t.BIGINT)
    CDS_Interchange_Sender_Identity = mapped_column(
        t.VARCHAR(12, collation="Latin1_General_CI_AS")
    )
    CDS_Prime_Recipient_Identity = mapped_column(
        t.VARCHAR(12, collation="Latin1_General_CI_AS")
    )
    CDS_Type = mapped_column(t.VARCHAR(3, collation="Latin1_General_CI_AS"))
    Cancer_Registry = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Clinical_Acuity_Code_Approved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Clinical_Chief_Complaint_Code_Approved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Clinical_Chief_Complaint_Extended_Code = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    Clinical_Chief_Complaint_Injury_Related = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Clinical_Disease_Notification = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS")
    )
    Clinical_Injury_Activity_Status_Code_Approved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Clinical_Injury_Activity_Type_Code_Approved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Clinical_Injury_Intent_Code_Approved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Clinical_Injury_Place_Type_Approved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Clinical_Trial_Code = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    Commissioner_Code = mapped_column(t.VARCHAR(12, collation="Latin1_General_CI_AS"))
    DQ_Chief_Complaint_Completed = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Chief_Complaint_Expected = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Chief_Complaint_Valid = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Completed = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Expected = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Valid = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Decision_To_Admit_Receiving_Site = mapped_column(
        t.VARCHAR(9, collation="Latin1_General_CI_AS")
    )
    Decision_To_Admit_Treatment_Function_Code = mapped_column(
        t.VARCHAR(8, collation="Latin1_General_CI_AS")
    )
    Der_AEA_Diagnosis_All = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    Der_AEA_Investigation_All = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    Der_AEA_Patient_Group = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Der_AEA_Treatment_All = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(6, collation="Latin1_General_CI_AS"))
    Der_Age_At_CDS_Activity_Date = mapped_column(t.Integer)
    Der_Commissioner_Code = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Der_Dupe_Flag = mapped_column(t.Integer)
    Der_EC_Arrival_Date_Time = mapped_column(t.DateTime)
    Der_EC_Departure_Date_Time = mapped_column(t.DateTime)
    Der_EC_Diagnosis_All = mapped_column(
        t.VARCHAR(500, collation="Latin1_General_CI_AS")
    )
    Der_EC_Duration = mapped_column(t.Integer)
    Der_EC_Investigation_All = mapped_column(
        t.VARCHAR(500, collation="Latin1_General_CI_AS")
    )
    Der_EC_Treatment_All = mapped_column(
        t.VARCHAR(500, collation="Latin1_General_CI_AS")
    )
    Der_Financial_Year = mapped_column(
        t.VARCHAR(7, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    Der_Number_AEA_Diagnosis = mapped_column(t.Integer)
    Der_Number_AEA_Investigation = mapped_column(t.Integer)
    Der_Number_AEA_Treatment = mapped_column(t.Integer)
    Der_Number_EC_Diagnosis = mapped_column(t.Integer)
    Der_Number_EC_Investigation = mapped_column(t.Integer)
    Der_Number_EC_Treatment = mapped_column(t.Integer)
    Der_Provider_Code = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Der_Provider_Site_Code = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Der_Record_Type = mapped_column(t.VARCHAR(4, collation="Latin1_General_CI_AS"))
    DischargeDestinationApproved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Discharge_Destination_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    Discharge_Follow_Up_Approved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Discharge_Follow_Up_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    Discharge_Information_Given_Approved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Discharge_Information_Given_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    EC_Acuity_SNOMED_CT = mapped_column(t.VARCHAR(18, collation="Latin1_General_CI_AS"))
    EC_Arrival_Mode_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    EC_AttendanceCategory = mapped_column(
        t.VARCHAR(1, collation="Latin1_General_CI_AS")
    )
    EC_Attendance_Source_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    EC_Chief_Complaint_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    EC_Conclusion_Date = mapped_column(t.Date)
    EC_Conclusion_Time = mapped_column(t.VARCHAR(8, collation="Latin1_General_CI_AS"))
    EC_Conclusion_Time_Since_Arrival = mapped_column(t.BIGINT)
    EC_Decision_To_Admit_Date = mapped_column(t.Date)
    EC_Decision_To_Admit_Time = mapped_column(
        t.VARCHAR(8, collation="Latin1_General_CI_AS")
    )
    EC_Decision_To_Admit_Time_Since_Arrival = mapped_column(t.BIGINT)
    EC_Department_Type = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    EC_Departure_Date = mapped_column(t.Date)
    EC_Departure_Time = mapped_column(t.VARCHAR(8, collation="Latin1_General_CI_AS"))
    EC_Departure_Time_Since_Arrival = mapped_column(t.BIGINT)
    EC_Discharge_Status_Approved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    EC_Discharge_Status_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    EC_Ident = mapped_column(t.BIGINT)
    EC_Initial_Assessment_Date = mapped_column(t.Date)
    EC_Initial_Assessment_Time = mapped_column(
        t.VARCHAR(8, collation="Latin1_General_CI_AS")
    )
    EC_Initial_Assessment_Time_Since_Arrival = mapped_column(t.BIGINT)
    EC_Injury_Activity_Status_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    EC_Injury_Activity_Type_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    EC_Injury_Date = mapped_column(t.Date)
    EC_Injury_Intent_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    EC_Injury_Mechanism_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    EC_Injury_Time = mapped_column(t.VARCHAR(8, collation="Latin1_General_CI_AS"))
    EC_PCD_Indicator = mapped_column(t.Integer)
    EC_Place_Of_Injury_Latitude = mapped_column(
        t.VARCHAR(10, collation="Latin1_General_CI_AS")
    )
    EC_Place_Of_Injury_Longitude = mapped_column(
        t.VARCHAR(10, collation="Latin1_General_CI_AS")
    )
    EC_Place_Of_Injury_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    EC_Seen_For_Treatment_Date = mapped_column(t.Date)
    EC_Seen_For_Treatment_Time = mapped_column(
        t.VARCHAR(8, collation="Latin1_General_CI_AS")
    )
    EC_Seen_For_Treatment_Time_Since_Arrival = mapped_column(t.BIGINT)
    Ethnic_Category = mapped_column(t.VARCHAR(1, collation="Latin1_General_CI_AS"))
    Exclusions = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Finished_Indicator = mapped_column(t.BIGINT)
    Fractional_Age_At_Arrival = mapped_column(t.Float)
    HES_Age_At_Arrival = mapped_column(t.BIGINT)
    HES_Age_At_Departure = mapped_column(t.BIGINT)
    Index_Of_Multiple_Deprivation_Decile = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS")
    )
    Index_Of_Multiple_Deprivation_Decile_Description = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS")
    )
    Interpreter_Language_Code_Approved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Interpreter_Language_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    Month_of_Birth = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    NHS_Number_Is_Valid = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    NHS_Number_Status_Indicator_Code = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Overseas_Visitor_Charging_Category = mapped_column(
        t.VARCHAR(1, collation="Latin1_General_CI_AS")
    )
    Patient_Type = mapped_column(t.VARCHAR(4, collation="Latin1_General_CI_AS"))
    Preferred_Spoken_Language_Code_Approved = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Preferred_Spoken_Language_SNOMED_CT = mapped_column(
        t.VARCHAR(18, collation="Latin1_General_CI_AS")
    )
    Provider_Code = mapped_column(t.VARCHAR(12, collation="Latin1_General_CI_AS"))
    RTT_Period_End_Date = mapped_column(t.Date)
    RTT_Period_Length = mapped_column(t.BIGINT)
    RTT_Period_Start_Date = mapped_column(t.Date)
    RTT_Period_Status = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Reason_For_Access = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Rural_Urban_Indicator = mapped_column(
        t.VARCHAR(1, collation="Latin1_General_CI_AS")
    )
    SNOMED_Version = mapped_column(t.VARCHAR(6, collation="Latin1_General_CI_AS"))
    SUS_Code_Cleaning_Applied = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    SUS_Costing_Period = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    SUS_Excluded = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    SUS_Final_Price = mapped_column(t.Numeric)
    SUS_Grouper_Version = mapped_column(t.VARCHAR(8, collation="Latin1_General_CI_AS"))
    SUS_HRG_Code = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    SUS_MFAdjustment = mapped_column(t.Numeric)
    SUS_MFF = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    SUS_Tariff = mapped_column(t.Numeric)
    SUS_Tariff_Description = mapped_column(
        t.VARCHAR(10, collation="Latin1_General_CI_AS")
    )
    Sex = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Site_Code_of_Treatment = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Wait_Time_Measurement_Type = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Withheld_Identity_Reason = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Year_of_Birth = mapped_column(t.VARCHAR(4, collation="Latin1_General_CI_AS"))


class ECDS_EC_Diagnoses(Base):
    __tablename__ = "ECDS_EC_Diagnoses"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    DiagnosisCode = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT)
    Ordinal = mapped_column(t.Integer, nullable=False, default=0)


class EC_ARCHIVED(Base):
    __tablename__ = "EC_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Arrival_Date = mapped_column(t.Date)
    Arrival_Time = mapped_column(t.Time)
    DQ_Chief_Complaint_Completed = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Chief_Complaint_Expected = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Chief_Complaint_Valid = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Completed = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Expected = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Valid = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Decision_To_Admit_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(6, collation="Latin1_General_CI_AS"))
    Der_EC_Diagnosis_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_EC_Investigation_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_EC_Treatment_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_Financial_Year = mapped_column(t.VARCHAR(7, collation="Latin1_General_CI_AS"))
    Discharge_Destination_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Arrival_Mode_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_AttendanceCategory = mapped_column(
        t.VARCHAR(1, collation="Latin1_General_CI_AS")
    )
    EC_Attendance_Source_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Chief_Complaint_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Decision_To_Admit_Date = mapped_column(t.Date)
    EC_Department_Type = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Injury_Date = mapped_column(t.Date)
    Ethnic_Category = mapped_column(t.VARCHAR(1, collation="Latin1_General_CI_AS"))
    SUS_Final_Price = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    SUS_HRG_Code = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    SUS_Tariff = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))


class EC_ARCHIVED_Old(Base):
    __tablename__ = "EC_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Arrival_Date = mapped_column(t.Date)
    Arrival_Time = mapped_column(t.Time)
    DQ_Chief_Complaint_Completed = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Chief_Complaint_Expected = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Chief_Complaint_Valid = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Completed = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Expected = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Valid = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Decision_To_Admit_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(6, collation="Latin1_General_CI_AS"))
    Der_EC_Diagnosis_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_EC_Investigation_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_EC_Treatment_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_Financial_Year = mapped_column(t.VARCHAR(7, collation="Latin1_General_CI_AS"))
    Discharge_Destination_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Arrival_Mode_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_AttendanceCategory = mapped_column(
        t.VARCHAR(1, collation="Latin1_General_CI_AS")
    )
    EC_Attendance_Source_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Chief_Complaint_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Decision_To_Admit_Date = mapped_column(t.Date)
    EC_Department_Type = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Injury_Date = mapped_column(t.Date)
    Ethnic_Category = mapped_column(t.VARCHAR(1, collation="Latin1_General_CI_AS"))
    SUS_Final_Price = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    SUS_HRG_Code = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    SUS_Tariff = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))


class EC_AlcoholDrugInvolvement(Base):
    __tablename__ = "EC_AlcoholDrugInvolvement"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Alcohol_Drug_Involvement_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_10 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_11 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_12 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Is_Code_Approved_01 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_02 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_03 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_04 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_05 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_06 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_07 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_08 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_09 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_10 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_11 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_12 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))


class EC_AlcoholDrugInvolvement_ARCHIVED(Base):
    __tablename__ = "EC_AlcoholDrugInvolvement_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Alcohol_Drug_Involvement_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_10 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_11 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_12 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Is_Code_Approved_01 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_02 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_03 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_04 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_05 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_06 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_07 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_08 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_09 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_10 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_11 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_12 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))


class EC_AlcoholDrugInvolvement_ARCHIVED_Old(Base):
    __tablename__ = "EC_AlcoholDrugInvolvement_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Alcohol_Drug_Involvement_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_10 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_11 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_12 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Is_Code_Approved_01 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_02 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_03 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_04 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_05 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_06 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_07 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_08 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_09 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_10 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_11 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_12 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))


class EC_AlcoholDrugInvolvement_JRC20231023_LastFilesToContainAllHistoricalCostData(
    Base
):
    __tablename__ = (
        "EC_AlcoholDrugInvolvement_JRC20231023_LastFilesToContainAllHistoricalCostData"
    )
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Alcohol_Drug_Involvement_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_10 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_11 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_12 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Is_Code_Approved_01 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_02 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_03 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_04 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_05 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_06 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_07 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_08 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_09 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_10 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_11 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_12 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))


class EC_AlcoholDrugInvolvement_JRC20251111_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = (
        "EC_AlcoholDrugInvolvement_JRC20251111_BeforeOldFinancialYearDataRemoved"
    )
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Alcohol_Drug_Involvement_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_10 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_11 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Alcohol_Drug_Involvement_12 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Is_Code_Approved_01 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_02 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_03 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_04 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_05 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_06 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_07 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_08 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_09 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_10 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_11 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    Is_Code_Approved_12 = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))


class EC_Comorbidities(Base):
    __tablename__ = "EC_Comorbidities"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Comorbidity_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)


class EC_Comorbidities_ARCHIVED(Base):
    __tablename__ = "EC_Comorbidities_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Comorbidity_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)


class EC_Comorbidities_ARCHIVED_Old(Base):
    __tablename__ = "EC_Comorbidities_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Comorbidity_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)


class EC_Comorbidities_JRC20231023_LastFilesToContainAllHistoricalCostData(Base):
    __tablename__ = (
        "EC_Comorbidities_JRC20231023_LastFilesToContainAllHistoricalCostData"
    )
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Comorbidity_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)


class EC_Comorbidities_JRC20251111_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = "EC_Comorbidities_JRC20251111_BeforeOldFinancialYearDataRemoved"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Comorbidity_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    Comorbidity_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)


class EC_Cost(Base):
    __tablename__ = "EC_Cost"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class EC_Cost_ARCHIVED(Base):
    __tablename__ = "EC_Cost_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class EC_Cost_ARCHIVED_Old(Base):
    __tablename__ = "EC_Cost_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class EC_Cost_JRC20231023_LastFilesToContainAllHistoricalCostData(Base):
    __tablename__ = "EC_Cost_JRC20231023_LastFilesToContainAllHistoricalCostData"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class EC_Cost_JRC20251111_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = "EC_Cost_JRC20251111_BeforeOldFinancialYearDataRemoved"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class EC_Diagnosis(Base):
    __tablename__ = "EC_Diagnosis"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Diagnosis_01 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_02 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_03 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_04 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_05 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_06 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_07 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_08 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_09 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_10 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_11 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_12 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_13 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_14 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_15 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_16 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_17 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_18 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_19 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_20 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_21 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_22 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_23 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_24 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    EC_Chief_Complaint_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Diagnosis_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)


class EC_Diagnosis_ARCHIVED(Base):
    __tablename__ = "EC_Diagnosis_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Diagnosis_01 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_02 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_03 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_04 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_05 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_06 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_07 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_08 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_09 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_10 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_11 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_12 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_13 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_14 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_15 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_16 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_17 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_18 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_19 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_20 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_21 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_22 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_23 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_24 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    EC_Chief_Complaint_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Diagnosis_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)


class EC_Diagnosis_ARCHIVED_Old(Base):
    __tablename__ = "EC_Diagnosis_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Diagnosis_01 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_02 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_03 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_04 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_05 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_06 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_07 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_08 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_09 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_10 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_11 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_12 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_13 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_14 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_15 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_16 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_17 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_18 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_19 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_20 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_21 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_22 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_23 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_24 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    EC_Chief_Complaint_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Diagnosis_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)


class EC_Diagnosis_JRC20231023_LastFilesToContainAllHistoricalCostData(Base):
    __tablename__ = "EC_Diagnosis_JRC20231023_LastFilesToContainAllHistoricalCostData"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Diagnosis_01 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_02 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_03 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_04 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_05 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_06 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_07 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_08 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_09 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_10 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_11 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_12 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_13 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_14 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_15 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_16 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_17 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_18 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_19 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_20 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_21 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_22 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_23 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_24 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    EC_Chief_Complaint_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Diagnosis_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)


class EC_Diagnosis_JRC20251111_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = "EC_Diagnosis_JRC20251111_BeforeOldFinancialYearDataRemoved"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Diagnosis_01 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_02 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_03 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_04 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_05 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_06 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_07 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_08 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_09 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_10 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_11 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_12 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_13 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_14 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_15 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_16 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_17 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_18 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_19 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_20 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_21 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_22 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_23 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    AEA_Diagnosis_24 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    EC_Chief_Complaint_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Diagnosis_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Diagnosis_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)


class EC_Investigation(Base):
    __tablename__ = "EC_Investigation"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Investigation_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_10 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_11 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_12 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_13 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_14 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_15 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_16 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_17 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_18 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_19 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_20 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_21 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_22 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_23 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_24 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Investigation_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))


class EC_Investigation_ARCHIVED(Base):
    __tablename__ = "EC_Investigation_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Investigation_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_10 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_11 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_12 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_13 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_14 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_15 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_16 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_17 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_18 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_19 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_20 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_21 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_22 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_23 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_24 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Investigation_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))


class EC_Investigation_ARCHIVED_Old(Base):
    __tablename__ = "EC_Investigation_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Investigation_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_10 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_11 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_12 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_13 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_14 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_15 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_16 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_17 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_18 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_19 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_20 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_21 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_22 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_23 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_24 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Investigation_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))


class EC_Investigation_JRC20231023_LastFilesToContainAllHistoricalCostData(Base):
    __tablename__ = (
        "EC_Investigation_JRC20231023_LastFilesToContainAllHistoricalCostData"
    )
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Investigation_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_10 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_11 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_12 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_13 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_14 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_15 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_16 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_17 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_18 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_19 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_20 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_21 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_22 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_23 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_24 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Investigation_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))


class EC_Investigation_JRC20251111_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = "EC_Investigation_JRC20251111_BeforeOldFinancialYearDataRemoved"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Investigation_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_10 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_11 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_12 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_13 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_14 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_15 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_16 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_17 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_18 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_19 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_20 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_21 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_22 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_23 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    AEA_Investigation_24 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Investigation_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Investigation_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))


class EC_JRC20231023_LastFilesToContainAllHistoricalCostData(Base):
    __tablename__ = "EC_JRC20231023_LastFilesToContainAllHistoricalCostData"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Arrival_Date = mapped_column(t.Date)
    Arrival_Time = mapped_column(t.Time)
    DQ_Chief_Complaint_Completed = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Chief_Complaint_Expected = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Chief_Complaint_Valid = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Completed = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Expected = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Valid = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Decision_To_Admit_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(6, collation="Latin1_General_CI_AS"))
    Der_EC_Diagnosis_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_EC_Investigation_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_EC_Treatment_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_Financial_Year = mapped_column(t.VARCHAR(7, collation="Latin1_General_CI_AS"))
    Discharge_Destination_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Arrival_Mode_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_AttendanceCategory = mapped_column(
        t.VARCHAR(1, collation="Latin1_General_CI_AS")
    )
    EC_Attendance_Source_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Chief_Complaint_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Decision_To_Admit_Date = mapped_column(t.Date)
    EC_Department_Type = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Injury_Date = mapped_column(t.Date)
    Ethnic_Category = mapped_column(t.VARCHAR(1, collation="Latin1_General_CI_AS"))
    SUS_Final_Price = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    SUS_HRG_Code = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    SUS_Tariff = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))


class EC_JRC20251111_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = "EC_JRC20251111_BeforeOldFinancialYearDataRemoved"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Arrival_Date = mapped_column(t.Date)
    Arrival_Time = mapped_column(t.Time)
    DQ_Chief_Complaint_Completed = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Chief_Complaint_Expected = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Chief_Complaint_Valid = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Completed = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Expected = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    DQ_Primary_Diagnosis_Valid = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Decision_To_Admit_Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(6, collation="Latin1_General_CI_AS"))
    Der_EC_Diagnosis_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_EC_Investigation_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_EC_Treatment_All = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    Der_Financial_Year = mapped_column(t.VARCHAR(7, collation="Latin1_General_CI_AS"))
    Discharge_Destination_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Arrival_Mode_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_AttendanceCategory = mapped_column(
        t.VARCHAR(1, collation="Latin1_General_CI_AS")
    )
    EC_Attendance_Source_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Chief_Complaint_SNOMED_CT = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    EC_Decision_To_Admit_Date = mapped_column(t.Date)
    EC_Department_Type = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Injury_Date = mapped_column(t.Date)
    Ethnic_Category = mapped_column(t.VARCHAR(1, collation="Latin1_General_CI_AS"))
    SUS_Final_Price = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    SUS_HRG_Code = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))
    SUS_Tariff = mapped_column(t.VARCHAR(5, collation="Latin1_General_CI_AS"))


class EC_PatientMentalHealth(Base):
    __tablename__ = "EC_PatientMentalHealth"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    MH_Classification_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_010 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_011 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_012 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_013 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_014 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_015 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_016 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_017 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_018 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_019 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_20 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_21 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_22 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_23 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_24 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Expiry_Date_01 = mapped_column(t.Date)
    MH_Expiry_Date_010 = mapped_column(t.Date)
    MH_Expiry_Date_011 = mapped_column(t.Date)
    MH_Expiry_Date_012 = mapped_column(t.Date)
    MH_Expiry_Date_013 = mapped_column(t.Date)
    MH_Expiry_Date_014 = mapped_column(t.Date)
    MH_Expiry_Date_015 = mapped_column(t.Date)
    MH_Expiry_Date_016 = mapped_column(t.Date)
    MH_Expiry_Date_017 = mapped_column(t.Date)
    MH_Expiry_Date_018 = mapped_column(t.Date)
    MH_Expiry_Date_019 = mapped_column(t.Date)
    MH_Expiry_Date_02 = mapped_column(t.Date)
    MH_Expiry_Date_03 = mapped_column(t.Date)
    MH_Expiry_Date_04 = mapped_column(t.Date)
    MH_Expiry_Date_05 = mapped_column(t.Date)
    MH_Expiry_Date_06 = mapped_column(t.Date)
    MH_Expiry_Date_07 = mapped_column(t.Date)
    MH_Expiry_Date_08 = mapped_column(t.Date)
    MH_Expiry_Date_09 = mapped_column(t.Date)
    MH_Expiry_Date_20 = mapped_column(t.Date)
    MH_Expiry_Date_21 = mapped_column(t.Date)
    MH_Expiry_Date_22 = mapped_column(t.Date)
    MH_Expiry_Date_23 = mapped_column(t.Date)
    MH_Expiry_Date_24 = mapped_column(t.Date)
    MH_Start_Date_01 = mapped_column(t.Date)
    MH_Start_Date_010 = mapped_column(t.Date)
    MH_Start_Date_011 = mapped_column(t.Date)
    MH_Start_Date_012 = mapped_column(t.Date)
    MH_Start_Date_013 = mapped_column(t.Date)
    MH_Start_Date_014 = mapped_column(t.Date)
    MH_Start_Date_015 = mapped_column(t.Date)
    MH_Start_Date_016 = mapped_column(t.Date)
    MH_Start_Date_017 = mapped_column(t.Date)
    MH_Start_Date_018 = mapped_column(t.Date)
    MH_Start_Date_019 = mapped_column(t.Date)
    MH_Start_Date_02 = mapped_column(t.Date)
    MH_Start_Date_03 = mapped_column(t.Date)
    MH_Start_Date_04 = mapped_column(t.Date)
    MH_Start_Date_05 = mapped_column(t.Date)
    MH_Start_Date_06 = mapped_column(t.Date)
    MH_Start_Date_07 = mapped_column(t.Date)
    MH_Start_Date_08 = mapped_column(t.Date)
    MH_Start_Date_09 = mapped_column(t.Date)
    MH_Start_Date_20 = mapped_column(t.Date)
    MH_Start_Date_21 = mapped_column(t.Date)
    MH_Start_Date_22 = mapped_column(t.Date)
    MH_Start_Date_23 = mapped_column(t.Date)
    MH_Start_Date_24 = mapped_column(t.Date)


class EC_PatientMentalHealth_ARCHIVED(Base):
    __tablename__ = "EC_PatientMentalHealth_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    MH_Classification_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_010 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_011 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_012 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_013 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_014 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_015 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_016 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_017 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_018 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_019 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_20 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_21 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_22 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_23 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_24 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Expiry_Date_01 = mapped_column(t.Date)
    MH_Expiry_Date_010 = mapped_column(t.Date)
    MH_Expiry_Date_011 = mapped_column(t.Date)
    MH_Expiry_Date_012 = mapped_column(t.Date)
    MH_Expiry_Date_013 = mapped_column(t.Date)
    MH_Expiry_Date_014 = mapped_column(t.Date)
    MH_Expiry_Date_015 = mapped_column(t.Date)
    MH_Expiry_Date_016 = mapped_column(t.Date)
    MH_Expiry_Date_017 = mapped_column(t.Date)
    MH_Expiry_Date_018 = mapped_column(t.Date)
    MH_Expiry_Date_019 = mapped_column(t.Date)
    MH_Expiry_Date_02 = mapped_column(t.Date)
    MH_Expiry_Date_03 = mapped_column(t.Date)
    MH_Expiry_Date_04 = mapped_column(t.Date)
    MH_Expiry_Date_05 = mapped_column(t.Date)
    MH_Expiry_Date_06 = mapped_column(t.Date)
    MH_Expiry_Date_07 = mapped_column(t.Date)
    MH_Expiry_Date_08 = mapped_column(t.Date)
    MH_Expiry_Date_09 = mapped_column(t.Date)
    MH_Expiry_Date_20 = mapped_column(t.Date)
    MH_Expiry_Date_21 = mapped_column(t.Date)
    MH_Expiry_Date_22 = mapped_column(t.Date)
    MH_Expiry_Date_23 = mapped_column(t.Date)
    MH_Expiry_Date_24 = mapped_column(t.Date)
    MH_Start_Date_01 = mapped_column(t.Date)
    MH_Start_Date_010 = mapped_column(t.Date)
    MH_Start_Date_011 = mapped_column(t.Date)
    MH_Start_Date_012 = mapped_column(t.Date)
    MH_Start_Date_013 = mapped_column(t.Date)
    MH_Start_Date_014 = mapped_column(t.Date)
    MH_Start_Date_015 = mapped_column(t.Date)
    MH_Start_Date_016 = mapped_column(t.Date)
    MH_Start_Date_017 = mapped_column(t.Date)
    MH_Start_Date_018 = mapped_column(t.Date)
    MH_Start_Date_019 = mapped_column(t.Date)
    MH_Start_Date_02 = mapped_column(t.Date)
    MH_Start_Date_03 = mapped_column(t.Date)
    MH_Start_Date_04 = mapped_column(t.Date)
    MH_Start_Date_05 = mapped_column(t.Date)
    MH_Start_Date_06 = mapped_column(t.Date)
    MH_Start_Date_07 = mapped_column(t.Date)
    MH_Start_Date_08 = mapped_column(t.Date)
    MH_Start_Date_09 = mapped_column(t.Date)
    MH_Start_Date_20 = mapped_column(t.Date)
    MH_Start_Date_21 = mapped_column(t.Date)
    MH_Start_Date_22 = mapped_column(t.Date)
    MH_Start_Date_23 = mapped_column(t.Date)
    MH_Start_Date_24 = mapped_column(t.Date)


class EC_PatientMentalHealth_ARCHIVED_Old(Base):
    __tablename__ = "EC_PatientMentalHealth_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    MH_Classification_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_010 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_011 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_012 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_013 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_014 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_015 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_016 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_017 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_018 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_019 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_20 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_21 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_22 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_23 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_24 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Expiry_Date_01 = mapped_column(t.Date)
    MH_Expiry_Date_010 = mapped_column(t.Date)
    MH_Expiry_Date_011 = mapped_column(t.Date)
    MH_Expiry_Date_012 = mapped_column(t.Date)
    MH_Expiry_Date_013 = mapped_column(t.Date)
    MH_Expiry_Date_014 = mapped_column(t.Date)
    MH_Expiry_Date_015 = mapped_column(t.Date)
    MH_Expiry_Date_016 = mapped_column(t.Date)
    MH_Expiry_Date_017 = mapped_column(t.Date)
    MH_Expiry_Date_018 = mapped_column(t.Date)
    MH_Expiry_Date_019 = mapped_column(t.Date)
    MH_Expiry_Date_02 = mapped_column(t.Date)
    MH_Expiry_Date_03 = mapped_column(t.Date)
    MH_Expiry_Date_04 = mapped_column(t.Date)
    MH_Expiry_Date_05 = mapped_column(t.Date)
    MH_Expiry_Date_06 = mapped_column(t.Date)
    MH_Expiry_Date_07 = mapped_column(t.Date)
    MH_Expiry_Date_08 = mapped_column(t.Date)
    MH_Expiry_Date_09 = mapped_column(t.Date)
    MH_Expiry_Date_20 = mapped_column(t.Date)
    MH_Expiry_Date_21 = mapped_column(t.Date)
    MH_Expiry_Date_22 = mapped_column(t.Date)
    MH_Expiry_Date_23 = mapped_column(t.Date)
    MH_Expiry_Date_24 = mapped_column(t.Date)
    MH_Start_Date_01 = mapped_column(t.Date)
    MH_Start_Date_010 = mapped_column(t.Date)
    MH_Start_Date_011 = mapped_column(t.Date)
    MH_Start_Date_012 = mapped_column(t.Date)
    MH_Start_Date_013 = mapped_column(t.Date)
    MH_Start_Date_014 = mapped_column(t.Date)
    MH_Start_Date_015 = mapped_column(t.Date)
    MH_Start_Date_016 = mapped_column(t.Date)
    MH_Start_Date_017 = mapped_column(t.Date)
    MH_Start_Date_018 = mapped_column(t.Date)
    MH_Start_Date_019 = mapped_column(t.Date)
    MH_Start_Date_02 = mapped_column(t.Date)
    MH_Start_Date_03 = mapped_column(t.Date)
    MH_Start_Date_04 = mapped_column(t.Date)
    MH_Start_Date_05 = mapped_column(t.Date)
    MH_Start_Date_06 = mapped_column(t.Date)
    MH_Start_Date_07 = mapped_column(t.Date)
    MH_Start_Date_08 = mapped_column(t.Date)
    MH_Start_Date_09 = mapped_column(t.Date)
    MH_Start_Date_20 = mapped_column(t.Date)
    MH_Start_Date_21 = mapped_column(t.Date)
    MH_Start_Date_22 = mapped_column(t.Date)
    MH_Start_Date_23 = mapped_column(t.Date)
    MH_Start_Date_24 = mapped_column(t.Date)


class EC_PatientMentalHealth_JRC20231023_LastFilesToContainAllHistoricalCostData(Base):
    __tablename__ = (
        "EC_PatientMentalHealth_JRC20231023_LastFilesToContainAllHistoricalCostData"
    )
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    MH_Classification_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_010 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_011 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_012 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_013 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_014 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_015 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_016 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_017 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_018 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_019 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_20 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_21 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_22 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_23 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_24 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Expiry_Date_01 = mapped_column(t.Date)
    MH_Expiry_Date_010 = mapped_column(t.Date)
    MH_Expiry_Date_011 = mapped_column(t.Date)
    MH_Expiry_Date_012 = mapped_column(t.Date)
    MH_Expiry_Date_013 = mapped_column(t.Date)
    MH_Expiry_Date_014 = mapped_column(t.Date)
    MH_Expiry_Date_015 = mapped_column(t.Date)
    MH_Expiry_Date_016 = mapped_column(t.Date)
    MH_Expiry_Date_017 = mapped_column(t.Date)
    MH_Expiry_Date_018 = mapped_column(t.Date)
    MH_Expiry_Date_019 = mapped_column(t.Date)
    MH_Expiry_Date_02 = mapped_column(t.Date)
    MH_Expiry_Date_03 = mapped_column(t.Date)
    MH_Expiry_Date_04 = mapped_column(t.Date)
    MH_Expiry_Date_05 = mapped_column(t.Date)
    MH_Expiry_Date_06 = mapped_column(t.Date)
    MH_Expiry_Date_07 = mapped_column(t.Date)
    MH_Expiry_Date_08 = mapped_column(t.Date)
    MH_Expiry_Date_09 = mapped_column(t.Date)
    MH_Expiry_Date_20 = mapped_column(t.Date)
    MH_Expiry_Date_21 = mapped_column(t.Date)
    MH_Expiry_Date_22 = mapped_column(t.Date)
    MH_Expiry_Date_23 = mapped_column(t.Date)
    MH_Expiry_Date_24 = mapped_column(t.Date)
    MH_Start_Date_01 = mapped_column(t.Date)
    MH_Start_Date_010 = mapped_column(t.Date)
    MH_Start_Date_011 = mapped_column(t.Date)
    MH_Start_Date_012 = mapped_column(t.Date)
    MH_Start_Date_013 = mapped_column(t.Date)
    MH_Start_Date_014 = mapped_column(t.Date)
    MH_Start_Date_015 = mapped_column(t.Date)
    MH_Start_Date_016 = mapped_column(t.Date)
    MH_Start_Date_017 = mapped_column(t.Date)
    MH_Start_Date_018 = mapped_column(t.Date)
    MH_Start_Date_019 = mapped_column(t.Date)
    MH_Start_Date_02 = mapped_column(t.Date)
    MH_Start_Date_03 = mapped_column(t.Date)
    MH_Start_Date_04 = mapped_column(t.Date)
    MH_Start_Date_05 = mapped_column(t.Date)
    MH_Start_Date_06 = mapped_column(t.Date)
    MH_Start_Date_07 = mapped_column(t.Date)
    MH_Start_Date_08 = mapped_column(t.Date)
    MH_Start_Date_09 = mapped_column(t.Date)
    MH_Start_Date_20 = mapped_column(t.Date)
    MH_Start_Date_21 = mapped_column(t.Date)
    MH_Start_Date_22 = mapped_column(t.Date)
    MH_Start_Date_23 = mapped_column(t.Date)
    MH_Start_Date_24 = mapped_column(t.Date)


class EC_PatientMentalHealth_JRC20251111_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = (
        "EC_PatientMentalHealth_JRC20251111_BeforeOldFinancialYearDataRemoved"
    )
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    MH_Classification_01 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_010 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_011 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_012 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_013 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_014 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_015 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_016 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_017 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_018 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_019 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_02 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_03 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_04 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_05 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_06 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_07 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_08 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_09 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_20 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_21 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_22 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_23 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Classification_24 = mapped_column(
        t.VARCHAR(20, collation="Latin1_General_CI_AS")
    )
    MH_Expiry_Date_01 = mapped_column(t.Date)
    MH_Expiry_Date_010 = mapped_column(t.Date)
    MH_Expiry_Date_011 = mapped_column(t.Date)
    MH_Expiry_Date_012 = mapped_column(t.Date)
    MH_Expiry_Date_013 = mapped_column(t.Date)
    MH_Expiry_Date_014 = mapped_column(t.Date)
    MH_Expiry_Date_015 = mapped_column(t.Date)
    MH_Expiry_Date_016 = mapped_column(t.Date)
    MH_Expiry_Date_017 = mapped_column(t.Date)
    MH_Expiry_Date_018 = mapped_column(t.Date)
    MH_Expiry_Date_019 = mapped_column(t.Date)
    MH_Expiry_Date_02 = mapped_column(t.Date)
    MH_Expiry_Date_03 = mapped_column(t.Date)
    MH_Expiry_Date_04 = mapped_column(t.Date)
    MH_Expiry_Date_05 = mapped_column(t.Date)
    MH_Expiry_Date_06 = mapped_column(t.Date)
    MH_Expiry_Date_07 = mapped_column(t.Date)
    MH_Expiry_Date_08 = mapped_column(t.Date)
    MH_Expiry_Date_09 = mapped_column(t.Date)
    MH_Expiry_Date_20 = mapped_column(t.Date)
    MH_Expiry_Date_21 = mapped_column(t.Date)
    MH_Expiry_Date_22 = mapped_column(t.Date)
    MH_Expiry_Date_23 = mapped_column(t.Date)
    MH_Expiry_Date_24 = mapped_column(t.Date)
    MH_Start_Date_01 = mapped_column(t.Date)
    MH_Start_Date_010 = mapped_column(t.Date)
    MH_Start_Date_011 = mapped_column(t.Date)
    MH_Start_Date_012 = mapped_column(t.Date)
    MH_Start_Date_013 = mapped_column(t.Date)
    MH_Start_Date_014 = mapped_column(t.Date)
    MH_Start_Date_015 = mapped_column(t.Date)
    MH_Start_Date_016 = mapped_column(t.Date)
    MH_Start_Date_017 = mapped_column(t.Date)
    MH_Start_Date_018 = mapped_column(t.Date)
    MH_Start_Date_019 = mapped_column(t.Date)
    MH_Start_Date_02 = mapped_column(t.Date)
    MH_Start_Date_03 = mapped_column(t.Date)
    MH_Start_Date_04 = mapped_column(t.Date)
    MH_Start_Date_05 = mapped_column(t.Date)
    MH_Start_Date_06 = mapped_column(t.Date)
    MH_Start_Date_07 = mapped_column(t.Date)
    MH_Start_Date_08 = mapped_column(t.Date)
    MH_Start_Date_09 = mapped_column(t.Date)
    MH_Start_Date_20 = mapped_column(t.Date)
    MH_Start_Date_21 = mapped_column(t.Date)
    MH_Start_Date_22 = mapped_column(t.Date)
    MH_Start_Date_23 = mapped_column(t.Date)
    MH_Start_Date_24 = mapped_column(t.Date)


class EC_Treatment(Base):
    __tablename__ = "EC_Treatment"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Treatment_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Treatment_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))


class EC_Treatment_ARCHIVED(Base):
    __tablename__ = "EC_Treatment_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Treatment_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Treatment_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))


class EC_Treatment_ARCHIVED_Old(Base):
    __tablename__ = "EC_Treatment_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Treatment_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Treatment_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))


class EC_Treatment_JRC20231023_LastFilesToContainAllHistoricalCostData(Base):
    __tablename__ = "EC_Treatment_JRC20231023_LastFilesToContainAllHistoricalCostData"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Treatment_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Treatment_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))


class EC_Treatment_JRC20251111_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = "EC_Treatment_JRC20251111_BeforeOldFinancialYearDataRemoved"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AEA_Treatment_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    AEA_Treatment_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    EC_Treatment_01 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_02 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_03 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_04 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_05 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_06 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_07 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_08 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_09 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_10 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_11 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_12 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_13 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_14 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_15 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_16 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_17 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_18 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_19 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_20 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_21 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_22 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_23 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))
    EC_Treatment_24 = mapped_column(t.VARCHAR(20, collation="Latin1_General_CI_AS"))


class HealthCareWorker(Base):
    __tablename__ = "HealthCareWorker"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    HealthCareWorker = mapped_column(
        t.VARCHAR(10, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class HighCostDrugs(Base):
    __tablename__ = "HighCostDrugs"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ActivityTreatmentFunctionCode = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    DerivedSNOMEDFromName = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    DerivedVTM = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    DerivedVTMName = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    DispensingRoute = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    DrugName = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    DrugPackSize = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    DrugQuanitityOrWeightProportion = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    DrugStrength = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    DrugVolume = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    FinancialMonth = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    FinancialYear = mapped_column(t.VARCHAR(6, collation="Latin1_General_CI_AS"))
    HighCostTariffExcludedDrugCode = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    HomeDeliveryCharge = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    PersonAge = mapped_column(t.Integer)
    PersonGender = mapped_column(t.Integer)
    RouteOfAdministration = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    TherapeuticIndicationCode = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    TotalCost = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    UnitOfMeasurement = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))


class Household(Base):
    __tablename__ = "Household"
    _pk = mapped_column(t.Integer, primary_key=True)

    CareHome = mapped_column(t.Boolean)
    HouseholdSize = mapped_column(t.Integer)
    Household_ID = mapped_column(t.BIGINT)
    MSOA = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    MatchesUprnCount = mapped_column(t.Boolean)
    MixedSoftwareHousehold = mapped_column(t.Boolean)
    NFA_Unknown = mapped_column(t.Boolean)
    Prison = mapped_column(t.Boolean)
    TppPercentage = mapped_column(t.Integer)


class HouseholdMember(Base):
    __tablename__ = "HouseholdMember"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    HouseholdMember_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Household_ID = mapped_column(t.BIGINT, nullable=False, default=0)


class ICD10Dictionary(Base):
    __tablename__ = "ICD10Dictionary"
    _pk = mapped_column(t.Integer, primary_key=True)

    Code = mapped_column(
        t.VARCHAR(4, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    CodeDescription = mapped_column(
        t.VARCHAR(500, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    ParentCode = mapped_column(
        t.CHAR(3, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    ParentCodeDescription = mapped_column(
        t.VARCHAR(500, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class ICD10Dictionary_BUILDING(Base):
    __tablename__ = "ICD10Dictionary_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    Code = mapped_column(
        t.VARCHAR(4, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    CodeDescription = mapped_column(
        t.VARCHAR(500, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    ParentCode = mapped_column(
        t.CHAR(3, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    ParentCodeDescription = mapped_column(
        t.VARCHAR(500, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class ICNARC(Base):
    __tablename__ = "ICNARC"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AP2score = mapped_column(t.Integer)
    AdvancedDays_CardiovascularSupport = mapped_column(t.Integer)
    AdvancedDays_RespiratorySupport = mapped_column(t.Integer)
    BasicDays_CardiovascularSupport = mapped_column(t.Integer)
    BasicDays_RespiratorySupport = mapped_column(t.Integer)
    CalculatedAge = mapped_column(t.Integer)
    DateOfDeath = mapped_column(t.DateTime)
    EstimatedAge = mapped_column(t.Integer)
    HRG = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    HighestLevelFirst24Hours = mapped_column(t.Integer)
    HospitalAdmissionDate = mapped_column(t.DateTime)
    HospitalDischargeDate = mapped_column(t.DateTime)
    ICNARC_ID = mapped_column(t.BIGINT)
    IMscore = mapped_column(t.Integer)
    IcuAdmissionDateTime = mapped_column(t.DateTime)
    IcuDischargeDateTime = mapped_column(t.DateTime)
    Level0days = mapped_column(t.Integer)
    Level1days = mapped_column(t.Integer)
    Level2days = mapped_column(t.Integer)
    Level3days = mapped_column(t.Integer)
    OriginalHospitalAdmissionDate = mapped_column(t.DateTime)
    OriginalIcuAdmissionDate = mapped_column(t.DateTime)
    Sex = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    SupportDays_Dermatological = mapped_column(t.Integer)
    SupportDays_Gastrointestinal = mapped_column(t.Integer)
    SupportDays_Liver = mapped_column(t.Integer)
    SupportDays_Neurological = mapped_column(t.Integer)
    SupportDays_Renal = mapped_column(t.Integer)
    TransferredIn = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    TransferredOut = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    UltimateHospitalDischargeDate = mapped_column(t.DateTime)
    UltimateIcuDischargeDate = mapped_column(t.DateTime)
    Ventilator = mapped_column(t.Integer)
    ahsurv = mapped_column(t.Integer)
    ausurv = mapped_column(t.Integer)
    pfratio = mapped_column(t.REAL)
    yhsurv = mapped_column(t.Integer)
    yusurv = mapped_column(t.Integer)


class ISARIC_New(Base):
    __tablename__ = "ISARIC_New"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    abdopain_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    abdopain_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    adeno_mbcat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    adeno_mbcat_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    adm_no_symp = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    admission_diabp_vsorres = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    admission_signs_and_symptoms_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    age = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    age_factor = mapped_column(
        "age.factor", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    age_estimateyears = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    age_estimateyearsu = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    agedatyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ageusia_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    ageusia_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    aidshiv_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    aneamia_ceterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    animal_erdat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    animal_erdat_2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    animal_erterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    animal_erterm_2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    animal_eryn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    animal_eryn_2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    anosmia_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    anosmia_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    antibiotic2_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antibiotic2_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antibiotic3_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antibiotic3_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antibiotic4_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antibiotic4_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antibiotic5_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antibiotic5_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antibiotic6_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antibiotic6_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antibiotic7_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antibiotic7_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antibiotic_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antibiotic_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antifung_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antifungal_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    antiviral_cmtrt___1 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    antiviral_cmtrt___10 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    antiviral_cmtrt___11 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    antiviral_cmtrt___12 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    antiviral_cmtrt___2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    antiviral_cmtrt___3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    antiviral_cmtrt___4 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    antiviral_cmtrt___5 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    antiviral_cmtrt___6 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    antiviral_cmtrt___7 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    antiviral_cmtrt___8 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    antiviral_cmtrt___9 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    antiviral_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    any_daily_fio2_21 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    any_daily_fio2_28 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    any_daily_hoterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    any_daily_invasive_prtrt = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    any_daily_nasaloxy_cmtrt = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    any_daily_noninvasive_prtrt = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    any_icu = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    any_icu_hoterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    any_invasive = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    any_invasive_proccur = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    any_noninvasive = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    any_noninvasive_proccur = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    any_oxygen = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    any_oxygen_cmoccur = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    any_oxygenhf_cmoccur = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    any_trach = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    anydat_day1 = mapped_column(
        "anydat.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    anydat_disch = mapped_column(
        "anydat.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    apdm_age = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    aplb_lbmethod = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    aplb_lbmethodoth = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    aplb_lborres = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    aplb_lborres_out = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    aplb_lbperf = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    aplb_lbperf_out = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    apsc_brdisdat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    apsc_brfedind = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    apsc_brfedindy = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    apsc_dvageind = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    apsc_gestout = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    apsc_vcageind = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    apvs_weight = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    apvs_weightnk = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    apvs_weightu = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ards_ceoccur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ari = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    arm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    arm_n = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    arm_participant = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    arrhythmia_ceterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    asthma_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    asymptomatic = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    avpu_vsorres_day1 = mapped_column(
        "avpu_vsorres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    avpu_vsorres_disch = mapped_column(
        "avpu_vsorres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    bact_mborres = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    bacteraemia_ceterm = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    bacteria_mborres = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    bactpneu_ceoccur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    bleed_ceoccur_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    bleed_ceoccur_v3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    bleed_ceterm_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    bleed_cetermy_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    bleed_cetermy_v3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    bloodgroup = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    bronchio_ceterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    calc_age = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    cardiacarrest_ceterm = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    cardiomyopathy_ceterm = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    casiriv_cmtrt_first = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    ccg = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    cestdat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    chestpain_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    chestpain_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    chrincard = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    chronic_ace_cmoccur = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    chronic_arb_cmoccur = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    chronic_nsaid_cmoccur = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    chronichaemo_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    chronicneu_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    chronicpul_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    clinical_frailty = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    clinicalpneu_mborres = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    coagulo_ceterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    comorb_none = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    comorbidities_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    complications_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    complications_none = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    confirmed_negative_pcr = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    confirmed_negative_pcr_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    confusion_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    confusion_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    conjunct_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    conjunct_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    consent_ctu_dms_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    consent_daterec = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    consent_given = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    consent_mode___1 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    consent_mode___10 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    consent_mode___11 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    consent_mode___2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    consent_mode___3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    consent_mode___4 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    consent_mode___5 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    consent_mode___6 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    consent_mode___7 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    consent_mode___8 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    consent_mode___9 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    consent_optcondit___1 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    consent_optcondit___2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    consent_optcondit___3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    consent_optcondit___4 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    consent_phone = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    conv_plasma_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    core_additional_information_complete = mapped_column(
        t.VARCHAR(4000, collation="Latin1_General_CI_AS")
    )
    coriona_ieorres2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    coriona_ieorres3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corna_mbcat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corna_mbcaty = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corona_ieorres = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    coronaother_mborres = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    corticost2_cmdose = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost2_cmroute = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    corticost2_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost2_cmtrt_type = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    corticost2_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost3_cmdose = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost3_cmroute = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    corticost3_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost3_cmtrt_type = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    corticost3_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost4_cmdose = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost4_cmroute = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    corticost4_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost4_cmtrt_type = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    corticost4_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost5_cmdose = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost5_cmroute = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    corticost5_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost5_cmtrt_type = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    corticost5_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost_cmdose = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost_cmroute = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    corticost_cmtrt_type = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    corticost_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    cough = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    cough_ceoccur_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    cough_ceoccur_v3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    coughhb_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    coughhb_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    coughsput_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    coughsput_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    country = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    country_pcds_day1 = mapped_column(
        "country_pcds.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    country_pcds_disch = mapped_column(
        "country_pcds.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    cov19sars_mbyn_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    covid19_new = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    covid19_vaccine = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    covid19_vaccine2d = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    covid19_vaccine2d_nk = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    covid19_vaccine_other_type = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    covid19_vaccine_type = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    covid19_vaccined = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    covid19_vaccined_nk = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    cryptogenic_ceterm = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_alt_lborres_day1 = mapped_column(
        "daily_alt_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_alt_lborres_disch = mapped_column(
        "daily_alt_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_alt_lbyn_day1 = mapped_column(
        "daily_alt_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_alt_lbyn_disch = mapped_column(
        "daily_alt_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_altop_lbyn_day1 = mapped_column(
        "daily_altop_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_altop_lbyn_disch = mapped_column(
        "daily_altop_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_aptt_lborres_day1 = mapped_column(
        "daily_aptt_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_aptt_lborres_disch = mapped_column(
        "daily_aptt_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_aptt_lbyn_day1 = mapped_column(
        "daily_aptt_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_aptt_lbyn_disch = mapped_column(
        "daily_aptt_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_apttop_lborres_day1 = mapped_column(
        "daily_apttop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_apttop_lborres_disch = mapped_column(
        "daily_apttop_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ast_lborres_day1 = mapped_column(
        "daily_ast_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ast_lborres_disch = mapped_column(
        "daily_ast_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ast_lbyn_day1 = mapped_column(
        "daily_ast_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ast_lbyn_disch = mapped_column(
        "daily_ast_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_astop_lborres_day1 = mapped_column(
        "daily_astop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_astop_lborres_disch = mapped_column(
        "daily_astop_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_baseex_lborres_day1 = mapped_column(
        "daily_baseex_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_baseex_lborres_disch = mapped_column(
        "daily_baseex_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_baseex_lbyn_day1 = mapped_column(
        "daily_baseex_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_baseex_lbyn_disch = mapped_column(
        "daily_baseex_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bil_lborres_day1 = mapped_column(
        "daily_bil_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bil_lborres_disch = mapped_column(
        "daily_bil_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bil_lborresu_day1 = mapped_column(
        "daily_bil_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bil_lborresu_disch = mapped_column(
        "daily_bil_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bil_lbyn_day1 = mapped_column(
        "daily_bil_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bil_lbyn_disch = mapped_column(
        "daily_bil_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bilop_lborres_day1 = mapped_column(
        "daily_bilop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bilop_lborres_disch = mapped_column(
        "daily_bilop_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bun_lborres_day1 = mapped_column(
        "daily_bun_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bun_lborres_disch = mapped_column(
        "daily_bun_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bun_lborresu_day1 = mapped_column(
        "daily_bun_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bun_lborresu_disch = mapped_column(
        "daily_bun_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bun_lbyn_day1 = mapped_column(
        "daily_bun_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bun_lbyn_disch = mapped_column(
        "daily_bun_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bunop_lborres_day1 = mapped_column(
        "daily_bunop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_bunop_lborres_disch = mapped_column(
        "daily_bunop_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_cpk_lby_day1 = mapped_column(
        "daily_cpk_lby.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_cpk_lby_disch = mapped_column(
        "daily_cpk_lby.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_cpk_lbyn_2_day1 = mapped_column(
        "daily_cpk_lbyn_2.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_cpk_lbyn_2_disch = mapped_column(
        "daily_cpk_lbyn_2.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_cpkop_lbyn_2_day1 = mapped_column(
        "daily_cpkop_lbyn_2.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_cpkop_lbyn_2_disch = mapped_column(
        "daily_cpkop_lbyn_2.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_creat_lborres_day1 = mapped_column(
        "daily_creat_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_creat_lborres_disch = mapped_column(
        "daily_creat_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_creat_lborresu_day1 = mapped_column(
        "daily_creat_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_creat_lborresu_disch = mapped_column(
        "daily_creat_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_creat_lbyn_day1 = mapped_column(
        "daily_creat_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_creat_lbyn_disch = mapped_column(
        "daily_creat_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_creatop_lborres_day1 = mapped_column(
        "daily_creatop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_creatop_lborres_disch = mapped_column(
        "daily_creatop_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_crp_lborres_day1 = mapped_column(
        "daily_crp_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_crp_lborres_disch = mapped_column(
        "daily_crp_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_crp_lborresu_day1 = mapped_column(
        "daily_crp_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_crp_lborresu_disch = mapped_column(
        "daily_crp_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_crp_lbyn_day1 = mapped_column(
        "daily_crp_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_crp_lbyn_disch = mapped_column(
        "daily_crp_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_crpop_lborres_day1 = mapped_column(
        "daily_crpop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_crpop_lborres_disch = mapped_column(
        "daily_crpop_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_dop5to15_cmtrt_day1 = mapped_column(
        "daily_dop5to15_cmtrt.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_dop5to15_cmtrt_disch = mapped_column(
        "daily_dop5to15_cmtrt.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_dopgr15_cmtrt_day1 = mapped_column(
        "daily_dopgr15_cmtrt.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_dopgr15_cmtrt_disch = mapped_column(
        "daily_dopgr15_cmtrt.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_dopless5_cmtrt_day1 = mapped_column(
        "daily_dopless5_cmtrt.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_dopless5_cmtrt_disch = mapped_column(
        "daily_dopless5_cmtrt.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_dsstdat_day1 = mapped_column(
        "daily_dsstdat.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_dsstdat_disch = mapped_column(
        "daily_dsstdat.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ecmo_prtrt_day1 = mapped_column(
        "daily_ecmo_prtrt.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ecmo_prtrt_disch = mapped_column(
        "daily_ecmo_prtrt.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_egfr_equation___1_day1 = mapped_column(
        "daily_egfr_equation___1.day1",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_egfr_equation___1_disch = mapped_column(
        "daily_egfr_equation___1.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_egfr_equation___2_day1 = mapped_column(
        "daily_egfr_equation___2.day1",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_egfr_equation___2_disch = mapped_column(
        "daily_egfr_equation___2.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_egfr_equation___3_day1 = mapped_column(
        "daily_egfr_equation___3.day1",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_egfr_equation___3_disch = mapped_column(
        "daily_egfr_equation___3.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_egfr_equation___4_day1 = mapped_column(
        "daily_egfr_equation___4.day1",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_egfr_equation___4_disch = mapped_column(
        "daily_egfr_equation___4.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_egfr_lborres_day1 = mapped_column(
        "daily_egfr_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_egfr_lborres_disch = mapped_column(
        "daily_egfr_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_egfr_lbyn_day1 = mapped_column(
        "daily_egfr_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_egfr_lbyn_disch = mapped_column(
        "daily_egfr_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_egfrop_lborres_day1 = mapped_column(
        "daily_egfrop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_egfrop_lborres_disch = mapped_column(
        "daily_egfrop_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_esr_lborres_day1 = mapped_column(
        "daily_esr_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_esr_lborres_disch = mapped_column(
        "daily_esr_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_esr_lbyn_day1 = mapped_column(
        "daily_esr_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_esr_lbyn_disch = mapped_column(
        "daily_esr_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_esrop_lbyn_day1 = mapped_column(
        "daily_esrop_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_esrop_lbyn_disch = mapped_column(
        "daily_esrop_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ferr_lborres_day1 = mapped_column(
        "daily_ferr_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ferr_lborres_disch = mapped_column(
        "daily_ferr_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ferr_lborresu_day1 = mapped_column(
        "daily_ferr_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ferr_lborresu_disch = mapped_column(
        "daily_ferr_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ferr_lbyn_day1 = mapped_column(
        "daily_ferr_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ferr_lbyn_disch = mapped_column(
        "daily_ferr_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ferrop_lbyn_day1 = mapped_column(
        "daily_ferrop_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ferrop_lbyn_disch = mapped_column(
        "daily_ferrop_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_fi02_lbyn_day1 = mapped_column(
        "daily_fi02_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_fi02_lbyn_disch = mapped_column(
        "daily_fi02_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_fio2_combined_day1 = mapped_column(
        "daily_fio2_combined.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_fio2_combined_disch = mapped_column(
        "daily_fio2_combined.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_fio2_lborres_day1 = mapped_column(
        "daily_fio2_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_fio2_lborres_disch = mapped_column(
        "daily_fio2_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_fio2b_lborres_day1 = mapped_column(
        "daily_fio2b_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_fio2b_lborres_disch = mapped_column(
        "daily_fio2b_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_fio2c_lborres_day1 = mapped_column(
        "daily_fio2c_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_fio2c_lborres_disch = mapped_column(
        "daily_fio2c_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_fio2c_lborres_converted_day1 = mapped_column(
        "daily_fio2c_lborres_converted.day1",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_fio2c_lborres_converted_disch = mapped_column(
        "daily_fio2c_lborres_converted.disch",
        t.VARCHAR(4000, collation="Latin1_General_CI_AS"),
    )
    daily_form_complete_day1 = mapped_column(
        "daily_form_complete.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_form_complete_disch = mapped_column(
        "daily_form_complete.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_gcs_lbyn_day1 = mapped_column(
        "daily_gcs_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_gcs_lbyn_disch = mapped_column(
        "daily_gcs_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_gcs_vsorres_day1 = mapped_column(
        "daily_gcs_vsorres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_gcs_vsorres_disch = mapped_column(
        "daily_gcs_vsorres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_glucose_lborres_day1 = mapped_column(
        "daily_glucose_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_glucose_lborres_disch = mapped_column(
        "daily_glucose_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_glucose_lborresu_day1 = mapped_column(
        "daily_glucose_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_glucose_lborresu_disch = mapped_column(
        "daily_glucose_lborresu.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_glucose_lbyn_day1 = mapped_column(
        "daily_glucose_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_glucose_lbyn_disch = mapped_column(
        "daily_glucose_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_glucoseop_lborres_day1 = mapped_column(
        "daily_glucoseop_lborres.day1",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_glucoseop_lborres_disch = mapped_column(
        "daily_glucoseop_lborres.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_haematocrit_lborres_day1 = mapped_column(
        "daily_haematocrit_lborres.day1",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_haematocrit_lborres_disch = mapped_column(
        "daily_haematocrit_lborres.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_haematocrit_lborresu_day1 = mapped_column(
        "daily_haematocrit_lborresu.day1",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_haematocrit_lborresu_disch = mapped_column(
        "daily_haematocrit_lborresu.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_haematocrit_lbyn_day1 = mapped_column(
        "daily_haematocrit_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_haematocrit_lbyn_disch = mapped_column(
        "daily_haematocrit_lbyn.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_hb_lborres_day1 = mapped_column(
        "daily_hb_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hb_lborres_disch = mapped_column(
        "daily_hb_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hb_lborresu_day1 = mapped_column(
        "daily_hb_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hb_lborresu_disch = mapped_column(
        "daily_hb_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hb_lbyn_day1 = mapped_column(
        "daily_hb_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hb_lbyn_disch = mapped_column(
        "daily_hb_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hba1c_lborres_day1 = mapped_column(
        "daily_hba1c_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hba1c_lborres_disch = mapped_column(
        "daily_hba1c_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hba1c_lborresd_day1 = mapped_column(
        "daily_hba1c_lborresd.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hba1c_lborresd_disch = mapped_column(
        "daily_hba1c_lborresd.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hba1c_lborresnk_day1 = mapped_column(
        "daily_hba1c_lborresnk.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hba1c_lborresnk_disch = mapped_column(
        "daily_hba1c_lborresnk.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hba1c_lborresu_day1 = mapped_column(
        "daily_hba1c_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hba1c_lborresu_disch = mapped_column(
        "daily_hba1c_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hba1cop_lborres_day1 = mapped_column(
        "daily_hba1cop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hba1cop_lborres_disch = mapped_column(
        "daily_hba1cop_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hbop_lborres_day1 = mapped_column(
        "daily_hbop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hbop_lborres_disch = mapped_column(
        "daily_hbop_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hco3_lborres_day1 = mapped_column(
        "daily_hco3_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hco3_lborres_disch = mapped_column(
        "daily_hco3_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hco3_lborresu_day1 = mapped_column(
        "daily_hco3_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hco3_lborresu_disch = mapped_column(
        "daily_hco3_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hco3_lbyn_day1 = mapped_column(
        "daily_hco3_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hco3_lbyn_disch = mapped_column(
        "daily_hco3_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hoterm_day1 = mapped_column(
        "daily_hoterm.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_hoterm_disch = mapped_column(
        "daily_hoterm.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_inotrope_cmyn_day1 = mapped_column(
        "daily_inotrope_cmyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_inotrope_cmyn_disch = mapped_column(
        "daily_inotrope_cmyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_inr_lborres_day1 = mapped_column(
        "daily_inr_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_inr_lborres_disch = mapped_column(
        "daily_inr_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_inrop_lborres_day1 = mapped_column(
        "daily_inrop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_inrop_lborres_disch = mapped_column(
        "daily_inrop_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_invasive_prtrt_day1 = mapped_column(
        "daily_invasive_prtrt.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_invasive_prtrt_disch = mapped_column(
        "daily_invasive_prtrt.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lactate_lborres_day1 = mapped_column(
        "daily_lactate_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lactate_lborres_disch = mapped_column(
        "daily_lactate_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lactate_lborresu_day1 = mapped_column(
        "daily_lactate_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lactate_lborresu_disch = mapped_column(
        "daily_lactate_lborresu.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_lactate_lbyn_day1 = mapped_column(
        "daily_lactate_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lactate_lbyn_disch = mapped_column(
        "daily_lactate_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lactateop_lbyn_day1 = mapped_column(
        "daily_lactateop_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lactateop_lbyn_disch = mapped_column(
        "daily_lactateop_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lbdat_day1 = mapped_column(
        "daily_lbdat.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lbdat_disch = mapped_column(
        "daily_lbdat.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lbperf_day1 = mapped_column(
        "daily_lbperf.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lbperf_disch = mapped_column(
        "daily_lbperf.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ldh_lborres_day1 = mapped_column(
        "daily_ldh_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ldh_lborres_disch = mapped_column(
        "daily_ldh_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ldh_lbyn_day1 = mapped_column(
        "daily_ldh_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ldh_lbyn_disch = mapped_column(
        "daily_ldh_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ldhop_lborres_day1 = mapped_column(
        "daily_ldhop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ldhop_lborres_disch = mapped_column(
        "daily_ldhop_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lymp_lborres_day1 = mapped_column(
        "daily_lymp_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lymp_lborres_disch = mapped_column(
        "daily_lymp_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lymp_lborresu_day1 = mapped_column(
        "daily_lymp_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lymp_lborresu_disch = mapped_column(
        "daily_lymp_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lymp_lbyn_day1 = mapped_column(
        "daily_lymp_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lymp_lbyn_disch = mapped_column(
        "daily_lymp_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lympop_lbyn_day1 = mapped_column(
        "daily_lympop_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_lympop_lbyn_disch = mapped_column(
        "daily_lympop_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_meanart_lbyn_day1 = mapped_column(
        "daily_meanart_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_meanart_lbyn_disch = mapped_column(
        "daily_meanart_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_meanart_vsorres_day1 = mapped_column(
        "daily_meanart_vsorres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_meanart_vsorres_disch = mapped_column(
        "daily_meanart_vsorres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_nasaloxy_cmtrt_day1 = mapped_column(
        "daily_nasaloxy_cmtrt.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_nasaloxy_cmtrt_disch = mapped_column(
        "daily_nasaloxy_cmtrt.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_neuro_cmtrt_day1 = mapped_column(
        "daily_neuro_cmtrt.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_neuro_cmtrt_disch = mapped_column(
        "daily_neuro_cmtrt.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_neutro_lborres_day1 = mapped_column(
        "daily_neutro_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_neutro_lborres_disch = mapped_column(
        "daily_neutro_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_neutro_lborresu_day1 = mapped_column(
        "daily_neutro_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_neutro_lborresu_disch = mapped_column(
        "daily_neutro_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_neutro_lbyn_day1 = mapped_column(
        "daily_neutro_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_neutro_lbyn_disch = mapped_column(
        "daily_neutro_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_neutroop_lbyn_day1 = mapped_column(
        "daily_neutroop_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_neutroop_lbyn_disch = mapped_column(
        "daily_neutroop_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_nitritc_cmtrt_day1 = mapped_column(
        "daily_nitritc_cmtrt.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_nitritc_cmtrt_disch = mapped_column(
        "daily_nitritc_cmtrt.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_noninvasive_prtrt_day1 = mapped_column(
        "daily_noninvasive_prtrt.day1",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_noninvasive_prtrt_disch = mapped_column(
        "daily_noninvasive_prtrt.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_other_prtrt_day1 = mapped_column(
        "daily_other_prtrt.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_other_prtrt_disch = mapped_column(
        "daily_other_prtrt.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pao2_lborres_day1 = mapped_column(
        "daily_pao2_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pao2_lborres_disch = mapped_column(
        "daily_pao2_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pao2_lborresu_day1 = mapped_column(
        "daily_pao2_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pao2_lborresu_disch = mapped_column(
        "daily_pao2_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pao2_lbspec_day1 = mapped_column(
        "daily_pao2_lbspec.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pao2_lbspec_disch = mapped_column(
        "daily_pao2_lbspec.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pao2_lbyn_day1 = mapped_column(
        "daily_pao2_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pao2_lbyn_disch = mapped_column(
        "daily_pao2_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pco2_lborres_day1 = mapped_column(
        "daily_pco2_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pco2_lborres_disch = mapped_column(
        "daily_pco2_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pco2_lborresu_day1 = mapped_column(
        "daily_pco2_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pco2_lborresu_disch = mapped_column(
        "daily_pco2_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pco2_lbyn_day1 = mapped_column(
        "daily_pco2_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pco2_lbyn_disch = mapped_column(
        "daily_pco2_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ph_lborres_day1 = mapped_column(
        "daily_ph_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ph_lborres_disch = mapped_column(
        "daily_ph_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ph_lbyn_day1 = mapped_column(
        "daily_ph_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ph_lbyn_disch = mapped_column(
        "daily_ph_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_plt_lborres_day1 = mapped_column(
        "daily_plt_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_plt_lborres_disch = mapped_column(
        "daily_plt_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_plt_lborresu_day1 = mapped_column(
        "daily_plt_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_plt_lborresu_disch = mapped_column(
        "daily_plt_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_plt_lbyn_day1 = mapped_column(
        "daily_plt_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_plt_lbyn_disch = mapped_column(
        "daily_plt_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pltop_lborres_day1 = mapped_column(
        "daily_pltop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pltop_lborres_disch = mapped_column(
        "daily_pltop_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_potassium_lborres_day1 = mapped_column(
        "daily_potassium_lborres.day1",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_potassium_lborres_disch = mapped_column(
        "daily_potassium_lborres.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_potassium_lborresu_day1 = mapped_column(
        "daily_potassium_lborresu.day1",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_potassium_lborresu_disch = mapped_column(
        "daily_potassium_lborresu.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_potassium_lbyn_day1 = mapped_column(
        "daily_potassium_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_potassium_lbyn_disch = mapped_column(
        "daily_potassium_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_potassiumop_lborres_day1 = mapped_column(
        "daily_potassiumop_lborres.day1",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_potassiumop_lborres_disch = mapped_column(
        "daily_potassiumop_lborres.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_procal_lborres_day1 = mapped_column(
        "daily_procal_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_procal_lborres_disch = mapped_column(
        "daily_procal_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_procal_lbyn_day1 = mapped_column(
        "daily_procal_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_procal_lbyn_disch = mapped_column(
        "daily_procal_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_procalop_lborres_day1 = mapped_column(
        "daily_procalop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_procalop_lborres_disch = mapped_column(
        "daily_procalop_lborres.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_prone_cmtrt_day1 = mapped_column(
        "daily_prone_cmtrt.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_prone_cmtrt_disch = mapped_column(
        "daily_prone_cmtrt.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_prperf_day1 = mapped_column(
        "daily_prperf.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_prperf_disch = mapped_column(
        "daily_prperf.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pt_inr_lbyn_day1 = mapped_column(
        "daily_pt_inr_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pt_inr_lbyn_disch = mapped_column(
        "daily_pt_inr_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pt_lborres_day1 = mapped_column(
        "daily_pt_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pt_lborres_disch = mapped_column(
        "daily_pt_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_pt_lborres_add_inr_day1 = mapped_column(
        "daily_pt_lborres_add_inr.day1",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_pt_lborres_add_inr_disch = mapped_column(
        "daily_pt_lborres_add_inr.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_ptop_lborres_day1 = mapped_column(
        "daily_ptop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_ptop_lborres_disch = mapped_column(
        "daily_ptop_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_rr_day1 = mapped_column(
        "daily_rr.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_rr_disch = mapped_column(
        "daily_rr.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_rr_nk_day1 = mapped_column(
        "daily_rr_nk.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_rr_nk_disch = mapped_column(
        "daily_rr_nk.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_rrt_cmtrt_day1 = mapped_column(
        "daily_rrt_cmtrt.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_rrt_cmtrt_disch = mapped_column(
        "daily_rrt_cmtrt.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_sa02_lbyn_day1 = mapped_column(
        "daily_sa02_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_sa02_lbyn_disch = mapped_column(
        "daily_sa02_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_samples_day1 = mapped_column(
        "daily_samples.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_samples_disch = mapped_column(
        "daily_samples.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_samples_kitno_day1 = mapped_column(
        "daily_samples_kitno.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_samples_kitno_disch = mapped_column(
        "daily_samples_kitno.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_sao2_lborres_day1 = mapped_column(
        "daily_sao2_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_sao2_lborres_disch = mapped_column(
        "daily_sao2_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_sodium_lborres_day1 = mapped_column(
        "daily_sodium_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_sodium_lborres_disch = mapped_column(
        "daily_sodium_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_sodium_lborresu_day1 = mapped_column(
        "daily_sodium_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_sodium_lborresu_disch = mapped_column(
        "daily_sodium_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_sodium_lbyn_day1 = mapped_column(
        "daily_sodium_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_sodium_lbyn_disch = mapped_column(
        "daily_sodium_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_sodiumop_lborres_day1 = mapped_column(
        "daily_sodiumop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_sodiumop_lborres_disch = mapped_column(
        "daily_sodiumop_lborres.disch",
        t.VARCHAR(1000, collation="Latin1_General_CI_AS"),
    )
    daily_temp_vsorres_day1 = mapped_column(
        "daily_temp_vsorres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_temp_vsorres_disch = mapped_column(
        "daily_temp_vsorres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_temp_vsorresnk_day1 = mapped_column(
        "daily_temp_vsorresnk.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_temp_vsorresnk_disch = mapped_column(
        "daily_temp_vsorresnk.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_temp_vsorresu_day1 = mapped_column(
        "daily_temp_vsorresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_temp_vsorresu_disch = mapped_column(
        "daily_temp_vsorresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_trach_prperf_day1 = mapped_column(
        "daily_trach_prperf.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_trach_prperf_disch = mapped_column(
        "daily_trach_prperf.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_urine_lborres_day1 = mapped_column(
        "daily_urine_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_urine_lborres_disch = mapped_column(
        "daily_urine_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_urine_lbyn_day1 = mapped_column(
        "daily_urine_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_urine_lbyn_disch = mapped_column(
        "daily_urine_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_wbc_lborres_day1 = mapped_column(
        "daily_wbc_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_wbc_lborres_disch = mapped_column(
        "daily_wbc_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_wbc_lborresu_day1 = mapped_column(
        "daily_wbc_lborresu.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_wbc_lborresu_disch = mapped_column(
        "daily_wbc_lborresu.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_wbc_lbyn_day1 = mapped_column(
        "daily_wbc_lbyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_wbc_lbyn_disch = mapped_column(
        "daily_wbc_lbyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_wbcop_lborres_day1 = mapped_column(
        "daily_wbcop_lborres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    daily_wbcop_lborres_disch = mapped_column(
        "daily_wbcop_lborres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dehydration_vsorres = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dementia_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    demographics_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dexamethasone2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dexamethasone2_days = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone2_dose = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone2_freq = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone2_other_freq = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone2_route = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dexamethasone3_days = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone3_dose = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone3_freq = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone3_other_freq = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone3_route = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone4 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dexamethasone4_days = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone4_dose = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone4_freq = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone4_other_freq = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone4_route = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone5 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dexamethasone5_days = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone5_dose = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone5_freq = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone5_other_freq = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone5_route = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone_days = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone_dose = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone_freq = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone_other_freq = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dexamethasone_route = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    diabetes_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    diabetes_type_mhyn = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    diabetescom_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    diabp_vsyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    diarrhoea_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    diarrhoea_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    diastolic_vsorres_day1 = mapped_column(
        "diastolic_vsorres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    diastolic_vsorres_disch = mapped_column(
        "diastolic_vsorres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    diastolic_vsyn_day1 = mapped_column(
        "diastolic_vsyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    diastolic_vsyn_disch = mapped_column(
        "diastolic_vsyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dlvrdtc_rptestcd = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dlvrdtc_rptestcd_out = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    dshosp = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dsstdat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dsstdtc = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dsstdtc_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dsstdtc_v2_nk = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dsstdtcyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dsterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dsterm_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dvt_ceterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    dyspnoe = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    earpain_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    earpain_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    egestage_rptestcd = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    endocarditis_aeterm = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    erendat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    erendat_2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    estgest = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ethnic___1 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ethnic___10 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ethnic___2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ethnic___3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ethnic___4 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ethnic___5 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ethnic___6 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ethnic___7 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ethnic___8 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ethnic___9 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ethnicity = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    excorp_prdur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    excorp_still_on = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    extracorp_prtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    fatigue_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    fatigue_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    fever = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    fever_ceoccur_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    fever_ceoccur_v3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    final_outcome_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    flw_any_day1 = mapped_column(
        "flw_any.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    flw_any_disch = mapped_column(
        "flw_any.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    gastro_ceterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    headache_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    headache_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    healthwork_erterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    heartfailure_ceterm = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    hodur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    hooccur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    hostdat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    hostdat_transfer = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    hostdat_transfernk = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    hosttim = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    hr_vsorres = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    hr_vsyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    hyperglycemia_aeterm = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    hypertension_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    hypoglycemia_ceterm = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    icu_hoendat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    icu_hoendat2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    icu_hoendat2_nk = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    icu_hoendat3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    icu_hoendat3_nk = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    icu_hoendatnk = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    icu_hostdat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    icu_hostdat2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    icu_hostdat2_nk = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    icu_hostdat3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    icu_hostdat3_nk = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    icu_hostdatnk = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    icu_hostillin = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    icu_hoterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    icu_no = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    il6_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    il6_cmtrt_first = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    il6_cmtrt_last = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    il6_cmtrt_other = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    imd_quintile = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    immno_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    inclusion_criteria_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    infect = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    infect_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    infectious_respiratory_disease_pathogen_diagnosis_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    infectuk_mborres = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    infiltrates_faorres_day1 = mapped_column(
        "infiltrates_faorres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    infiltrates_faorres_disch = mapped_column(
        "infiltrates_faorres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    inflammatory_mss = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    influ_mbcat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    influ_mbyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    influ_mbyn_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    influenza_2021_vaccine = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    influenza_2021_vaccined = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    influenza_2021_vaccined_nk = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    influother_mborres = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    influothera_mborres = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    inhalednit_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    inotrop_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    inotrope_cmdur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    inotrope_still_on = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    interleukin_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    interleukin_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    invasive_prdur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    invasive_proccur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    invasive_still_on = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ischaemia_ceterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    jointpain_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    jointpain_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    labwork_erterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    liverdysfunction_ceterm = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    lowerchest_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    lowerchest_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    lymp_ceoccur_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    lymp_ceoccur_v3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    malignantneo_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    malnutrition_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    mbperf = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    meningitis_ceterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    mildliver = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    modliv = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    myalgia_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    myalgia_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    myocarditis_ceterm = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    neuro_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    neuro_comp = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    nhs_region = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    ni_site = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    no_symptoms = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    no_symptoms_v3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    noncorona_expphi = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    noninvasive_proccur = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    obesity_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    offlabel_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    offlabel_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    onset2admission = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    onset_and_admission_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    othantiviral2_cmyn = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    othantiviral3_cmtrt = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    othantiviral3_cmyn = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    othantiviral4_cmtrt = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    othantiviral4_cmyn = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    othantiviral5_cmtrt = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    othantiviral5_cmyn = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    othantiviral_cmtrt = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    other_ceoccur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    other_ceterm = mapped_column(t.VARCHAR(4000, collation="Latin1_General_CI_AS"))
    other_cm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    other_cmoccur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    other_cmtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    other_cmyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    other_ethnic = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    other_mborres = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    other_mbyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    other_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    othhantiviral2_cmtrt = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    outcome_complete = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    oxy_vsorres = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    oxy_vsorresu = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    oxy_vsyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    oxygen_cmoccur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    oxygen_proccur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    oxygen_proccur_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    oxygenhf_cmoccur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    pancreat_ceterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    participant_identification_number_pin_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    pcr_path_diag___0 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    pcr_path_diag___1 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    pcr_path_diag___10 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    pcr_path_diag___2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    pcr_path_diag___3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    pcr_path_diag___4 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    pcr_path_diag___5 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    pcr_path_diag___6 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    pcr_path_diago = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    pleuraleff_ceterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    pneumothorax_ceterm = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    postpart_rptestcd = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    postpart_rptestcd_out = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    preadmission_treatment_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    pregout_rptestcd = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    pregout_rptestcd_out = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    pregyn_rptestcd = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    prev_subjid = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    prev_subjid_nk = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    pronevent_prtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    pulmthromb_ceterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    rash_ceoccur_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    rash_ceoccur_v3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    readm_cov19 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    readminreas = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    readminreasnk = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reason_for_withdrawal = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    recruitment = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_antigen = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_antigend = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_asymptomatic = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    reinf_cestdat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_pcr = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_pcrd = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_pre_adm_hosp = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    reinf_pre_casiriv = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_pre_chloro_hchlo = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    reinf_pre_conv_plasma = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    reinf_pre_dexameth = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    reinf_pre_ecmo = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_pre_hdu_icu = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_pre_interferon = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    reinf_pre_inv_vent = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    reinf_pre_lopin_riton = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    reinf_pre_oxygen = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_pre_remdesivir = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    reinf_pre_steroid = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_pre_tociliz = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_prev_enrol = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_serology = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_serologyd = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinf_treat_none = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    reinfection_form_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    remdes_cmtrt_first = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    remdes_cmtrt_last = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    remdesivir_day1 = mapped_column(
        "remdesivir.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    remdesivir_disch = mapped_column(
        "remdesivir.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    remdesivir_day_day1 = mapped_column(
        "remdesivir_day.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    remdesivir_day_disch = mapped_column(
        "remdesivir_day.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    remdesivir_last_dose_day1 = mapped_column(
        "remdesivir_last_dose.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    remdesivir_last_dose_disch = mapped_column(
        "remdesivir_last_dose.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    renal_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    renal_proccur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    renalinjury_ceterm = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    research_samples_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    rhabdomyolsis_ceterm = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    rheumatologic_mhyn = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    rr_vsorres = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    rr_vsyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    rrt_prtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    rrt_still_on = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    rrt_totdur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    rsv_mbcat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    rsv_mbcat_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    runnynose_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    runnynose_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    sample_date = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    sample_kit = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    sample_obtained = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    seizure_ceterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    seizures_cecoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    seizures_cecoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    sex = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    shortbreath_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    shortbreath_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    site_type = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    siteid = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    siteid_transfernk = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    siteid_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    siteid_v2_nk = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    siteidnk = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    siteyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    siteyn_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    siteyn_v3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    skinulcers_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    skinulcers_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    smoking_mhyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    smoking_mhyn_2levels = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    sorethroat_ceoccur_v2 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    sorethroat_ceoccur_v3 = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    status = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    stercap_vsorres = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    stercap_vsyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    stroke_ceterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    study_1_id = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    study_1_name = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    study_2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    study_2_id = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    study_2_name = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    study_3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    study_3_id = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    study_3_name = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    study_participation_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    subjid_transfer = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    subjidcat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    subjidcat_transfer = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    subjidcat_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    suppds_qval = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    suppds_qval_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    supper_trcity = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    supper_trcity_2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    supper_trcntry = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    supper_trcntry_2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    surgefacil = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    susp_reinf = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    symptoms_epi_animal = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    symptoms_epi_healthfac = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    symptoms_epi_lab = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    symptoms_epi_pathogen = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    symptoms_epi_physical = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    symptoms_epi_travel = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    sysbp_vsorres = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    sysbp_vsyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    systolic_vsorres_day1 = mapped_column(
        "systolic_vsorres.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    systolic_vsorres_disch = mapped_column(
        "systolic_vsorres.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    systolic_vsyn_day1 = mapped_column(
        "systolic_vsyn.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    systolic_vsyn_disch = mapped_column(
        "systolic_vsyn.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    temp_vsorres = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    temp_vsorresu = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    temp_vsyn = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    tiers_consent_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    tiers_faorres___1 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    tiers_faorres___2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    tiers_faorres___3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    tracheo_prtrt = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    transfer_subjid = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    travel_erterm = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    travel_erterm_2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    treatment_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    vaccine_covid_trial = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    vaccine_covid_triald = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    version_9_7 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    vomit_ceoccur_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    vomit_ceoccur_v3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    vrialpneu_ceoccur = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    vulnerable_cancers = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    vulnerable_copd = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    vulnerable_immuno = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    vulnerable_no_nk = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    vulnerable_preg = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    vulnerable_scid = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    vulnerable_transplant = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    wheeze_ceoccur_v2 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    wheeze_ceoccur_v3 = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    withddat = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    withdrawal_form_complete = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    withdreas = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    withdtype = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    xray_prperf_day1 = mapped_column(
        "xray_prperf.day1", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    xray_prperf_disch = mapped_column(
        "xray_prperf.disch", t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )


class ISARIC_Patient_Data(Base):
    __tablename__ = "ISARIC_Patient_Data"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    adeno_mbcat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    adeno_mbcat_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    aneamia_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ards_ceoccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    arrhythmia_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    bact_mborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    bacteraemia_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    bacteria_mborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    bactpneu_ceoccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    bronchio_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cardiacarrest_ceterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    cardiomyopathy_ceterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    clinicalpneu_mborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    cmdose = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cmdose_unit = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cmdose_unitoth = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cmdosfrq = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cmdosfrqoth = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cmroute = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cmrouteoth = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cmtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    coagulo_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    conv_plasma_cmyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    corna_mbcat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    corna_mbcaty = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    coronaother_mborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    cov19sars_mbyn_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cryptogenic_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_alt_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_alt_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_altop_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_aptt_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_aptt_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_apttop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_ast_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ast_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_astop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_bil_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_bil_lborresu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_bil_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_bilop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_bun_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_bun_lborresu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_bun_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_bunop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_cpk_lby = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_cpk_lbyn_2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_cpkop_lbyn_2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_creat_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_creat_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_creat_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_creatop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_crp_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_crp_lborresu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_crp_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_crpop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_dop5to15_cmtrt = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_dopgr15_cmtrt = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_dopless5_cmtrt = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_dsstdat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ecmo_prtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_esr_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_esr_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_esrop_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ferr_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ferr_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_ferr_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ferrop_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_glucose_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_glucose_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_glucose_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_glucoseop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_haematocrit_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_haematocrit_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_haematocrit_lbyn = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_hb_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_hb_lborresu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_hb_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_hbop_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_hoterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_inotrope_cmyn = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_inr_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_inrop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_invasive_prtrt = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_lactate_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_lactate_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_lactate_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_lactateop_lbyn = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_lbdat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_lbperf = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ldh_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ldh_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ldhop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_lymp_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_lymp_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_lymp_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_lympop_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_mbperf = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_nasaloxy_cmtrt = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_neuro_cmtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_neutro_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_neutro_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_neutro_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_neutroop_lbyn = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_nitritc_cmtrt = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_noninvasive_prtrt = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_other_prtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_plt_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_plt_lborresu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_plt_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_pltop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_potassium_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_potassium_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_potassium_lbyn = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_potassiumop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_procal_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_procal_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_procalop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_prone_cmtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_prperf = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_pt_inr_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_pt_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ptop_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_rrt_cmtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_sodium_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_sodium_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_sodium_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_sodiumop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_trach_prperf = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_wbc_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_wbc_lborresu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_wbc_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_wbcop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    dshosp = mapped_column(t.VARCHAR(4000, collation="Latin1_General_CI_AS"))
    dsstdtc = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    dsstdtc_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    dsstdtc_v2_nk = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    dsstdtcyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    dsterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    dsterm_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    dvt_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    endocarditis_aeterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    excorp_prdur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    excorp_still_on = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    extracorp_prtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    final_outcome_complete = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    gastro_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    heartfailure_ceterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    hodur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    hyperglycemia_aeterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    hypoglycemia_ceterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    icu_hoendat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    icu_hoendat2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    icu_hoendat2_nk = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    icu_hoendat3 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    icu_hoendat3_nk = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    icu_hoendatnk = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    icu_hostdat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    icu_hostdat2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    icu_hostdat2_nk = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    icu_hostdat3 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    icu_hostdat3_nk = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    icu_hostdatnk = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    icu_hostillin = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    icu_hoterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    icu_no = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    infectious_respiratory_disease_pathogen_diagnosis_complete = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    infectuk_mborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    influ_mbcat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    influ_mbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    influ_mbyn_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    influother_mborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    influothera_mborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    inhalednit_cmtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    inotrop_cmtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    inotrope_cmdur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    inotrope_still_on = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    interleukin_cmtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    interleukin_cmyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    invasive_prdur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    invasive_proccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    invasive_still_on = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ischaemia_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    liverdysfunction_ceterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    mbdat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbdat_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbdat_v3 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbmethod = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mborres_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbperf = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbspec = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbspec_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbspec_v3 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd = mapped_column(t.VARCHAR(2000, collation="Latin1_General_CI_AS"))
    mbtestcd_bc = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd_bco = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd_csf = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd_csfo = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd_drs = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd_drso = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd_fst = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd_fsto = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd_nsth = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd_nstho = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd_sp = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd_spo = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd_ur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd_uro = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mbtestcd_v3 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    meningitis_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    myocarditis_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    neuro_comp = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    no_medication = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    noninvasive_proccur = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    other_ceoccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    other_cm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    other_cmoccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    other_cmtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    other_cmyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    other_mbmethod = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    other_mborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    other_mbspec = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    other_mbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    outcome_complete = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    oxygen_cmoccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    oxygen_proccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    oxygen_proccur_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    oxygenhf_cmoccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pancreat_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pcr_path_diag___0 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pcr_path_diag___1 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pcr_path_diag___10 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pcr_path_diag___2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pcr_path_diag___3 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pcr_path_diag___4 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pcr_path_diag___5 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pcr_path_diag___6 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pcr_path_diago = mapped_column(t.VARCHAR(2000, collation="Latin1_General_CI_AS"))
    pleuraleff_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pneumothorax_ceterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    pronevent_prtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pulmthromb_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    remdesivir = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    remdesivir_day = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    remdesivir_last_dose = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    renal_proccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    renalinjury_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    rhabdomyolsis_ceterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    rrt_prtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    rrt_still_on = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    rrt_totdur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    rsv_mbcat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    rsv_mbcat_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    seizure_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    stroke_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    suppds_qval = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    suppds_qval_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    tracheo_prtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    vrialpneu_ceoccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))


class ISARIC_Patient_Data_TopLine(Base):
    __tablename__ = "ISARIC_Patient_Data_TopLine"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    abdopain_ceoccur_v2 = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    admission2onset = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    admission_diabp_vsorres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    admission_month = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    admission_week = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    age_estimateyears = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    age_estimateyearsu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    age_factor_19_no_neonates = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    age_factor_19_with_neonates = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    agedatyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ageusia_ceoccur_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    aidshiv_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    all_antiviral = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    all_cardiac_comp = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    all_ecmo = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    all_imm_mod = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    all_inotropes = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    all_invasive = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    all_ivig = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    all_noninvasive = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    alt_reason_admit = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    aneamia_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    anosmia_ceoccur_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    antibiotic = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    antiviral = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    any_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    any_max_steroid = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    any_trach = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    apdm_age = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    aplb_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    aplb_lbperf = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    apsc_brdisdat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    apsc_brfedind = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    apsc_brfedindy = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    apsc_dvageind = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    apsc_gestout = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    apsc_vcageind = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    apvs_weight = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    apvs_weightnk = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    apvs_weightu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ards_ceoccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ari = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    arm_participant = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    arrhythmia_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    assess_age = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    assess_age_minus_age = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    assess_or_admit_date = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    asthma_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    asthma_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    asymp = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    asymp_or_incident = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    bacteraemia_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    bactpneu_ceoccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    bleed_ceoccur_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    bleed_ceterm_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    bmj_pt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    bronchio_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    calc_age = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cardiac_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cardiac_comp = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cardiacarrest_ceterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    cardiomyopathy_ceterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    cestdat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    chestpain_ceoccur_v2 = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    chrincard = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    chronic_nsaid_cmoccur = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    chronichaemo_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    chronicneu_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    chronicpul_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    coagulo_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    comorb_count = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    confusion_ceoccur_v2 = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    conjunct_ceoccur_v2 = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    coriona_ieorres2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    coriona_ieorres3 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    corona_ieorres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cough = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cough_ceoccur_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    coughhb_ceoccur_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    coughsput_ceoccur_v2 = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    country = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    country_pcds = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    covid19_vaccine = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cryptogenic_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cxr_count = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    cxr_done = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_alt_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_alt_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_altop_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_aptt_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_aptt_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_apttop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_ast_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ast_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_bil_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_bil_lborresu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_bil_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_bilop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_bun_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_bun_lborresu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_bun_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_bunop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_cpk_lby = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_cpk_lbyn_2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_cpkop_lbyn_2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_creat_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_creat_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_creat_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_creatop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_crp_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_crp_lborresu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_crp_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_crpop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_dsstdat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_esr_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_esr_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ferr_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ferr_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_ferr_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ferrop_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_glucose_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_glucose_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_glucose_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_glucoseop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_haematocrit_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_haematocrit_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_haematocrit_lbyn = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_hb_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_hb_lborresu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_hb_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_hbop_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_inr_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_lactate_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_lactate_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_lactate_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_lactateop_lbyn = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_lbdat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ldh_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ldh_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_lymp_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_lymp_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_lymp_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_lympop_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_neutro_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_neutro_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_neutro_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_neutroop_lbyn = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_plt_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_plt_lborresu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_plt_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_pltop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_potassium_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_potassium_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_potassium_lbyn = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_potassiumop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_procal_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_procal_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_procalop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_pt_inr_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_pt_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_ptop_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_sodium_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_sodium_lborresu = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_sodium_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_sodiumop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    daily_wbc_lborres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_wbc_lborresu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_wbc_lbyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    daily_wbcop_lborres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    death = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    dehydration_vsorres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    dementia_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    diabetes_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    diabetes_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    diabetes_type_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    diabetescom_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    dialysis = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    diarrhoea_ceoccur_v2 = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    dlvrdtc_rptestcd = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    dsstdat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    dsstdtc = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    dsterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    dvt_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    dyspnoe = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    earpain_ceoccur_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ecmo = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    egestage_rptestcd = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    endocarditis_aeterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    estgest = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ethnic___1 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ethnic___10 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ethnic___2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ethnic___3 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ethnic___4 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ethnic___5 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ethnic___6 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ethnic___7 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ethnic___8 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ethnic___9 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ethnicity = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    fatigue_ceoccur_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    fever = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    fever_all = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    fever_ceoccur_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    first_wave = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    gastro_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    genetic_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    haem_onc_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    has_picu = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    headache_ceoccur_v2 = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    heartfailure_ceterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    high_flow_o2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    hooccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    hostdat = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    hostdat_transfer = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    hostdat_transfernk = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    hosttim = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    hr_vsorres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    hyperglycemia_aeterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    hyperinflam_WHO = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    hypertension_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    hypoglycemia_ceterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    imm_sup_all = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    immno_cmtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    incidental_covid = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    infant = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    infect_cmtrt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    infiltrates_faorres = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    infiltrates_yn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    inflammatory_mss = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    influenza_2021_vaccine = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    influenza_2021_vaccined = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    inotrope = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ischaemia_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    ivig_freetext = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    jointpain_ceoccur_v2 = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    ld_asd_ad_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    liver_gi_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    liverdysfunction_ceterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    los = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    los2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    los_covid = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    los_covid2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    lowerchest_ceoccur_v2 = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    lymp_ceoccur_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    malignantneo_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    malnutrition_comorb = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    malnutrition_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    max_crp = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    max_ferritin = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    max_inr = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    max_pt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    max_resp_support = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    meningitis_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    metabolic_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    mildliver = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    min_systolic = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    misc_cardiac = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    misc_considered_pims = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    misc_final_status = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    misc_immunomod = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    misc_iv_steroids = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    misc_ivig = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    misc_oral_steroids = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    misc_pcr = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    misc_serology = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    modliv = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    myalgia_ceoccur_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    myocarditis_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    neonate = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    neuro_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    neuro_comp = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    neurodisab_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    nhs_region = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    nitric = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    no_symptoms = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    nosocomial14 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    nosocomial2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    nosocomial5 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    nosocomial7 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    obesity_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    obesity_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    onset2admission = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    other_ceoccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    other_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    other_endo_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    other_ethnic = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    other_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    oxy_vsorres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pancreat_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pews_crt = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pews_gcs = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pews_hr = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pews_o2_rx = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pews_over_2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pews_rr = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pews_sbp = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pews_spo2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pews_temp = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pews_total = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pims_freetext = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pleuraleff_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pneumothorax_ceterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    postpart_rptestcd = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pregout_rptestcd = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pregyn_rptestcd = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    preterm_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    prone = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    pulmthromb_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    rash_ceoccur_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    readm_cov19 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    readminreas = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    renal_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    renal_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    renalinjury_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    resp_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    rhabdomyolsis_ceterm = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    rheum_comorb = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    rheumatologic_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    rr_vsorres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    runnynose_ceoccur_v2 = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    second_wave = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    seizure_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    seizures_cecoccur_v2 = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    sex = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    shortbreath_ceoccur_v2 = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    skinulcers_ceoccur_v2 = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    smoking_mhyn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    sorethroat_ceoccur_v2 = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    stercap_vsorres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    stroke_ceterm = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    supp_o2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    surgefacil = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    susp_reinf = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    symp_or_assess_date = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    symptom_count = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    symptom_missing_count = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    sysbp_vsorres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    temp_vsorres = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    vaccine_covid_trial = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    vomit_ceoccur_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    vrialpneu_ceoccur = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    vulnerable_cancers = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    vulnerable_copd = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    vulnerable_immuno = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    vulnerable_preg = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    vulnerable_scid = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    vulnerable_transplant = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    wave = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    wheeze_ceoccur_v2 = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    who_cardiac = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    who_coag = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    who_conjunct_rash = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    who_criteria = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    who_crp = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    who_fever = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    who_five_criteria = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    who_gi = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    who_hypotension = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    xray_prperf = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))


class LatestBuildTime(Base):
    __tablename__ = "LatestBuildTime"
    _pk = mapped_column(t.Integer, primary_key=True)

    DtLatestBuild = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )


class MPI(Base):
    __tablename__ = "MPI"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Birth_Month = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Care_Home_Flag = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Data_Source = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    DateFrom = mapped_column(t.Date)
    DateTo = mapped_column(t.Date)
    Date_Added = mapped_column(t.Date)
    Death_Month = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Gender = mapped_column(t.VARCHAR(1, collation="Latin1_General_CI_AS"))
    Latest_Flag = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Living_Alone_Flag = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Living_with_elderly_Flag = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Living_with_young_Flag = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    OS_Property_Classification = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Original_Posting_Date = mapped_column(t.Date)
    Pseudo_parent_uprn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    Pseudo_uprn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    RP_of_Death = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Rural_Urban_Classification = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    ServiceType = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    private_outdoor_space = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    private_outdoor_space_area = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    property_type = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))


class MSOA_PopulationEstimates_2019(Base):
    __tablename__ = "MSOA_PopulationEstimates_2019"
    _pk = mapped_column(t.Integer, primary_key=True)

    Age_0 = mapped_column(t.Integer, nullable=False, default=0)
    Age_1 = mapped_column(t.Integer, nullable=False, default=0)
    Age_10 = mapped_column(t.Integer, nullable=False, default=0)
    Age_11 = mapped_column(t.Integer, nullable=False, default=0)
    Age_12 = mapped_column(t.Integer, nullable=False, default=0)
    Age_13 = mapped_column(t.Integer, nullable=False, default=0)
    Age_14 = mapped_column(t.Integer, nullable=False, default=0)
    Age_15 = mapped_column(t.Integer, nullable=False, default=0)
    Age_16 = mapped_column(t.Integer, nullable=False, default=0)
    Age_17 = mapped_column(t.Integer, nullable=False, default=0)
    Age_18 = mapped_column(t.Integer, nullable=False, default=0)
    Age_19 = mapped_column(t.Integer, nullable=False, default=0)
    Age_2 = mapped_column(t.Integer, nullable=False, default=0)
    Age_20 = mapped_column(t.Integer, nullable=False, default=0)
    Age_21 = mapped_column(t.Integer, nullable=False, default=0)
    Age_22 = mapped_column(t.Integer, nullable=False, default=0)
    Age_23 = mapped_column(t.Integer, nullable=False, default=0)
    Age_24 = mapped_column(t.Integer, nullable=False, default=0)
    Age_25 = mapped_column(t.Integer, nullable=False, default=0)
    Age_26 = mapped_column(t.Integer, nullable=False, default=0)
    Age_27 = mapped_column(t.Integer, nullable=False, default=0)
    Age_28 = mapped_column(t.Integer, nullable=False, default=0)
    Age_29 = mapped_column(t.Integer, nullable=False, default=0)
    Age_3 = mapped_column(t.Integer, nullable=False, default=0)
    Age_30 = mapped_column(t.Integer, nullable=False, default=0)
    Age_31 = mapped_column(t.Integer, nullable=False, default=0)
    Age_32 = mapped_column(t.Integer, nullable=False, default=0)
    Age_33 = mapped_column(t.Integer, nullable=False, default=0)
    Age_34 = mapped_column(t.Integer, nullable=False, default=0)
    Age_35 = mapped_column(t.Integer, nullable=False, default=0)
    Age_36 = mapped_column(t.Integer, nullable=False, default=0)
    Age_37 = mapped_column(t.Integer, nullable=False, default=0)
    Age_38 = mapped_column(t.Integer, nullable=False, default=0)
    Age_39 = mapped_column(t.Integer, nullable=False, default=0)
    Age_4 = mapped_column(t.Integer, nullable=False, default=0)
    Age_40 = mapped_column(t.Integer, nullable=False, default=0)
    Age_41 = mapped_column(t.Integer, nullable=False, default=0)
    Age_42 = mapped_column(t.Integer, nullable=False, default=0)
    Age_43 = mapped_column(t.Integer, nullable=False, default=0)
    Age_44 = mapped_column(t.Integer, nullable=False, default=0)
    Age_45 = mapped_column(t.Integer, nullable=False, default=0)
    Age_46 = mapped_column(t.Integer, nullable=False, default=0)
    Age_47 = mapped_column(t.Integer, nullable=False, default=0)
    Age_48 = mapped_column(t.Integer, nullable=False, default=0)
    Age_49 = mapped_column(t.Integer, nullable=False, default=0)
    Age_5 = mapped_column(t.Integer, nullable=False, default=0)
    Age_50 = mapped_column(t.Integer, nullable=False, default=0)
    Age_51 = mapped_column(t.Integer, nullable=False, default=0)
    Age_52 = mapped_column(t.Integer, nullable=False, default=0)
    Age_53 = mapped_column(t.Integer, nullable=False, default=0)
    Age_54 = mapped_column(t.Integer, nullable=False, default=0)
    Age_55 = mapped_column(t.Integer, nullable=False, default=0)
    Age_56 = mapped_column(t.Integer, nullable=False, default=0)
    Age_57 = mapped_column(t.Integer, nullable=False, default=0)
    Age_58 = mapped_column(t.Integer, nullable=False, default=0)
    Age_59 = mapped_column(t.Integer, nullable=False, default=0)
    Age_6 = mapped_column(t.Integer, nullable=False, default=0)
    Age_60 = mapped_column(t.Integer, nullable=False, default=0)
    Age_61 = mapped_column(t.Integer, nullable=False, default=0)
    Age_62 = mapped_column(t.Integer, nullable=False, default=0)
    Age_63 = mapped_column(t.Integer, nullable=False, default=0)
    Age_64 = mapped_column(t.Integer, nullable=False, default=0)
    Age_65 = mapped_column(t.Integer, nullable=False, default=0)
    Age_66 = mapped_column(t.Integer, nullable=False, default=0)
    Age_67 = mapped_column(t.Integer, nullable=False, default=0)
    Age_68 = mapped_column(t.Integer, nullable=False, default=0)
    Age_69 = mapped_column(t.Integer, nullable=False, default=0)
    Age_7 = mapped_column(t.Integer, nullable=False, default=0)
    Age_70 = mapped_column(t.Integer, nullable=False, default=0)
    Age_71 = mapped_column(t.Integer, nullable=False, default=0)
    Age_72 = mapped_column(t.Integer, nullable=False, default=0)
    Age_73 = mapped_column(t.Integer, nullable=False, default=0)
    Age_74 = mapped_column(t.Integer, nullable=False, default=0)
    Age_75 = mapped_column(t.Integer, nullable=False, default=0)
    Age_76 = mapped_column(t.Integer, nullable=False, default=0)
    Age_77 = mapped_column(t.Integer, nullable=False, default=0)
    Age_78 = mapped_column(t.Integer, nullable=False, default=0)
    Age_79 = mapped_column(t.Integer, nullable=False, default=0)
    Age_8 = mapped_column(t.Integer, nullable=False, default=0)
    Age_80 = mapped_column(t.Integer, nullable=False, default=0)
    Age_81 = mapped_column(t.Integer, nullable=False, default=0)
    Age_82 = mapped_column(t.Integer, nullable=False, default=0)
    Age_83 = mapped_column(t.Integer, nullable=False, default=0)
    Age_84 = mapped_column(t.Integer, nullable=False, default=0)
    Age_85 = mapped_column(t.Integer, nullable=False, default=0)
    Age_86 = mapped_column(t.Integer, nullable=False, default=0)
    Age_87 = mapped_column(t.Integer, nullable=False, default=0)
    Age_88 = mapped_column(t.Integer, nullable=False, default=0)
    Age_89 = mapped_column(t.Integer, nullable=False, default=0)
    Age_9 = mapped_column(t.Integer, nullable=False, default=0)
    Age_90_Plus = mapped_column(t.Integer, nullable=False, default=0)
    Age_All = mapped_column(t.Integer, nullable=False, default=0)
    LA_Code_2019 = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    LA_Code_2020 = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    MSOA_Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class MedicationDictionary(Base):
    __tablename__ = "MedicationDictionary"
    _pk = mapped_column(t.Integer, primary_key=True)

    CompanyName = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    DMD_ID = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    Form = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    FullName = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    MultilexDrug_ID = mapped_column(t.VARCHAR(767, collation="Latin1_General_CI_AS"))
    PackDescription = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    ProductId = mapped_column(t.BIGINT, nullable=False, default=0)
    RootName = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Strength = mapped_column(t.VARCHAR(500, collation="Latin1_General_CI_AS"))


class MedicationDictionary_BUILDING(Base):
    __tablename__ = "MedicationDictionary_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    CompanyName = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    DMD_ID = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    Form = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    FullName = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    MultilexDrug_ID = mapped_column(t.VARCHAR(767, collation="Latin1_General_CI_AS"))
    PackDescription = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    ProductId = mapped_column(t.BIGINT, nullable=False, default=0)
    RootName = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Strength = mapped_column(t.VARCHAR(500, collation="Latin1_General_CI_AS"))


class MedicationIssue(Base):
    __tablename__ = "MedicationIssue"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ConsultationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Consultation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Dose = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    EndDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    MedicationIssue_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    MedicationStatus = mapped_column(t.Integer, nullable=False, default=0)
    MultilexDrug_ID = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    Quantity = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    RepeatMedication_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    StartDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")


class MedicationIssue_BUILDING(Base):
    __tablename__ = "MedicationIssue_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ConsultationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Consultation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Dose = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    EndDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    MedicationIssue_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    MedicationStatus = mapped_column(t.Integer, nullable=False, default=0)
    MultilexDrug_ID = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    Quantity = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    RepeatMedication_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    StartDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")


class MedicationRepeat(Base):
    __tablename__ = "MedicationRepeat"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ConsultationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Consultation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Dose = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    EndDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    MedicationRepeat_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    MedicationStatus = mapped_column(t.Integer, nullable=False, default=0)
    MultilexDrug_ID = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    Quantity = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    StartDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")


class MedicationRepeat_BUILDING(Base):
    __tablename__ = "MedicationRepeat_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ConsultationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Consultation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Dose = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    EndDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    MedicationRepeat_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    MedicationStatus = mapped_column(t.Integer, nullable=False, default=0)
    MultilexDrug_ID = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    Quantity = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    StartDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")


class MedicationSensitivity(Base):
    __tablename__ = "MedicationSensitivity"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.Integer, nullable=False, default=0)
    ConsultationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Consultation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Ended = mapped_column(t.Boolean)
    FormulationSpecific = mapped_column(t.Boolean, nullable=False, default=0)
    MedicationSensitivity_ID = mapped_column(t.Integer, nullable=False, default=0)
    MultilexDrug_ID = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    StartDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")


class MedicationSensitivity_BUILDING(Base):
    __tablename__ = "MedicationSensitivity_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.Integer, nullable=False, default=0)
    ConsultationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Consultation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Ended = mapped_column(t.Boolean)
    FormulationSpecific = mapped_column(t.Boolean, nullable=False, default=0)
    MedicationSensitivity_ID = mapped_column(t.Integer, nullable=False, default=0)
    MultilexDrug_ID = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    StartDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")


class NationalDataOptOut(Base):
    __tablename__ = "NationalDataOptOut"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)


class ONS_Deaths(Base):
    __tablename__ = "ONS_Deaths"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    FIC10MEN1 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10MEN10 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10MEN11 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10MEN12 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10MEN13 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10MEN14 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10MEN15 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10MEN2 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10MEN3 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10MEN4 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10MEN5 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10MEN6 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10MEN7 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10MEN8 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10MEN9 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    FIC10UND = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10001 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10002 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10003 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10004 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10005 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10006 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10007 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10008 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10009 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10010 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10011 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10012 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10013 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10014 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    ICD10015 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Place_of_occurrence = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    ageinyrs = mapped_column(t.Integer)
    dod = mapped_column(t.Date)
    icd10u = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    sex = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))


class OPA(Base):
    __tablename__ = "OPA"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Activity_Location_Type_Code = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Administrative_Category = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Appointment_Date = mapped_column(t.Date)
    Attendance_Status = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Clinic_Code = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Consultation_Medium_Used = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Der_Financial_Year = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Ethnic_Category = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    First_Attendance = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    HRG_Code = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    HRG_Version_No = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Main_Specialty_Code = mapped_column(t.VARCHAR(3, collation="Latin1_General_CI_AS"))
    Medical_Staff_Type_Seeing_Patient = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    MultiProf_Ind_Code = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Referral_Source = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Operation_Status = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Outcome_of_Attendance = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Priority_Type = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Provider_Code = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Provider_Code_Type = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Referral_Request_Received_Date = mapped_column(t.Date)
    Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )


class OPA_ARCHIVED(Base):
    __tablename__ = "OPA_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Activity_Location_Type_Code = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Administrative_Category = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Appointment_Date = mapped_column(t.Date)
    Attendance_Status = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Clinic_Code = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Consultation_Medium_Used = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Der_Financial_Year = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Ethnic_Category = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    First_Attendance = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    HRG_Code = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    HRG_Version_No = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Main_Specialty_Code = mapped_column(t.VARCHAR(3, collation="Latin1_General_CI_AS"))
    Medical_Staff_Type_Seeing_Patient = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    MultiProf_Ind_Code = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Referral_Source = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Operation_Status = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Outcome_of_Attendance = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Priority_Type = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Provider_Code = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Provider_Code_Type = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Referral_Request_Received_Date = mapped_column(t.Date)
    Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )


class OPA_ARCHIVED_Old(Base):
    __tablename__ = "OPA_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Activity_Location_Type_Code = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Administrative_Category = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Appointment_Date = mapped_column(t.Date)
    Attendance_Status = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Clinic_Code = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Consultation_Medium_Used = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Der_Financial_Year = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Ethnic_Category = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    First_Attendance = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    HRG_Code = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    HRG_Version_No = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Main_Specialty_Code = mapped_column(t.VARCHAR(3, collation="Latin1_General_CI_AS"))
    Medical_Staff_Type_Seeing_Patient = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    MultiProf_Ind_Code = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Referral_Source = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Operation_Status = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Outcome_of_Attendance = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Priority_Type = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Provider_Code = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Provider_Code_Type = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Referral_Request_Received_Date = mapped_column(t.Date)
    Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )


class OPA_Cost(Base):
    __tablename__ = "OPA_Cost"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Tariff_OPP = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class OPA_Cost_ARCHIVED(Base):
    __tablename__ = "OPA_Cost_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Tariff_OPP = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class OPA_Cost_ARCHIVED_Old(Base):
    __tablename__ = "OPA_Cost_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Tariff_OPP = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class OPA_Cost_JRC20231009_LastFilesToContainAllHistoricalCostData(Base):
    __tablename__ = "OPA_Cost_JRC20231009_LastFilesToContainAllHistoricalCostData"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Tariff_OPP = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class OPA_Cost_JRC20251022_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = "OPA_Cost_JRC20251022_BeforeOldFinancialYearDataRemoved"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Grand_Total_Payment_MFF = mapped_column(t.REAL)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Tariff_OPP = mapped_column(t.REAL)
    Tariff_Total_Payment = mapped_column(t.REAL)


class OPA_Diag(Base):
    __tablename__ = "OPA_Diag"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Primary_Diagnosis_Code = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Primary_Diagnosis_Code_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Secondary_Diagnosis_Code_1 = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Secondary_Diagnosis_Code_1_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )


class OPA_Diag_ARCHIVED(Base):
    __tablename__ = "OPA_Diag_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Primary_Diagnosis_Code = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Primary_Diagnosis_Code_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Secondary_Diagnosis_Code_1 = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Secondary_Diagnosis_Code_1_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )


class OPA_Diag_ARCHIVED_Old(Base):
    __tablename__ = "OPA_Diag_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Primary_Diagnosis_Code = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Primary_Diagnosis_Code_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Secondary_Diagnosis_Code_1 = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Secondary_Diagnosis_Code_1_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )


class OPA_Diag_JRC20231009_LastFilesToContainAllHistoricalCostData(Base):
    __tablename__ = "OPA_Diag_JRC20231009_LastFilesToContainAllHistoricalCostData"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Primary_Diagnosis_Code = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Primary_Diagnosis_Code_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Secondary_Diagnosis_Code_1 = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Secondary_Diagnosis_Code_1_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )


class OPA_Diag_JRC20251022_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = "OPA_Diag_JRC20251022_BeforeOldFinancialYearDataRemoved"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Primary_Diagnosis_Code = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Primary_Diagnosis_Code_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Secondary_Diagnosis_Code_1 = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Secondary_Diagnosis_Code_1_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )


class OPA_JRC20231009_LastFilesToContainAllHistoricalCostData(Base):
    __tablename__ = "OPA_JRC20231009_LastFilesToContainAllHistoricalCostData"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Activity_Location_Type_Code = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Administrative_Category = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Appointment_Date = mapped_column(t.Date)
    Attendance_Status = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Clinic_Code = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Consultation_Medium_Used = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Der_Financial_Year = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Ethnic_Category = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    First_Attendance = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    HRG_Code = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    HRG_Version_No = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Main_Specialty_Code = mapped_column(t.VARCHAR(3, collation="Latin1_General_CI_AS"))
    Medical_Staff_Type_Seeing_Patient = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    MultiProf_Ind_Code = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Referral_Source = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Operation_Status = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Outcome_of_Attendance = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Priority_Type = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Provider_Code = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Provider_Code_Type = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Referral_Request_Received_Date = mapped_column(t.Date)
    Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )


class OPA_JRC20251022_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = "OPA_JRC20251022_BeforeOldFinancialYearDataRemoved"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Activity_Location_Type_Code = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Administrative_Category = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Appointment_Date = mapped_column(t.Date)
    Attendance_Status = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Clinic_Code = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Consultation_Medium_Used = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Der_Activity_Month = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Der_Financial_Year = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Ethnic_Category = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    First_Attendance = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    HRG_Code = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    HRG_Version_No = mapped_column(t.VARCHAR(10, collation="Latin1_General_CI_AS"))
    Main_Specialty_Code = mapped_column(t.VARCHAR(3, collation="Latin1_General_CI_AS"))
    Medical_Staff_Type_Seeing_Patient = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    MultiProf_Ind_Code = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Referral_Source = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Operation_Status = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Outcome_of_Attendance = mapped_column(
        t.VARCHAR(2, collation="Latin1_General_CI_AS")
    )
    Priority_Type = mapped_column(t.VARCHAR(2, collation="Latin1_General_CI_AS"))
    Provider_Code = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Provider_Code_Type = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Referral_Request_Received_Date = mapped_column(t.Date)
    Treatment_Function_Code = mapped_column(
        t.VARCHAR(3, collation="Latin1_General_CI_AS")
    )


class OPA_Proc(Base):
    __tablename__ = "OPA_Proc"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Primary_Procedure_Code = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Primary_Procedure_Code_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Procedure_Code_2 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Procedure_Code_2_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )


class OPA_Proc_ARCHIVED(Base):
    __tablename__ = "OPA_Proc_ARCHIVED"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Primary_Procedure_Code = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Primary_Procedure_Code_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Procedure_Code_2 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Procedure_Code_2_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )


class OPA_Proc_ARCHIVED_Old(Base):
    __tablename__ = "OPA_Proc_ARCHIVED_Old"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Primary_Procedure_Code = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Primary_Procedure_Code_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Procedure_Code_2 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Procedure_Code_2_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )


class OPA_Proc_JRC20231009_LastFilesToContainAllHistoricalCostData(Base):
    __tablename__ = "OPA_Proc_JRC20231009_LastFilesToContainAllHistoricalCostData"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Primary_Procedure_Code = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Primary_Procedure_Code_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Procedure_Code_2 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Procedure_Code_2_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )


class OPA_Proc_JRC20251022_BeforeOldFinancialYearDataRemoved(Base):
    __tablename__ = "OPA_Proc_JRC20251022_BeforeOldFinancialYearDataRemoved"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    OPA_Ident = mapped_column(t.BIGINT, nullable=False, default=0)
    Primary_Procedure_Code = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    Primary_Procedure_Code_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )
    Procedure_Code_2 = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Procedure_Code_2_Read = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS")
    )


class OpenPROMPT(Base):
    __tablename__ = "OpenPROMPT"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.Integer, nullable=False, default=0)
    CTV3Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_BIN"), nullable=False, default=""
    )
    CodeSystemId = mapped_column(t.Integer, nullable=False, default=0)
    CodedEvent_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ConceptId = mapped_column(t.VARCHAR(50, collation="Latin1_General_BIN"))
    ConsultationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    Consultation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    CreationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    NumericCode = mapped_column(t.Integer, nullable=False, default=0)
    NumericValue = mapped_column(t.REAL, nullable=False, default=0.0)


class Organisation(Base):
    __tablename__ = "Organisation"
    _pk = mapped_column(t.Integer, primary_key=True)

    DirectionsAcknowledged = mapped_column(t.Boolean)
    GoLiveDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    MSOACode = mapped_column(
        t.VARCHAR(150, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    Organisation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Region = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    STPCode = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class Organisation_BUILDING(Base):
    __tablename__ = "Organisation_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    GoLiveDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    MSOACode = mapped_column(
        t.VARCHAR(150, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    Organisation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Region = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    STPCode = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class Patient(Base):
    __tablename__ = "Patient"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    DateOfBirth = mapped_column(t.Date)
    DateOfDeath = mapped_column(t.Date)
    Sex = mapped_column(
        t.CHAR(1, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class PatientAddress(Base):
    __tablename__ = "PatientAddress"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AddressType = mapped_column(t.Integer, nullable=False, default=0)
    EndDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    ImdRankRounded = mapped_column(t.Integer, nullable=False, default=0)
    MSOACode = mapped_column(
        t.VARCHAR(150, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    PatientAddress_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    RuralUrbanClassificationCode = mapped_column(t.Integer, nullable=False, default=0)
    StartDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")


class PatientAddress_BUILDING(Base):
    __tablename__ = "PatientAddress_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AddressType = mapped_column(t.Integer, nullable=False, default=0)
    EndDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    ImdRankRounded = mapped_column(t.Integer, nullable=False, default=0)
    MSOACode = mapped_column(
        t.VARCHAR(150, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    PatientAddress_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    RuralUrbanClassificationCode = mapped_column(t.Integer, nullable=False, default=0)
    StartDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")


class Patient_BUILDING(Base):
    __tablename__ = "Patient_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    DateOfBirth = mapped_column(t.Date)
    DateOfDeath = mapped_column(t.Date)
    Sex = mapped_column(
        t.CHAR(1, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class PatientsWithTypeOneDissent(Base):
    __tablename__ = "PatientsWithTypeOneDissent"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)


class PotentialCareHomeAddress(Base):
    __tablename__ = "PotentialCareHomeAddress"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    LocationDoesNotRequireNursing = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    LocationRequiresNursing = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    PatientAddress_ID = mapped_column(t.BIGINT, nullable=False, default=0)


class PotentialCareHomeAddress_BUILDING(Base):
    __tablename__ = "PotentialCareHomeAddress_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    LocationDoesNotRequireNursing = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    LocationRequiresNursing = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    PatientAddress_ID = mapped_column(t.BIGINT, nullable=False, default=0)


class QOFClusterReference(Base):
    __tablename__ = "QOFClusterReference"
    _pk = mapped_column(t.Integer, primary_key=True)

    CTV3Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_BIN"), nullable=False, default=""
    )
    ClusterName = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    ClusterType = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    Description = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class QOFClusterReference_BUILDING(Base):
    __tablename__ = "QOFClusterReference_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    CTV3Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_BIN"), nullable=False, default=""
    )
    ClusterName = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    ClusterType = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    Description = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class RegistrationHistory(Base):
    __tablename__ = "RegistrationHistory"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EndDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    Organisation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Registration_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    StartDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")


class RegistrationHistory_BUILDING(Base):
    __tablename__ = "RegistrationHistory_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    EndDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")
    Organisation_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Registration_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    StartDate = mapped_column(t.DateTime, nullable=False, default="9999-12-31T00:00:00")


class Relationship(Base):
    __tablename__ = "Relationship"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.Integer, nullable=False, default=0)
    EventDate = mapped_column(t.Date)
    Patient_ID_Relationship_With = mapped_column(t.Integer, nullable=False, default=0)
    RelationshipEndDate = mapped_column(t.Date)
    Type_of_Relationship = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class SGSS_AllTests_Negative(Base):
    __tablename__ = "SGSS_AllTests_Negative"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Age_In_Years = mapped_column(t.Integer)
    County_Description = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    Ethnic_Category_Desc = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS")
    )
    LFT_Flag = mapped_column(t.VARCHAR(255, collation="Latin1_General_CI_AS"))
    Lab_Report_Date = mapped_column(t.Date)
    Organism_Species_Name = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    Patient_Sex = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    Pillar = mapped_column(t.VARCHAR(255, collation="Latin1_General_CI_AS"))
    PostCode_Source = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    Specimen_Date = mapped_column(t.Date)
    Symptomatic = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))


class SGSS_AllTests_Positive(Base):
    __tablename__ = "SGSS_AllTests_Positive"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Age_In_Years = mapped_column(t.Integer)
    County_Description = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    Ethnic_Category_Desc = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS")
    )
    LFT_Flag = mapped_column(t.VARCHAR(255, collation="Latin1_General_CI_AS"))
    Lab_Report_Date = mapped_column(t.Date)
    Organism_Species_Name = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    Patient_Sex = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    Pillar = mapped_column(t.VARCHAR(255, collation="Latin1_General_CI_AS"))
    PostCode_Source = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    SGTF = mapped_column(t.VARCHAR(255, collation="Latin1_General_CI_AS"))
    Specimen_Date = mapped_column(t.Date)
    Symptomatic = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    Variant = mapped_column(t.VARCHAR(255, collation="Latin1_General_CI_AS"))
    VariantDetectionMethod = mapped_column(
        t.VARCHAR(255, collation="Latin1_General_CI_AS")
    )


class SGSS_Negative(Base):
    __tablename__ = "SGSS_Negative"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Age_In_Years = mapped_column(t.Integer)
    County_Description = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    Earliest_Specimen_Date = mapped_column(t.Date)
    Lab_Report_Date = mapped_column(t.Date)
    Organism_Species_Name = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    Patient_Sex = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    PostCode_Source = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))


class SGSS_Positive(Base):
    __tablename__ = "SGSS_Positive"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Age_In_Years = mapped_column(t.Integer)
    CaseCategory = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    County_Description = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    Earliest_Specimen_Date = mapped_column(t.Date)
    Lab_Report_Date = mapped_column(t.Date)
    Organism_Species_Name = mapped_column(
        t.VARCHAR(200, collation="Latin1_General_CI_AS")
    )
    Patient_Sex = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    PostCode_Source = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    SGTF = mapped_column(
        t.VARCHAR(10, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )


class Therapeutics(Base):
    __tablename__ = "Therapeutics"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    AgeAtReceivedDate = mapped_column(t.Integer)
    CASIM05_date_of_symptom_onset = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    CASIM05_risk_cohort = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    COVID_indication = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Count = mapped_column(t.Integer)
    CurrentStatus = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Der_LoadDate = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Diagnosis = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    FormName = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Intervention = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    MOL1_high_risk_cohort = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    MOL1_onset_of_symptoms = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Received = mapped_column(t.DateTime)
    Region = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    SOT02_onset_of_symptoms = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    SOT02_risk_cohorts = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    TreatmentStartDate = mapped_column(t.DateTime)


class UKRR(Base):
    __tablename__ = "UKRR"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    creat = mapped_column(t.REAL)
    dataset = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    eGFR_ckdepi = mapped_column(t.REAL)
    mod_prev = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    mod_start = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    renal_centre = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    rrt_start = mapped_column(t.Date)


class UPRN(Base):
    __tablename__ = "UPRN"
    _pk = mapped_column(t.Integer, primary_key=True)

    Care_Home_Flag = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Pseudo_parent_uprn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    Pseudo_uprn = mapped_column(t.VARCHAR(200, collation="Latin1_General_CI_AS"))
    Rural_Urban_Classification = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    ServiceType = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    Total_Pop = mapped_column(t.Integer)
    _0to4 = mapped_column(t.Integer)
    _10to14 = mapped_column(t.Integer)
    _15to19 = mapped_column(t.Integer)
    _20to24 = mapped_column(t.Integer)
    _25to29 = mapped_column(t.Integer)
    _30to34 = mapped_column(t.Integer)
    _40to44 = mapped_column(t.Integer)
    _45to49 = mapped_column(t.Integer)
    _50to54 = mapped_column(t.Integer)
    _55to59 = mapped_column(t.Integer)
    _5to9 = mapped_column(t.Integer)
    _60to64 = mapped_column(t.Integer)
    _65to69 = mapped_column(t.Integer)
    _70to74 = mapped_column(t.Integer)
    _75to79 = mapped_column(t.Integer)
    _80to84 = mapped_column(t.Integer)
    _85Plus = mapped_column(t.Integer)
    class_ = mapped_column("class", t.VARCHAR(100, collation="Latin1_General_CI_AS"))
    private_outdoor_space = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    private_outdoor_space_area = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS")
    )
    property_type = mapped_column(t.VARCHAR(100, collation="Latin1_General_CI_AS"))


class UnitDictionary(Base):
    __tablename__ = "UnitDictionary"
    _pk = mapped_column(t.Integer, primary_key=True)

    CTV3Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_BIN"), nullable=False, default=""
    )
    DecimalPlaces = mapped_column(t.Integer, nullable=False, default=0)
    LowerNormalBound = mapped_column(t.REAL, nullable=False, default=0.0)
    Maximum = mapped_column(t.REAL, nullable=False, default=0.0)
    Minimum = mapped_column(t.REAL, nullable=False, default=0.0)
    UnitDictionary_ID = mapped_column(t.Integer, nullable=False, default=0)
    Units = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    UpperNormalBound = mapped_column(t.REAL, nullable=False, default=0.0)


class UnitDictionary_BUILDING(Base):
    __tablename__ = "UnitDictionary_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    CTV3Code = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_BIN"), nullable=False, default=""
    )
    DecimalPlaces = mapped_column(t.Integer, nullable=False, default=0)
    LowerNormalBound = mapped_column(t.REAL, nullable=False, default=0.0)
    Maximum = mapped_column(t.REAL, nullable=False, default=0.0)
    Minimum = mapped_column(t.REAL, nullable=False, default=0.0)
    UnitDictionary_ID = mapped_column(t.Integer, nullable=False, default=0)
    Units = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    UpperNormalBound = mapped_column(t.REAL, nullable=False, default=0.0)


class Vaccination(Base):
    __tablename__ = "Vaccination"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    VaccinationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    VaccinationName = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    VaccinationName_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    VaccinationSchedulePart = mapped_column(t.Integer, nullable=False, default=0)
    Vaccination_ID = mapped_column(t.BIGINT, nullable=False, default=0)


class VaccinationReference(Base):
    __tablename__ = "VaccinationReference"
    _pk = mapped_column(t.Integer, primary_key=True)

    VaccinationContent = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    VaccinationName = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    VaccinationName_ID = mapped_column(t.Integer, nullable=False, default=0)


class VaccinationReference_BUILDING(Base):
    __tablename__ = "VaccinationReference_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    VaccinationContent = mapped_column(
        t.VARCHAR(50, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    VaccinationName = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    VaccinationName_ID = mapped_column(t.Integer, nullable=False, default=0)


class Vaccination_BUILDING(Base):
    __tablename__ = "Vaccination_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    VaccinationDate = mapped_column(
        t.DateTime, nullable=False, default="9999-12-31T00:00:00"
    )
    VaccinationName = mapped_column(
        t.VARCHAR(100, collation="Latin1_General_CI_AS"), nullable=False, default=""
    )
    VaccinationName_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    VaccinationSchedulePart = mapped_column(t.Integer, nullable=False, default=0)
    Vaccination_ID = mapped_column(t.BIGINT, nullable=False, default=0)


class WL_ClockStops(Base):
    __tablename__ = "WL_ClockStops"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ACTIVITY_TREATMENT_FUNCTION_CODE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    ADMISSION_METHOD_CODE_HOSPITAL_PROVIDER_SPELL = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Cancellation_Date = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Completed_Type = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    DECISION_TO_ADMIT_DATE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Date_Last_Attended = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Date_Of_Last_Priority_Review = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Diagnostic_Priority_Code = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Due_Date = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Inclusion_On_Cancer_Ptl = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Last_Dna_Date = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Local_Outcome_Of_Attendance = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Local_Rtt_Status_Code = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    MAIN_SPECIALTY_CODE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    OPCS_Code = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    OUTCOME_OF_ATTENDANCE_CODE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Outpatient_Appointment_Date = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Outpatient_Future_Appointment_Date = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Outpatient_Priority_Code = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    PRIORITY_TYPE_CODE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    PSEUDO_ORGANISATION_CODE_PATIENT_PATHWAY_IDENTIFIER_ISSUER = mapped_column(
        t.VARBINARY(8000)
    )
    PSEUDO_ORGANISATION_IDENTIFIER_CODE_OF_COMMISSIONER = mapped_column(
        t.VARBINARY(8000)
    )
    PSEUDO_ORGANISATION_IDENTIFIER_CODE_OF_PROVIDER = mapped_column(t.VARBINARY(8000))
    PSEUDO_ORGANISATION_SITE_IDENTIFIER_OF_TREATMENT = mapped_column(t.VARBINARY(8000))
    PSEUDO_PATIENT_PATHWAY_IDENTIFIER = mapped_column(t.VARBINARY(8000))
    Procedure_Priority_Code = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Pseudo_Referral_Identifier = mapped_column(t.VARBINARY(8000))
    REFERRAL_TO_TREATMENT_PERIOD_END_DATE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    REFERRAL_TO_TREATMENT_PERIOD_START_DATE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    REFERRAL_TO_TREATMENT_PERIOD_STATUS = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Referral_Request_Received_Date = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    SOURCE_OF_REFERRAL_FOR_OUTPATIENTS = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Tci_Date = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Waiting_List_Type = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Week_Ending_Date = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))


class WL_Diagnostics(Base):
    __tablename__ = "WL_Diagnostics"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    Diagnostic_Clock_Start_Date = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Diagnostic_Modality = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Diagnostic_Priority_Code = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Inclusion_On_Cancer_Ptl = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    PRIORITY_TYPE_CODE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    PSEUDO_ORGANISATION_CODE_PATIENT_PATHWAY_IDENTIFIER_ISSUER = mapped_column(
        t.VARBINARY(8000)
    )
    PSEUDO_ORGANISATION_IDENTIFIER_CODE_OF_COMMISSIONER = mapped_column(
        t.VARBINARY(8000)
    )
    PSEUDO_ORGANISATION_IDENTIFIER_CODE_OF_PROVIDER = mapped_column(t.VARBINARY(8000))
    PSEUDO_ORGANISATION_SITE_IDENTIFIER_OF_TREATMENT = mapped_column(t.VARBINARY(8000))
    PSEUDO_PATIENT_PATHWAY_IDENTIFIER = mapped_column(t.VARBINARY(8000))
    Planned_Diagnostic_Due_Date = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Proposed_Procedure_Opcs_Code = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Pseudo_Referral_Identifier = mapped_column(t.VARBINARY(8000))
    REFERRAL_TO_TREATMENT_PERIOD_END_DATE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    REFERRAL_TO_TREATMENT_PERIOD_START_DATE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Waiting_List_Type = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Week_Ending_Date = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))


class WL_OpenPathways(Base):
    __tablename__ = "WL_OpenPathways"
    _pk = mapped_column(t.Integer, primary_key=True)

    Patient_ID = mapped_column(t.BIGINT, nullable=False, default=0)
    ACTIVITY_TREATMENT_FUNCTION_CODE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    ADMISSION_METHOD_CODE_HOSPITAL_PROVIDER_SPELL = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Cancellation_Date = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Current_Pathway_Period_Start_Date = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    DECISION_TO_ADMIT_DATE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Date_Last_Attended = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Date_Of_Last_Priority_Review = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Diagnostic_Priority_Code = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Due_Date = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Inclusion_On_Cancer_Ptl = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Last_Dna_Date = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Local_Outcome_Of_Attendance = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Local_Rtt_Status_Code = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    MAIN_SPECIALTY_CODE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    OUTCOME_OF_ATTENDANCE_CODE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Outpatient_Appointment_Date = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Outpatient_Future_Appointment_Date = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Outpatient_Priority_Code = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    PRIORITY_TYPE_CODE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    PSEUDO_ORGANISATION_CODE_PATIENT_PATHWAY_IDENTIFIER_ISSUER = mapped_column(
        t.VARBINARY(8000)
    )
    PSEUDO_ORGANISATION_IDENTIFIER_CODE_OF_COMMISSIONER = mapped_column(
        t.VARBINARY(8000)
    )
    PSEUDO_ORGANISATION_IDENTIFIER_CODE_OF_PROVIDER = mapped_column(t.VARBINARY(8000))
    PSEUDO_ORGANISATION_SITE_IDENTIFIER_OF_TREATMENT = mapped_column(t.VARBINARY(8000))
    PSEUDO_PATIENT_PATHWAY_IDENTIFIER = mapped_column(t.VARBINARY(8000))
    Procedure_Priority_Code = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Proposed_Procedure_Opcs_Code = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Pseudo_Referral_Identifier = mapped_column(t.VARBINARY(8000))
    REFERRAL_REQUEST_RECEIVED_DATE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    REFERRAL_TO_TREATMENT_PERIOD_END_DATE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    REFERRAL_TO_TREATMENT_PERIOD_START_DATE = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    REFERRAL_TO_TREATMENT_PERIOD_STATUS = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    SOURCE_OF_REFERRAL = mapped_column(
        t.VARCHAR(1000, collation="Latin1_General_CI_AS")
    )
    Tci_Date = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Waiting_List_Type = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))
    Week_Ending_Date = mapped_column(t.VARCHAR(1000, collation="Latin1_General_CI_AS"))


class YCodeToSnomedMapping(Base):
    __tablename__ = "YCodeToSnomedMapping"
    _pk = mapped_column(t.Integer, primary_key=True)

    SctConceptId = mapped_column(t.BIGINT)
    YCode = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_BIN"), nullable=False, default=""
    )


class YCodeToSnomedMapping_BUILDING(Base):
    __tablename__ = "YCodeToSnomedMapping_BUILDING"
    _pk = mapped_column(t.Integer, primary_key=True)

    SctConceptId = mapped_column(t.BIGINT)
    YCode = mapped_column(
        t.VARCHAR(5, collation="Latin1_General_BIN"), nullable=False, default=""
    )
