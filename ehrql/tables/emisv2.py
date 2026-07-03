import datetime

from ehrql.codes import DMDCode, SNOMEDCTCode
from ehrql.tables import Constraint, EventFrame, Series, table
from ehrql.tables.core import patients


# Exclude emisv2 tables from docs for now to avoid user confusion
exclude_from_docs = True

__all__ = [
    "addresses",
    "clinical_events",
    "medications",
    "patients",
    "practice_registrations",
]


@table
class addresses(EventFrame):
    """
    Geographic characteristics of the home address a patient registers with a practice.
    Each row in this table is one practice registration period per patient.
    The patient's Middle Layer Super Output Areas (MSOA) from the address is provided,
    from which other larger geographic representations can be derived
    (see various [ONS publications][addresses_ukgeographies] for more detail).

    [addresses_ukgeographies]: https://www.ons.gov.uk/methodology/geography/ukgeographies

    [Example ehrQL usage of addresses](../../how-to/examples.md#addresses)
    """

    class _meta:
        activation_filter_field = False

    start_date = Series(
        datetime.date,
        description="Patient's registration start date.",
    )
    end_date = Series(
        datetime.date,
        description="Patient's registration end date.",
        dummy_data_constraints=[Constraint.DateAfter(["start_date"])],
    )

    imd_rounded = Series(
        int,
        description="""
            [Index of Multiple Deprivation][addresses_imd] (IMD)
            rank of each lower layer super output area (LSOA), rounded to the nearest 100, where
            lower values represent more deprived areas. E.g. 1 is the most deprived LSOA in the country
            and 32,844 is the least deprived (though in this field these are rounded to 0 and 32,800
            respectively)

            [addresses_imd]: https://www.gov.uk/government/statistics/english-indices-of-deprivation-2019
        """,
        constraints=[Constraint.ClosedRange(0, 32_800, 100)],
    )

    msoa_code = Series(
        str,
        description="Middle Layer Super Output Areas (MSOA) code.",
        constraints=[Constraint.Regex("E020[0-9]{5}")],
    )

    def for_patient_on(self, date):
        """
        Return each patient's address information as it was on the supplied registration
        date.
        """
        # Note that the addresses table is an event-level table, but for EmisV2, it is
        # derived from the patient table, so we know that there can only be at most one
        # matching address per patient
        spanning_addrs = self.where(self.start_date <= date).except_where(
            self.end_date < date
        )
        return spanning_addrs.sort_by(self.start_date).last_for_patient()


@table
class clinical_events(EventFrame):
    """
    Each record corresponds to a single clinical or consultation event for a patient.

    Note that event codes do not change in this table. If an event code in the coding
    system becomes inactive, the event will still be coded to the inactive code.
    As such, codelists should include all relevant inactive codes.

    By default, only events with a consultation `date` on or before the date of the patient's
    last de-registration from an activated GP practice (a practice that has acknowledged the
    new non-COVID directions) are included.

    [Example ehrQL usage of clinical_events](../../how-to/examples.md#clinical-events)
    """

    class _meta:
        activation_filter_field = "date"

    date = Series(datetime.date)
    snomedct_code = Series(SNOMEDCTCode)
    numeric_value = Series(float)


@table
class medications(EventFrame):
    """
    The medications table provides data about prescribed medications in primary care.

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

    By default, only medications with a consultation `date` on or before the date of the patient's
    last de-registration from an activated GP practice (a practice that has acknowledged the
    new non-COVID directions) are included.

    ### Factors to consider when using medications data

    Depending on the specific area of research, you may wish to exclude medications
    in particular periods. For example, in order to ensure medication data is stable
    following a change of practice, you may want to exclude patients for a period after
    the start of their practice registration. You may also want to
    exclude medications for patients for a period prior to their leaving a practice.
    Alternatively, for research looking at a specific period of
    interest, you may simply want to ensure that all included patients were registered
    at a single practice for a minimum time prior to the study period, and were
    registered at the same practice for the duration of the study period.

    Examples of using ehrQL to calculation such periods can be found in the documentation
    on how to
    [use ehrQL to answer specific questions using the medications table](../../how-to/examples.md#medications)
    """

    class _meta:
        activation_filter_field = "date"

    date = Series(datetime.date)
    dmd_code = Series(DMDCode)


@table
class practice_registrations(EventFrame):
    """
    Each record corresponds to a patient's registration with a practice.
    """

    start_date = Series(
        datetime.date,
        constraints=[Constraint.NotNull()],
        description="Date patient joined practice.",
    )
    end_date = Series(
        datetime.date,
        description="Date patient left practice.",
        dummy_data_constraints=[Constraint.Categorical([None])],
    )

    def for_patient_on(self, date):
        """
        Return each patient's practice registration as it was on the supplied date.
        """
        # Note that practice_registrations is an event-level table, but for EMISv2, it is
        # derived from the patient table, so we know that there can only be at most one
        # matching registration per patient
        return self.spanning(date, date).sort_by(self.start_date).last_for_patient()

    def exists_for_patient_on(self, date):
        """
        Returns whether a person was registered with a practice on the supplied date.

        NB. The implementation currently uses `spanning()`. It would also have been
        valid to implement as
        `practice_registrations.for_patient_on(date).exists_for_patient()`, but for
        internal reasons that is less efficient.

        """
        return self.spanning(date, date).exists_for_patient()

    def spanning(self, start_date, end_date):
        """
        Filter registrations to just those spanning the entire period between
        `start_date` and `end_date`.
        """
        return self.where(
            self.start_date.is_on_or_before(start_date)
            & (self.end_date.is_on_or_after(end_date) | self.end_date.is_null())
        )
