"""
This defines all the data (both primary care and externally linked) available in the
OpenSAFELY-TPP backend. For more information about this backend, see the
[*SystmOne Primary Care*](https://docs.opensafely.org/data-sources/systmone/) section.
"""
import datetime

from ehrql import case, when
from ehrql.codes import CTV3Code, ICD10Code, OPCS4Code, SNOMEDCTCode
from ehrql.tables import Constraint, EventFrame, PatientFrame, Series, table
from ehrql.tables.beta.core import medications, ons_deaths, patients


__all__ = [
    "addresses",
    "apcs",
    "apcs_cost",
    "appointments",
    "clinical_events",
    "ec",
    "ec_cost",
    "emergency_care_attendances",
    "hospital_admissions",
    "household_memberships_2020",
    "isaric_raw",
    "medications",
    "occupation_on_covid_vaccine_record",
    "ons_deaths",
    "opa",
    "opa_cost",
    "opa_diag",
    "opa_proc",
    "open_prompt",
    "patients",
    "practice_registrations",
    "sgss_covid_all_tests",
    "vaccinations",
    "wl_clockstops",
    "wl_clockstops_raw",
]


@table
class addresses(EventFrame):
    address_id = Series(int)
    start_date = Series(datetime.date)
    end_date = Series(datetime.date)
    address_type = Series(int)
    rural_urban_classification = Series(int)
    imd_rounded = Series(int, constraints=[Constraint.ClosedRange(0, 32_800, 100)])
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
class apcs(EventFrame):
    apcs_ident = Series(
        int,
        constraints=[Constraint.NotNull()],
        description="TODO",
    )
    admission_date = Series(
        datetime.date,
        description="TODO",
    )
    discharge_date = Series(
        datetime.date,
        description="TODO",
    )
    spell_core_hrg_sus = Series(
        str,
        description="TODO",
    )


@table
class apcs_cost(EventFrame):
    apcs_ident = Series(
        int,
        constraints=[Constraint.NotNull()],
        description="TODO",
    )
    grand_total_payment_mff = Series(
        float,
        description="TODO",
    )
    tariff_initial_amount = Series(
        float,
        description="TODO",
    )
    tariff_total_payment = Series(
        float,
        description="TODO",
    )
    admission_date = Series(
        datetime.date,
        description="TODO",
    )
    discharge_date = Series(
        datetime.date,
        description="TODO",
    )


@table
class appointments(EventFrame):
    """
    Appointments in primary care.

    You can find out more about this table in the [short data report][appointments_1].
    To view it, you will need a login for OpenSAFELY Jobs and the Project Collaborator
    or Project Developer role for the [project][appointments_4]. The
    [workspace][appointments_2] shows when the code that comprises the report was run;
    the code itself is in the [appointments-short-data-report][appointments_3]
    repository on GitHub.

    !!! tip
        Querying this table is similar to using Cohort Extractor's
        `patients.with_gp_consultations` function. However, that function filters by
        the status of the appointment. To achieve a similar result with this table:

        ```py
        appointments.where(
            appointments.status.is_in([
                "Arrived",
                "In Progress",
                "Finished",
                "Visit",
                "Waiting",
                "Patient Walked Out",
            ])
        )
        ```

    [appointments_1]: https://jobs.opensafely.org/curation-of-gp-appointments-data-short-data-report/appointments-short-data-report/outputs/latest/tpp/output/reports/report.html
    [appointments_2]: https://jobs.opensafely.org/curation-of-gp-appointments-data-short-data-report/appointments-short-data-report/
    [appointments_3]: https://github.com/opensafely/appointments-short-data-report
    [appointments_4]: https://jobs.opensafely.org/curation-of-gp-appointments-data-short-data-report/
    """

    booked_date = Series(
        datetime.date,
        description="The date the appointment was booked",
    )
    start_date = Series(
        datetime.date,
        description="The date the appointment was due to start",
    )
    status = Series(
        str,
        description="The status of the appointment",
        constraints=[
            Constraint.Categorical(
                [
                    "Booked",
                    "Arrived",
                    "Did Not Attend",
                    "In Progress",
                    "Finished",
                    "Requested",
                    "Blocked",
                    "Visit",
                    "Waiting",
                    "Cancelled by Patient",
                    "Cancelled by Unit",
                    "Cancelled by Other Service",
                    "No Access Visit",
                    "Cancelled Due To Death",
                    "Patient Walked Out",
                ]
            )
        ],
    )


