import datetime

from ehrql import case, when
from ehrql.codes import CTV3Code, DMDCode, ICD10Code, SNOMEDCTCode
from ehrql.tables import Constraint, EventFrame, PatientFrame, Series, table


__all__ = [
    "patients",
    "vaccinations",
    "practice_registrations",
    "ons_deaths",
    "clinical_events",
    "medications",
    "addresses",
    "sgss_covid_all_tests",
    "occupation_on_covid_vaccine_record",
    "emergency_care_attendances",
    "hospital_admissions",
    "appointments",
    "ons_cis",
    "isaric_raw",
]


@table
class patients(PatientFrame):
    date_of_birth = Series(
        datetime.date,
        description="Patient's date of birth, rounded to first of month",
        constraints=[Constraint.FirstOfMonth(), Constraint.NotNull()],
    )
    sex = Series(
        str,
        description="Patient's sex",
        implementation_notes_to_add_to_description=(
            'Specify how this has been determined, e.g. "sex at birth", or "current sex".'
        ),
        constraints=[
            Constraint.NotNull(),
            Constraint.Categorical(["female", "male", "intersex", "unknown"]),
        ],
    )
    date_of_death = Series(
        datetime.date,
        description="Patient's date of death",
    )

    def age_on(self, date):
        """
        Patient's age as an integer, in whole elapsed calendar years, as it would be on
        the supplied date.

        Note that this takes no account of whether the patient is alive at the given
        date. In particular, it may return negative values if the date is before the
        patient's date of birth.
        """
        return (date - self.date_of_birth).years


@table
class vaccinations(EventFrame):
    vaccination_id = Series(int)
    date = Series(datetime.date)
    target_disease = Series(str)
    product_name = Series(str)


@table
class practice_registrations(EventFrame):
    start_date = Series(datetime.date)
    end_date = Series(datetime.date)
    practice_pseudo_id = Series(int)
    practice_stp = Series(
        str,
        constraints=[Constraint.Regex("E540000[0-9]{2}")],
    )
    practice_nuts1_region_name = Series(
        str,
        constraints=[
            Constraint.Categorical(
                [
                    "North East",
                    "North West",
                    "Yorkshire and The Humber",
                    "East Midlands",
                    "West Midlands",
                    "East",
                    "London",
                    "South East",
                    "South West",
                ]
            ),
        ],
        description=(
            "Name of the NUTS level 1 region of England to which the practice belongs.\n"
            "For more information see:\n"
            "https://www.ons.gov.uk/methodology/geography/ukgeographies/eurostat"
        ),
    )

    def for_patient_on(self, date):
        """
        Return each patient's practice registration as it was on the supplied date.

        Where a patient is registered with multiple practices we prefer the most recent
        registration and then, if there are multiple of these, the one with the longest
        duration. If there's stil an exact tie we choose arbitrarily based on the
        practice ID.
        """
        spanning_regs = self.where(self.start_date <= date).except_where(
            self.end_date < date
        )
        ordered_regs = spanning_regs.sort_by(
            self.start_date,
            self.end_date,
            self.practice_pseudo_id,
        )
        return ordered_regs.last_for_patient()


@table
class ons_deaths(EventFrame):
    date = Series(datetime.date)
    place = Series(
        str,
        constraints=[
            Constraint.Categorical(
                [
                    "Care Home",
                    "Elsewhere",
                    "Home",
                    "Hospice",
                    "Hospital",
                    "Other communal establishment",
                ]
            ),
        ],
    )
    # TODO: Revisit this when we have support for multi-valued fields
    cause_of_death_01 = Series(ICD10Code)
    cause_of_death_02 = Series(ICD10Code)
    cause_of_death_03 = Series(ICD10Code)
    cause_of_death_04 = Series(ICD10Code)
    cause_of_death_05 = Series(ICD10Code)
    cause_of_death_06 = Series(ICD10Code)
    cause_of_death_07 = Series(ICD10Code)
    cause_of_death_08 = Series(ICD10Code)
    cause_of_death_09 = Series(ICD10Code)
    cause_of_death_10 = Series(ICD10Code)
    cause_of_death_11 = Series(ICD10Code)
    cause_of_death_12 = Series(ICD10Code)
    cause_of_death_13 = Series(ICD10Code)
    cause_of_death_14 = Series(ICD10Code)
    cause_of_death_15 = Series(ICD10Code)


@table
class clinical_events(EventFrame):
    date = Series(datetime.date)
    snomedct_code = Series(SNOMEDCTCode)
    ctv3_code = Series(CTV3Code)
    numeric_value = Series(float)


@table
class medications(EventFrame):
    date = Series(datetime.date)
    dmd_code = Series(DMDCode)
    multilex_code = Series(str)


