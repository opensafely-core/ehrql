import datetime

from ehrql.tables import Constraint, EventFrame, Series, table
from ehrql.tables.core import clinical_events, medications, patients


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
            self.end_date.is_not_null() & (self.end_date < date)
        )
        return spanning_addrs.sort_by(self.start_date).last_for_patient()


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
