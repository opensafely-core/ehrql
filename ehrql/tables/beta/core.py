"""
This schema defines the core tables and columns which should be available in any backend
providing primary care data, allowing dataset definitions written using this schema to
run across multiple backends.

!!! warning
    This schema is still a work-in-progress while the EMIS backend remains under
    development. Projects requiring EMIS data should continue to use the [Cohort
    Extractor](https://docs.opensafely.org/study-def/) tool.
"""
import datetime

from ehrql.codes import DMDCode, ICD10Code, SNOMEDCTCode
from ehrql.tables import Constraint, EventFrame, PatientFrame, Series, table


__all__ = [
    "clinical_events",
    "medications",
    "ons_deaths",
    "patients",
]


@table
class patients(PatientFrame):
    """
    Patients in primary care.

    ### Representativeness

    You can find out more about the representativeness of these data in the
    OpenSAFELY-TPP backend in:

    > The OpenSAFELY Collaborative, Colm D. Andrews, Anna Schultze, Helen J. Curtis, William J. Hulme, John Tazare, Stephen J. W. Evans, _et al._ 2022.
    > "OpenSAFELY: Representativeness of Electronic Health Record Platform OpenSAFELY-TPP Data Compared to the Population of England."
    > Wellcome Open Res 2022, 7:191.
    > <https://doi.org/10.12688/wellcomeopenres.18010.1>


    ### Orphan records

    If a practice becomes aware that a patient has moved house,
    then the practice _deducts_, or removes, the patient's records from their register.
    If the patient doesn't register with a new practice within a given amount of time
    (normally from four to eight weeks),
    then the patient's records are permanently deducted and are _orphan records_.
    There are roughly 1.6 million orphan records.
    """

    date_of_birth = Series(
        datetime.date,
        description="Patient's date of birth.",
        constraints=[Constraint.FirstOfMonth(), Constraint.NotNull()],
    )
    sex = Series(
        str,
        description="Patient's sex.",
        implementation_notes_to_add_to_description=(
            'Specify how this has been determined, e.g. "sex at birth", or "current sex".'
        ),
        constraints=[
            Constraint.Categorical(["female", "male", "intersex", "unknown"]),
            Constraint.NotNull(),
        ],
    )
    date_of_death = Series(
        datetime.date,
        description="Patient's date of death.",
    )

    def age_on(self, date):
        """
        Patient's age as an integer, in whole elapsed calendar years, as it would be on
        the given date.

        This method takes no account of whether the patient is alive on the given date.
        In particular, it may return negative values if the given date is before the
        patient's date of birth.
        """
        return (date - self.date_of_birth).years


@table
class ons_deaths(PatientFrame):
    """
    Registered deaths

    Date and cause of death based on information recorded when deaths are
    certified and registered in England and Wales from February 2019 onwards.
    The data provider is the Office for National Statistics (ONS).
    This table is updated approximately weekly in OpenSAFELY.

    This table includes the underlying cause of death and up to 15 medical conditions mentioned on the death certificate.
    These codes (`cause_of_death_01` to `cause_of_death_15`) are not ordered meaningfully.

    More information about this table can be found in following documents provided by the ONS:

    - [Information collected at death registration](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/methodologies/userguidetomortalitystatisticsjuly2017#information-collected-at-death-registration)
    - [User guide to mortality statistics](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/methodologies/userguidetomortalitystatisticsjuly2017)
    - [How death registrations are recorded and stored by ONS](https://www.ons.gov.uk/aboutus/transparencyandgovernance/freedomofinformationfoi/howdeathregistrationsarerecordedandstoredbyons)

    In the associated database table [ONS_Deaths](https://reports.opensafely.org/reports/opensafely-tpp-database-schema/#ONS_Deaths),
    a small number of patients have multiple registered deaths.
    This table contains the earliest registered death.
    The `ehrql.tables.beta.raw.ons_deaths` table contains all registered deaths.
    """

    date = Series(
        datetime.date,
        description=("Patient's date of death."),
    )
    place = Series(
        str,
        description="Patient's date of death.",
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
    underlying_cause_of_death = Series(
        ICD10Code,
        description="Patient's underlying cause of death of death.",
    )
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


@table
class clinical_events(EventFrame):
    """
    Each record corresponds to a single clinical or consultation event for a patient.

    Note that event codes do not change in this table. If an event code in the coding
    system becomes inactive, the event will still be coded to the inactive code.
    As such, codelists should include all relevant inactive codes.

    """

    date = Series(datetime.date)
    snomedct_code = Series(SNOMEDCTCode)
    numeric_value = Series(float)


@table
class medications(EventFrame):
    date = Series(datetime.date)
    dmd_code = Series(DMDCode)