@table
class addresses(EventFrame):
    address_id = Series(int)
    start_date = Series(datetime.date)
    end_date = Series(datetime.date)
    address_type = Series(int)
    rural_urban_classification = Series(int)
    imd_rounded = Series(int)
    msoa_code = Series(
        str,
        constraints=[Constraint.Regex("E020[0-9]{5}")],
    )
    has_postcode = Series(bool)
    # Is the address potentially a match for a care home? (Using TPP's algorithm)
    care_home_is_potential_match = Series(bool)
    # These two fields look like they should be a single boolean, but this is how
    # they're represented in the data
    care_home_requires_nursing = Series(bool)
    care_home_does_not_require_nursing = Series(bool)

    def for_patient_on(self, date):
        """
        Return each patient's registered address as it was on the supplied date.

        Where there are multiple registered addresses we prefer any which have a known
        postcode (though we never have access to this postcode) as this is used by TPP
        to cross-reference other data associated with the address, such as the MSOA or
        index of multiple deprevation.

        Where there are multiple of these we prefer the most recently registered address
        and then, if there are multiple of these, the one with the longest duration. If
        there's stil an exact tie we choose arbitrarily based on the address ID.
        """
        spanning_addrs = self.where(self.start_date <= date).except_where(
            self.end_date < date
        )
        ordered_addrs = spanning_addrs.sort_by(
            case(when(self.has_postcode).then(1), default=0),
            self.start_date,
            self.end_date,
            self.address_id,
        )
        return ordered_addrs.last_for_patient()


@table
class sgss_covid_all_tests(EventFrame):
    specimen_taken_date = Series(datetime.date)
    is_positive = Series(bool)


@table
class occupation_on_covid_vaccine_record(EventFrame):
    is_healthcare_worker = Series(bool)


@table
class emergency_care_attendances(EventFrame):
    id = Series(int)  # noqa: A003
    arrival_date = Series(datetime.date)
    discharge_destination = Series(SNOMEDCTCode)
    # TODO: Revisit this when we have support for multi-valued fields
    diagnosis_01 = Series(SNOMEDCTCode)
    diagnosis_02 = Series(SNOMEDCTCode)
    diagnosis_03 = Series(SNOMEDCTCode)
    diagnosis_04 = Series(SNOMEDCTCode)
    diagnosis_05 = Series(SNOMEDCTCode)
    diagnosis_06 = Series(SNOMEDCTCode)
    diagnosis_07 = Series(SNOMEDCTCode)
    diagnosis_08 = Series(SNOMEDCTCode)
    diagnosis_09 = Series(SNOMEDCTCode)
    diagnosis_10 = Series(SNOMEDCTCode)
    diagnosis_11 = Series(SNOMEDCTCode)
    diagnosis_12 = Series(SNOMEDCTCode)
    diagnosis_13 = Series(SNOMEDCTCode)
    diagnosis_14 = Series(SNOMEDCTCode)
    diagnosis_15 = Series(SNOMEDCTCode)
    diagnosis_16 = Series(SNOMEDCTCode)
    diagnosis_17 = Series(SNOMEDCTCode)
    diagnosis_18 = Series(SNOMEDCTCode)
    diagnosis_19 = Series(SNOMEDCTCode)
    diagnosis_20 = Series(SNOMEDCTCode)
    diagnosis_21 = Series(SNOMEDCTCode)
    diagnosis_22 = Series(SNOMEDCTCode)
    diagnosis_23 = Series(SNOMEDCTCode)
    diagnosis_24 = Series(SNOMEDCTCode)


@table
class hospital_admissions(EventFrame):
    id = Series(int)  # noqa: A003
    admission_date = Series(datetime.date)
    discharge_date = Series(datetime.date)
    admission_method = Series(str)
    # TODO: Revisit this when we have support for multi-valued fields
    all_diagnoses = Series(str)
    patient_classification = Series(str)
    days_in_critical_care = Series(int)
    primary_diagnoses = Series(str)


@table
class appointments(EventFrame):
    booked_date = Series(datetime.date)
    start_date = Series(datetime.date)


@table
class household_memberships_2020(PatientFrame):
    """
    Inferred household membership as of 2020-02-01, as determined by TPP using an as yet
    undocumented algorithm
    """

    household_pseudo_id = Series(int)
    household_size = Series(int)


@table
class ons_cis(EventFrame):
    """
    ONS Covid Infection Survery
    """

    visit_date = Series(datetime.date)
    visit_num = Series(int)
    is_opted_out_of_nhs_data_share = Series(bool)
    last_linkage_dt = Series(datetime.date)
    imd_decile_e = Series(int)
    imd_quartile_e = Series(int)
    rural_urban = Series(int)


