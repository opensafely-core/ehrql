"""
This schema defines the core tables and columns which should be available in any backend
providing primary care data, allowing dataset definitions written using this schema to
run across multiple backends.

The data provided by this schema are minimally transformed. They are very close to the
data provided by the underlying database tables. They are provided for data development
and data curation purposes.
"""

import datetime

from ehrql.codes import DMDCode, ICD10Code
from ehrql.tables import EventFrame, Series, table


__all__ = [
    "medications",
    "ons_deaths",
]


class ons_deaths_raw(EventFrame):
    """
    Registered deaths

    Date and cause of death based on information recorded when deaths are
    certified and registered in England and Wales from February 2019 onwards.
    The data provider is the Office for National Statistics (ONS).

    This table includes the underlying cause of death and up to 15 medical conditions mentioned on the death certificate.
    These codes (`cause_of_death_01` to `cause_of_death_15`) are not ordered meaningfully.

    More information about this table can be found in following documents provided by the ONS:

    - [Information collected at death registration](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/methodologies/userguidetomortalitystatisticsjuly2017#information-collected-at-death-registration)
    - [User guide to mortality statistics](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/methodologies/userguidetomortalitystatisticsjuly2017)
    - [How death registrations are recorded and stored by ONS](https://www.ons.gov.uk/aboutus/transparencyandgovernance/freedomofinformationfoi/howdeathregistrationsarerecordedandstoredbyons)

    In the associated database table a small number of patients have multiple registered deaths.
    This table contains all registered deaths.
    The `ehrql.tables.core.ons_deaths` table contains the earliest registered death.

    !!! tip
        To return one row per patient from `ehrql.tables.raw.core.ons_deaths`,
        for example the latest registered death, you can use:

        ```py
        ons_deaths.sort_by(ons_deaths.date).last_for_patient()
        ```
    """

    date = Series(
        datetime.date,
        description=("Patient's date of death."),
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


class medications_raw(EventFrame):
    """
    The raw medication table provides data about prescribed medications in primary care together with the medication status.

    Prescribing data, including the contents of the medications table are standardised
    across clinical information systems such as SystmOne (TPP). This is a requirement
    for data transfer through the
    [Electronic Prescription Service](https://digital.nhs.uk/services/electronic-prescription-service/)
    in which data passes from the prescriber to the pharmacy for dispensing.

    Medications are coded using
    [dm+d codes](https://www.bennett.ox.ac.uk/blog/2019/08/what-is-the-dm-d-the-nhs-dictionary-of-medicines-and-devices/).
    The medications table is structured similarly to the [clinical_events](#clinical_events)
    table, and each row in the table is made up of a patient identifier, an event (dm+d)
    code, and an event date. For this table, the event refers to the issue of a medication
    (coded as a dm+d code), and the event date, the date the prescription was issued.

    ### Factors to consider when using medications data

    Depending on the specific area of research, you may wish to exclude medications
    in particular periods. For example, in order to ensure medication data is stable
    following a change of practice, you may want to exclude patients for a period after
    the start of their practice registration . You may also want to
    exclude medications for patients for a period prior to their leaving a practice.
    Alternatively, for research looking at a specific period of
    interest, you may simply want to ensure that all included patients were registered
    at a single practice for a minimum time prior to the study period, and were
    registered at the same practice for the duration of the study period.

    Examples of using ehrQL to calculation such periods can be found in the documentation
    on how to
    [use ehrQL to answer specific questions](../../how-to/examples.md#excluding-medications-for-patients-who-have-transferred-between-practices).
    """

    date = Series(datetime.date)
    dmd_code = Series(DMDCode)
    medication_status = Series(
        int,
        description="""
            Medication status. The values might map to the descriptions below from the data dictionary.
            Note that this still needs to be confirmed.

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
    )


medications = table(medications_raw)