@table
class clinical_events(EventFrame):
    """
    Each record corresponds to a single clinical or consultation event for a patient.

    Each event is recorded twice: once with a CTv3 code, and again with the equivalent
    SNOMED-CT code. Each record will have only one of the ctv3_code or snomedct_code
    columns set and the other will be null. This allows you to query the table using
    either a CTv3 codelist or SNOMED-CT codelist and all records using the other coding
    system will be effectively ignored.

    Note that event codes do not change in this table. If an event code in the coding
    system becomes inactive, the event will still be coded to the inactive code.
    As such, codelists should include all relevant inactive codes.

    Detailed information on onward referrals is not currently available. A subset of
    referrals are recorded in the clinical events table but this data will be incomplete.
    """

    date = Series(datetime.date)
    snomedct_code = Series(SNOMEDCTCode)
    ctv3_code = Series(CTV3Code)
    numeric_value = Series(float)


@table
class ec(EventFrame):
    ec_ident = Series(
        int,
        constraints=[Constraint.NotNull()],
        description="TODO",
    )
    arrival_date = Series(
        datetime.date,
        description="TODO",
    )
    sus_hrg_code = Series(
        str,
        description="TODO",
    )


@table
class ec_cost(EventFrame):
    ec_ident = Series(
        int,
        constraints=[Constraint.NotNull()],
        description="TODO",
    )
    grand_total_payment_mff = Series(
        float,
        description="TODO",
    )
    tariff_total_payment = Series(
        float,
        description="TODO",
    )
    arrival_date = Series(
        datetime.date,
        description="TODO",
    )
    ec_decision_to_admit_date = Series(
        datetime.date,
        description="TODO",
    )
    ec_injury_date = Series(
        datetime.date,
        description="TODO",
    )


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
class household_memberships_2020(PatientFrame):
    """
    Inferred household membership as of 2020-02-01, as determined by TPP using an as yet
    undocumented algorithm.
    """

    household_pseudo_id = Series(int)
    household_size = Series(int)