@table
class isaric_raw(EventFrame):
    """
    A subset of the ISARIC data.

    These columns are deliberately all taken as strings while in a preliminary phase.
    They will later change to more appropriate data types.

    Descriptions taken from:
    https://github.com/isaric4c/wiki/blob/d6b87d59a277cf2f6deedeb5e8c1a970dbb970a3/ISARIC/CCP_REDCap_ISARIC_data_dictionary_codebook.pdf
    """

    # Demographics
    age = Series(
        str,
        description="Age",
    )
    age_factor = Series(
        str,
        description="TODO",
    )
    calc_age = Series(
        str,
        description="Calculated age (comparing date of birth with date of enrolment). May be inaccurate if a date of February 29 is used.",
    )
    sex = Series(
        str,
        description="Sex at birth.",
    )
    ethnic___1 = Series(
        str,
        description="Ethnic group: Arab.",
    )
    ethnic___2 = Series(
        str,
        description="Ethnic group: Black.",
    )
    ethnic___3 = Series(
        str,
        description="Ethnic group: East Asian.",
    )
    ethnic___4 = Series(
        str,
        description="Ethnic group: South Asian.",
    )
    ethnic___5 = Series(
        str,
        description="Ethnic group: West Asian.",
    )
    ethnic___6 = Series(
        str,
        description="Ethnic group: Latin American.",
    )
    ethnic___7 = Series(
        str,
        description="Ethnic group: White.",
    )
    ethnic___8 = Series(
        str,
        description="Ethnic group: Aboriginal/First Nations.",
    )
    ethnic___9 = Series(
        str,
        description="Ethnic group: Other.",
    )
    ethnic___10 = Series(
        str,
        description="Ethnic group: N/A.",
    )

    # Vaccination
    covid19_vaccine = Series(
        str,
        description="Has the patient received a Covid-19 vaccine (open label licenced product)?",
    )
    covid19_vaccined = Series(
        datetime.date,
        description="Date first vaccine given (Covid-19) if known.",
    )
    covid19_vaccine2d = Series(
        datetime.date,
        description="Date second vaccine given (Covid-19) if known.",
    )
    covid19_vaccined_nk = Series(
        str,
        description="First vaccine given (Covid-19) but date not known.",
    )

    # Clinical
    corona_ieorres = Series(
        str,
        description="Suspected or proven infection with pathogen of public health interest.",
    )
    # Note the coriona spelling here (compared with corona_ieorres).
    # The difference exists both in the TPP ISARIC_New database table,
    # and the ISARIC data dictionary.
    coriona_ieorres2 = Series(
        str,
        description="Proven or high likelihood of infection with pathogen of public health interest.",
    )
    coriona_ieorres3 = Series(
        str,
        description="Proven infection with pathogen of public health interest.",
    )
    inflammatory_mss = Series(
        str,
        description="Adult or child who meets case definition for inflammatory multi-system syndrome (MIS-C/MIS-A).",
    )
    cestdat = Series(
        datetime.date,
        description="Onset date of first/earliest symptom.",
    )

    # Clinical characteristics
    chrincard = Series(
        str,
        description="Chronic cardiac disease, including congenital heart disease (not hypertension).",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    hypertension_mhyn = Series(
        str,
        description="Hypertension (physician diagnosed).",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    chronicpul_mhyn = Series(
        str,
        description="Chronic pulmonary disease (not asthma).",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    asthma_mhyn = Series(
        str,
        description="Asthma (physician diagnosed).",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    renal_mhyn = Series(
        str,
        description="Chronic kidney disease.",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    mildliver = Series(
        str,
        description="Mild liver disease.",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    modliv = Series(
        str,
        description="Moderate or severe liver disease",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    chronicneu_mhyn = Series(
        str,
        description="Chronic neurological disorder.",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    malignantneo_mhyn = Series(
        str,
        description="Malignant neoplasm.",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    chronichaemo_mhyn = Series(
        str,
        description="Chronic haematologic disease.",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    aidshiv_mhyn = Series(
        str,
        description="AIDS/HIV.",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    obesity_mhyn = Series(
        str,
        description="Obesity (as defined by clinical staff).",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    diabetes_type_mhyn = Series(
        str,
        description="Diabetes and type.",
        constraints=[Constraint.Categorical(["NO", "1", "2", "N/K"])],
    )
    diabetescom_mhyn = Series(
        str,
        description="Diabetes with complications.",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    diabetes_mhyn = Series(
        str,
        description="Diabetes without complications.",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    rheumatologic_mhyn = Series(
        str,
        description="Rheumatologic disorder.",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    dementia_mhyn = Series(
        str,
        description="Dementia.",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    malnutrition_mhyn = Series(
        str,
        description="Malnutrition.",
        constraints=[Constraint.Categorical(["YES", "NO", "Unknown"])],
    )
    smoking_mhyn = Series(
        str,
        description="Smoking.",
        constraints=[
            Constraint.Categorical(["Yes", "Never Smoked", "Former Smoker", "N/K"])
        ],
    )

    # Admission
    hostdat = Series(
        datetime.date,
        description="Admission date at this facility.",
    )
    hooccur = Series(
        str,
        description="Transfer from other facility?",
    )
    hostdat_transfer = Series(
        datetime.date,
        description="Admission date at previous facility.",
    )
    hostdat_transfernk = Series(
        str,
        description="Admission date at previous facility not known.",
    )
    readm_cov19 = Series(
        str,
        description="Is the patient being readmitted with Covid-19?",
    )
    dsstdat = Series(
        datetime.date,
        description="Date of enrolment.",
    )
    dsstdtc = Series(
        datetime.date,
        description="Outcome date.",
    )
