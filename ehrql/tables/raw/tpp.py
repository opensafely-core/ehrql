"""
This schema defines the data (both primary care and externally linked) available in the
OpenSAFELY-TPP backend. For more information about this backend, see
"[SystmOne Primary Care](https://docs.opensafely.org/data-sources/systmone/)".

The data provided by this schema are minimally transformed. They are very close to the
data provided by the underlying database tables. They are provided for data development
and data curation purposes.
"""

import datetime

from ehrql.codes import DMDCode, ICD10Code
from ehrql.tables import Constraint, EventFrame, Series, table


__all__ = [
    "apcs_cost_historical",
    "apcs_historical",
    "covid_therapeutics_raw",
    "isaric",
    "medications",
    "ons_deaths",
    "wl_clockstops",
    "wl_openpathways",
]


class isaric_raw(EventFrame):
    """
    ISARIC is a dataset of COVID-19-related hospital admissions,
    with coverage across the majority of hospitals across the UK,
    including much richer clinical information
    than collected in national Hospital Episode Statistics datasets.

    The data in this table covers a subset of the ISARIC data columns available in TPP,
    sourced from the [ISARIC COVID-19 Clinical Database][isaric_clinical_database].

    All columns included have deliberately been taken as strings while in a preliminary phase.

    Descriptions taken from [CCP_REDCap_ISARIC_data_dictionary_codebook.pdf][isaric_ddc_pdf]
    which also has information on the data expected for each column.

    !!! warning
        ISARIC data can only be used in collaboration with ISARIC researchers
        who must be involved in working on the study and writing it up.

    Refer to the [OpenSAFELY database build report][opensafely_database_build_report]
    to see when this data was last updated.

    [isaric_ddc_pdf]: https://github.com/isaric4c/wiki/blob/d6b87d59a277cf2f6deedeb5e8c1a970dbb970a3/ISARIC/CCP_REDCap_ISARIC_data_dictionary_codebook.pdf
    [isaric_clinical_database]: https://isaric.org/research/covid-19-clinical-research-resources/covid-19-data-management-hosting/
    [opensafely_database_build_report]: https://reports.opensafely.org/reports/opensafely-tpp-database-builds/
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


isaric = table(isaric_raw)


class medications_raw(EventFrame):
    """
    This table is an extension of the [`tpp.medications`](../schemas/tpp.md#medications) table.

    It contains additional fields whose contents are not yet well understood, with the
    aim of facilitating exploratory analysis for data development and data curation
    purposes.
    """

    date = Series(datetime.date)
    dmd_code = Series(DMDCode)
    consultation_id = Series(
        int, description="ID of the consultation associated with this event"
    )
    medication_status = Series(
        int,
        description="""
            Medication status. The values might map to the descriptions below from the
            data dictionary.  Note that this still needs to be confirmed.

            * 0 - Normal
            * 4 - Historical
            * 5 - Blue script
            * 6 - Private
            * 7 - Not in possession
            * 8 - Repeat dispensed
            * 9 - In possession
            * 10 - Dental
            * 11 - Hospital
            * 12 - Problem substance
            * 13 - From patient group direction
            * 14 - To take out
            * 15 - On admission
            * 16 - Regular medication
            * 17 - As required medication
            * 18 - Variable dose medication
            * 19 - Rate-controlled single regular
            * 20 - Only once
            * 21 - Outpatient
            * 22 - Rate-controlled multiple regular
            * 23 - Rate-controlled multiple only once
            * 24 - Rate-controlled single only once
            * 25 - Placeholder
            * 26 - Unconfirmed
            * 27 - Infusion
            * 28 - Reducing dose blue script
        """,
        constraints=[
            Constraint.ClosedRange(0, 28),
        ],
    )


medications = table(medications_raw)


class ons_deaths_raw(EventFrame):
    """
    Registered deaths

    Date and cause of death based on information recorded when deaths are
    certified and registered in England and Wales from February 2019 onwards.
    The data provider is the Office for National Statistics (ONS).
    This table is updated approximately weekly in OpenSAFELY.

    This table includes the underlying cause of death, place of death, and up to
    15 medical conditions mentioned on the death certificate.
    These codes (`cause_of_death_01` to `cause_of_death_15`) are not ordered meaningfully.

    More information about this table can be found in following documents provided by the ONS:

    - [Information collected at death registration](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/methodologies/userguidetomortalitystatisticsjuly2017#information-collected-at-death-registration)
    - [User guide to mortality statistics](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/methodologies/userguidetomortalitystatisticsjuly2017)
    - [How death registrations are recorded and stored by ONS](https://www.ons.gov.uk/aboutus/transparencyandgovernance/freedomofinformationfoi/howdeathregistrationsarerecordedandstoredbyons)

    In the associated database table [ONS_Deaths](https://reports.opensafely.org/reports/opensafely-tpp-database-schema/#ONS_Deaths),
    a small number of patients have multiple registered deaths.
    This table contains all registered deaths.
    The `ehrql.tables.ons_deaths` table contains the earliest registered death.

    !!! tip
        To return one row per patient from `ehrql.tables.raw.tpp.ons_deaths`,
        for example the latest registered death, you can use:

        ```py
        ons_deaths.sort_by(ons_deaths.date).last_for_patient()
        ```
    """

    date = Series(
        datetime.date,
        description=("Patient's date of death."),
    )
    place = Series(
        str,
        description="Patient's place of death.",
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
    underlying_cause_of_death = Series(ICD10Code)
    # TODO: Revisit this when we have support for multi-valued fields
    cause_of_death_01 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )
    cause_of_death_02 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )
    cause_of_death_03 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )
    cause_of_death_04 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )
    cause_of_death_05 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )
    cause_of_death_06 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )
    cause_of_death_07 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )
    cause_of_death_08 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )
    cause_of_death_09 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )
    cause_of_death_10 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )
    cause_of_death_11 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )
    cause_of_death_12 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )
    cause_of_death_13 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )
    cause_of_death_14 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )
    cause_of_death_15 = Series(
        ICD10Code,
        description="Medical condition mentioned on the death certificate.",
    )


ons_deaths = table(ons_deaths_raw)


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


wl_clockstops = table(wl_clockstops_raw)


class wl_openpathways_raw(EventFrame):
    """
    National Waiting List Open Pathways

    The columns in this table have the same data types as the columns in [the associated
    database table][wl_openpathways_raw_1]. The three "pseudo" columns are small
    exceptions, as they are converted from binary columns to string columns.

    [wl_openpathways_raw_1]: https://reports.opensafely.org/reports/opensafely-tpp-database-schema/#WL_OpenPathways
    """

    activity_treatment_function_code = Series(str)
    current_pathway_period_start_date = Series(str)
    priority_type_code = Series(str)
    pseudo_organisation_code_patient_pathway_identifier_issuer = Series(str)
    pseudo_patient_pathway_identifier = Series(str)
    pseudo_referral_identifier = Series(str)
    referral_request_received_date = Series(str)
    referral_to_treatment_period_end_date = Series(str)
    referral_to_treatment_period_start_date = Series(str)
    source_of_referral = Series(str)
    waiting_list_type = Series(str)
    week_ending_date = Series(str)


wl_openpathways = table(wl_openpathways_raw)


@table
class apcs_historical(EventFrame):
    """
    This table contains some historical APCS data.

    It has been exposed to users for data exploration, and may be removed in future.
    """

    apcs_ident = Series(
        int,
        constraints=[Constraint.NotNull()],
    )
    admission_date = Series(
        datetime.date,
    )
    discharge_date = Series(
        datetime.date,
    )
    spell_core_hrg_sus = Series(
        str,
    )


@table
class apcs_cost_historical(EventFrame):
    """
    This table contains some historical APCS cost data.

    It has been exposed to users for data exploration, and may be removed in future.
    """

    apcs_ident = Series(
        int,
        constraints=[Constraint.NotNull()],
    )
    grand_total_payment_mff = Series(
        float,
    )
    tariff_initial_amount = Series(
        float,
    )
    tariff_total_payment = Series(
        float,
    )
    admission_date = Series(
        datetime.date,
    )
    discharge_date = Series(
        datetime.date,
    )


@table
class covid_therapeutics_raw(EventFrame):
    """
    The COVID Therapeutics dataset contains information on COVID treatments used in inpatient
    and outpatient settings.

    **Metadata**

    * **Data provider** NHS England
    * **Participation / Coverage** Inpatients and outpatients treated with antivirals/nMABs for COVID-19 in England
    * **Provenance** Data sourced largely from BlueTeq system (forms completed by clinicians)
    * **Update frequency in OpenSAFELY** Approximately weekly
    * **Delay between event occurring and event appearing in OpenSAFELY** Approximately 2-9 days
    * **Collected information** Treatment start date; therapeutic intervention; COVID indication, current status, risk group, region


    **Overview**

    Antivirals and neutralising monoclonal antibodies (nMABs) for COVID-19 can be
    administered in inpatient setting or, for outpatients, in COVID Medicine Delivery
    Units (CMDUs) specifically set up for this purpose. For patients considered for
    these treatments, clinicians submit completed forms to NHS England. Each row
    represents one completed form for one course of treatment. Data received by
    OpenSAFELY currently covers patients who were approved for treatment. The patient
    may or may not have actually received the treatment or completed the course (but we
    assume that they usually do). They may have another form completed for another
    treatment, either because it was decided to give them a different treatment, or for
    some other reason. They may in theory also have another form completed some months
    later for another instance of infection.

    Treatment dates may be in the past or future at the point when the form is
    submitted.

    Note that this dataset contains some **duplicate** rows – some full duplicates and
    some partial duplicates.


    **More Information**

    * [Treatment guidelines](https://www.nice.org.uk/guidance/ta878)
    * [Draft Data Report](https://docs.google.com/document/d/15o4x9sqHEO-sLm2dTqgm3PyAh72cdgOOmZC4AB3BTNk/) (currently only available to internal staff)
    """

    current_status = Series(
        str,
        description="Status of form/application.",
        constraints=[
            Constraint.Categorical(
                [
                    "Approved",
                    "Treatment Complete",
                    "Treatment Not Started",
                    "Treatment Stopped",
                ]
            )
        ],
    )
    covid_indication = Series(
        str,
        description="Treatment setting/indication.",
        constraints=[
            Constraint.Categorical(
                ["non_hospitalised", "hospitalised_with", "hospital_onset"]
            )
        ],
    )
    diagnosis = Series(
        str,
        description="Always has the value 'Covid-19'.",
    )
    intervention = Series(
        str,
        description="""
            Intervention or therapeutic name. Expected to be one of:

             * Baricitinib
             * Casirivimab and imdevimab
             * Molnupiravir
             * Paxlovid
             * Remdesivir
             * sarilumab (sic)
             * Sotrovimab
             * Tocilizumab

        """,
    )
    treatment_start_date = Series(
        datetime.date,
        description="""
            Entered by the clinician and can represent either a future planned start
            date or a past date at the time of form submission.
        """,
    )
    CASIM05_risk_cohort = Series(
        str,
        description="""
            High-risk group to which the patient was considered to belong. Derived from
            tick-boxes. Multiple groups can be selected and will be joined with the word
            ` and ` e.g. `liver disease and rare neurological conditions`.

            The available groups as at the time of writing are listed below. However
            note that the precise wording used has changed over time and so filtering by
            a specific disease name may not be reliable.

             * `Downs syndrome`
             * `HIV or AIDS`
             * `IMID`
             * `haematologic malignancy`
             * `Patients with a haematological diseases` (sic)
             * `immune deficiencies`
             * `liver disease`
             * `primary immune deficiencies`
             * `rare neurological conditions`
             * `rare neurological diseases`
             * `renal disease`
             * `sickle cell disease`
             * `solid cancer`
             * `solid organ recipients`
             * `stem cell transplant recipients`
        """,
    )
    MOL1_high_risk_cohort = Series(
        str,
        description="""
            High-risk group to which the patient was considered to belong. Derived from
            tick-boxes. Multiple groups can be selected and will be joined with the word
            ` and ` e.g. `liver disease and rare neurological conditions`.

            The available groups as at the time of writing are listed below. However
            note that the precise wording used has changed over time and so filtering by
            a specific disease name may not be reliable.

             * `Downs syndrome`
             * `HIV or AIDS`
             * `IMID`
             * `haematologic malignancy`
             * `Patients with a haematological diseases` (sic)
             * `immune deficiencies`
             * `liver disease`
             * `primary immune deficiencies`
             * `rare neurological conditions`
             * `rare neurological diseases`
             * `renal disease`
             * `sickle cell disease`
             * `solid cancer`
             * `solid organ recipients`
             * `stem cell transplant recipients`
        """,
    )
    SOT02_risk_cohorts = Series(
        str,
        description="""
            High-risk group to which the patient was considered to belong. Derived from
            tick-boxes. Multiple groups can be selected and will be joined with the word
            ` and ` e.g. `liver disease and rare neurological conditions`.

            The available groups as at the time of writing are listed below. However
            note that the precise wording used has changed over time and so filtering by
            a specific disease name may not be reliable.

             * `Downs syndrome`
             * `HIV or AIDS`
             * `IMID`
             * `haematologic malignancy`
             * `Patients with a haematological diseases` (sic)
             * `immune deficiencies`
             * `liver disease`
             * `primary immune deficiencies`
             * `rare neurological conditions`
             * `rare neurological diseases`
             * `renal disease`
             * `sickle cell disease`
             * `solid cancer`
             * `solid organ recipients`
             * `stem cell transplant recipients`
        """,
    )
    form_name = Series(
        str,
        description="""
            Name and version of the patient registration form used to register the
            treatment.
        """,
    )
    received = Series(
        datetime.date,
        description="Date form submitted.",
    )
    count = Series(
        int,
        description="Number of forms.",
    )
    age_at_received_date = Series(
        int,
        description="""
            Can occasionally be zero, presumably indicating an unknown or missing value
            as minimum eligibility age is 12.
        """,
    )
    region = Series(
        str,
        description="""
            NHS England region in which the CMDU submitting the form is located.
        """,
    )
    load_date = Series(
        datetime.date,
        description="Date on which the current dataset was imported.",
    )