@table
class isaric_raw(EventFrame):
    """
    A subset of the ISARIC data.

    These columns are deliberately all taken as strings while in a preliminary phase.
    They will later change to more appropriate data types.

    Descriptions taken from: [CCP_REDCap_ISARIC_data_dictionary_codebook.pdf][isaric_ddc_pdf]

    [isaric_ddc_pdf]: https://github.com/isaric4c/wiki/blob/d6b87d59a277cf2f6deedeb5e8c1a970dbb970a3/ISARIC/CCP_REDCap_ISARIC_data_dictionary_codebook.pdf
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


@table
class occupation_on_covid_vaccine_record(EventFrame):
    is_healthcare_worker = Series(bool)


@table
class opa(EventFrame):
    opa_ident = Series(
        int,
        constraints=[Constraint.NotNull()],
        description="TODO",
    )
    appointment_date = Series(
        datetime.date,
        description="TODO",
    )
    attendance_status = Series(
        str,
        description="TODO",
    )
    consultation_medium_used = Series(
        str,
        description="TODO",
    )
    first_attendance = Series(
        str,
        description="TODO",
    )
    hrg_code = Series(
        str,
        description="TODO",
    )
    treatment_function_code = Series(
        str,
        description="TODO",
    )


@table
class opa_cost(EventFrame):
    opa_ident = Series(
        int,
        constraints=[Constraint.NotNull()],
        description="TODO",
    )
    tariff_opp = Series(
        float,
        description="TODO",
    )
    grand_total_payment_mff = Series(
        float,
        description="TODO",
    )
    tariff_total_payment = Series(
        float,
        description="TODO",
    )
    appointment_date = Series(
        datetime.date,
        description="TODO",
    )
    referral_request_received_date = Series(
        datetime.date,
        description="TODO",
    )


@table
class opa_diag(EventFrame):
    opa_ident = Series(
        int,
        constraints=[Constraint.NotNull()],
        description="TODO",
    )
    primary_diagnosis_code = Series(
        ICD10Code,
        description="TODO",
    )
    primary_diagnosis_code_read = Series(
        CTV3Code,
        description="TODO",
    )
    secondary_diagnosis_code_1 = Series(
        ICD10Code,
        description="TODO",
    )
    secondary_diagnosis_code_1_read = Series(
        CTV3Code,
        description="TODO",
    )
    appointment_date = Series(
        datetime.date,
        description="TODO",
    )
    referral_request_received_date = Series(
        datetime.date,
        description="TODO",
    )


@table
class opa_proc(EventFrame):
    opa_ident = Series(
        int,
        constraints=[Constraint.NotNull()],
        description="TODO",
    )
    primary_procedure_code = Series(
        OPCS4Code,
        description="TODO",
    )
    primary_procedure_code_read = Series(
        CTV3Code,
        description="TODO",
    )
    procedure_code_1 = Series(
        OPCS4Code,
        description="TODO",
    )
    procedure_code_2_read = Series(
        CTV3Code,
        description="TODO",
    )
    appointment_date = Series(
        datetime.date,
        description="TODO",
    )
    referral_request_received_date = Series(
        datetime.date,
        description="TODO",
    )


@table
class open_prompt(EventFrame):
    """
    This table contains responses to questions from the OpenPROMPT project.

    You can find out more about this table in the associated short data report. To view
    it, you will need a login for [Level 4][open_prompt_1]. The
    [workspace][open_prompt_2] shows when the code that comprises the report was run;
    the code itself is in the [airmid-short-data-report][open_prompt_3] repository on
    GitHub.

    [open_prompt_1]: https://docs.opensafely.org/security-levels/#level-4-nhs-england-are-data-controllers-of-the-data
    [open_prompt_2]: https://jobs.opensafely.org/datalab/opensafely-internal/airmid-short-data-report/
    [open_prompt_3]: https://github.com/opensafely/airmid-short-data-report
    """

    ctv3_code = Series(
        CTV3Code,
        constraints=[Constraint.NotNull()],
        description=(
            "The response to the question, as a CTV3 code. "
            "Alternatively, if the question does not admit a CTV3 code as the response, "
            "then the question, as a CTV3 code."
        ),
    )
    snomedct_code = Series(
        SNOMEDCTCode,
        description=(
            "The response to the question, as a SNOMED CT code. "
            "Alternatively, if the question does not admit a SNOMED CT code as the response, "
            "then the question, as a SNOMED CT code."
        ),
    )
    creation_date = Series(
        datetime.date,
        constraints=[Constraint.NotNull()],
        description="The date the survey was administered",
    )
    consultation_date = Series(
        datetime.date,
        constraints=[Constraint.NotNull()],
        description=(
            "The response to the question, as a date, "
            "if the question admits a date as the response. "
            "Alternatively, the date the survey was administered."
        ),
    )
    consultation_id = Series(
        int,
        constraints=[Constraint.NotNull()],
        description="The ID of the survey",
    )
    numeric_value = Series(
        float,
        description="The response to the question, as a number",
    )


@table
class practice_registrations(EventFrame):
    """
    Each record corresponds to a patient's registration with a practice.

    Only patients with a full GMS (General Medical Services) registration are included.

    We have registration history for:

    * all patients currently registered at a TPP practice
    * all patients registered at a TPP practice any time from 1 Jan 2009 onwards:
        * who have since de-registered
        * who have since died

    A patient can be registered with zero, one, or more than one practices at a given
    time. For instance, students are often registered with a practice at home and a
    practice at university.
    """

    start_date = Series(
        datetime.date,
        constraints=[Constraint.NotNull()],
        description="Date patient joined practice.",
    )
    end_date = Series(
        datetime.date,
        description="Date patient left practice.",
    )
    practice_pseudo_id = Series(
        int,
        constraints=[Constraint.NotNull()],
        description="Pseudonymised practice identifier.",
    )
    practice_stp = Series(
        str,
        constraints=[Constraint.Regex("E540000[0-9]{2}")],
        description="""
            ONS code of practice's STP (Sustainability and Transformation Partnership).
            STPs have been replaced by ICBs (Integrated Care Boards), and ICB codes will be available soon.
        """,
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
        description="""
            Name of the NUTS level 1 region of England to which the practice belongs.
            For more information see:
            <https://www.ons.gov.uk/methodology/geography/ukgeographies/eurostat>
        """,
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
class sgss_covid_all_tests(EventFrame):
    specimen_taken_date = Series(datetime.date)
    is_positive = Series(bool)


@table
class vaccinations(EventFrame):
    vaccination_id = Series(int)
    date = Series(datetime.date)
    target_disease = Series(str)
    product_name = Series(str)


@table
class wl_clockstops_raw(EventFrame):
    """
    National Waiting List Clock Stops

    The columns in this table have the same data types as the columns in [the associated
    database table][wl_clockstops_raw_1]. The three "pseudo" columns are small
    exceptions, as they are converted from binary columns to string columns.

    [wl_clockstops_raw_1]: https://reports.opensafely.org/reports/opensafely-tpp-database-schema/#WL_ClockStops
    """

    activity_treatment_function_code = Series(str)
    priority_type_code = Series(str)
    pseudo_organisation_code_patient_pathway_identifier_issuer = Series(str)
    pseudo_patient_pathway_identifier = Series(str)
    pseudo_referral_identifier = Series(str)
    referral_request_received_date = Series(str)
    referral_to_treatment_period_end_date = Series(str)
    referral_to_treatment_period_start_date = Series(str)
    source_of_referral_for_outpatients = Series(str)
    waiting_list_type = Series(str)
    week_ending_date = Series(str)


@table
class wl_clockstops(EventFrame):
    """
    National Waiting List Clock Stops

    This dataset contains all completed referral-to-treatment (RTT) pathways with a "clock stop" date between May 2021 and May 2022.
    Patients referred for non-emergency consultant-led treatment are on RTT pathways.
    The "clock start" date is the date of the first referral that starts the pathway.
    The "clock stop" date is when the patient either: receives treatment;
    declines treatment;
    enters a period of active monitoring;
    no longer requires treatment;
    or dies.
    The time spent waiting is the difference in these two dates.

    A patient may have multiple rows if they have multiple completed RTT pathways;
    however, there is only one row per unique pathway.
    Because referral identifiers aren't necessarily unique between hospitals,
    unique RTT pathways can be identified using a combination of:

    * `pseudo_organisation_code_patient_pathway_identifier_issuer`
    * `pseudo_patient_pathway_identifier`
    * `pseudo_referral_identifier`
    * `referral_to_treatment_period_start_date`

    For more information, see
    "[Consultant-led Referral to Treatment Waiting Times Rules and Guidance][wl_clockstops_1]".

    [wl_clockstops_1]: https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/rtt-guidance/
    """

    activity_treatment_function_code = Series(
        str,
        description="The treatment function",
        constraints=[Constraint.Regex(r"[a-zA-Z0-9]{3}")],
    )
    priority_type_code = Series(
        str,
        description="The priority type",
        constraints=[Constraint.Categorical(["routine", "urgent", "two week wait"])],
    )
    pseudo_organisation_code_patient_pathway_identifier_issuer = Series(str)
    pseudo_patient_pathway_identifier = Series(str)
    pseudo_referral_identifier = Series(str)
    referral_request_received_date = Series(
        datetime.date,
        description=(
            "The date the referral was received, "
            "for the referral that started the original pathway"
        ),
    )
    referral_to_treatment_period_end_date = Series(
        datetime.date,
        description="Clock stop for the completed pathway",
    )
    referral_to_treatment_period_start_date = Series(
        datetime.date,
        description="Clock start for the completed pathway",
    )
    source_of_referral_for_outpatients = Series(str)
    waiting_list_type = Series(
        str,
        description="The waiting list type on completion of the pathway",
        constraints=[Constraint.Categorical(["ORTT", "IRTT"])],
    )
    week_ending_date = Series(
        datetime.date,
        description="The Sunday of the week that the pathway relates to",
    )
