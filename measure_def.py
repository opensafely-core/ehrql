from databuilder.measures import GroupedSum, period
from databuilder.tables.beta import tpp as tables

"""
from cohortextractor import StudyDefinition, Measure, patients

study = StudyDefinition(
    # Configure the expectations framework
    default_expectations={
        "date": {"earliest": "2020-01-01", "latest": "today"},
        "rate": "exponential_increase",
        "incidence": 0.2,
    },

    index_date="2020-01-01",

    population=patients.registered_as_of("index_date"),

    stp=patients.registered_practice_as_of(
        "index_date",
        returning="stp_code",
        return_expectations={
            "category": {"ratios": {"stp1": 0.1, "stp2": 0.2, "stp3": 0.7}},
            "incidence": 1,
        },
    ),

    sex=patients.sex(
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"M": 0.49, "F": 0.51}},
        }
    ),

    admitted=patients.admitted_to_hospital(
        returning="binary_flag",
        between=["index_date", "last_day_of_month(index_date)"],
        return_expectations={"incidence": 0.1},
    ),

    died=patients.died_from_any_cause(
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.05},
    ),
)

measures = [
    Measure(
        id="hosp_admission_by_stp",
        numerator="admitted",
        denominator="population",
        group_by="stp",
    ),
    Measure(
        id="death_by_stp",
        numerator="died",
        denominator="population",
        group_by="stp",
        small_number_suppression=True,
    ),
]
"""


def registrations_overlapping_period(start_date, end_date):
    regs = tables.practice_registrations
    return regs.take(
        regs.start_date.is_on_or_before(start_date)
        & (regs.end_date.is_after(end_date) | regs.end_date.is_null())
    )


def practice_registration_as_of(date):
    regs = registrations_overlapping_period(date, date)
    return regs.sort_by(regs.start_date, regs.end_date).first_for_patient()




practice = practice_registration_as_of(period.start)
was_registered = practice.exists_for_patient()

admissions = tables.hospital_admissions
was_admitted = admissions.take(
    (admissions.admission_date >= period.start)
    & (admissions.admission_date <= period.end)
).exists_for_patient()


deaths = tables.ons_deaths
has_died = deaths.take(
    (deaths.date >= period.start) & (deaths.date <= period.end)
).exists_for_patient()

"""
measures = dict(
    hosp_admission_by_stp=Measure(
        numerator=was_admitted,
        denominator=was_registered,
        group_by=[period, practice.stp],
    ),
    death_by_stp=Measure(
        numerator=has_died,
        denominator=was_registered,
        group_by=[period, practice.stp],
    ),
)
"""

GroupedSum(
    population=was_registered,
    values=dict(
        has_died=has_died,
        was_admitted=was_admitted,
    ),
    group_by=dict(
        stp=practice.stp,
        date=period.start,
    ),
    date_start="2020-01-01",
    date_end="2020-12-01",
    frequency="month",
)
