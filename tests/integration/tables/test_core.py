from datetime import date

from ehrql import Dataset
from ehrql.tables import core


def test_patients_age_on(in_memory_engine):
    in_memory_engine.populate(
        {
            core.patients: [
                dict(patient_id=1, date_of_birth=date(1980, 1, 1)),
                dict(patient_id=2, date_of_birth=date(1800, 1, 1)),
                dict(patient_id=3, date_of_birth=date(2010, 1, 1)),
                dict(patient_id=4, date_of_birth=date(2010, 1, 2)),
            ]
        }
    )

    dataset = Dataset()
    dataset.define_population(core.patients.exists_for_patient())
    dataset.age_2010 = core.patients.age_on("2010-01-01")
    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "age_2010": 30},
        {"patient_id": 2, "age_2010": 210},
        {"patient_id": 3, "age_2010": 0},
        {"patient_id": 4, "age_2010": -1},
    ]


def test_practice_registrations_for_patient_on(in_memory_engine):
    in_memory_engine.populate(
        # Simple case: successive registrations
        {
            core.practice_registrations: [
                dict(
                    patient_id=1,
                    practice_pseudo_id=123,
                    start_date=date(2000, 1, 1),
                    end_date=date(2005, 1, 1),
                ),
                dict(
                    patient_id=1,
                    practice_pseudo_id=456,
                    start_date=date(2005, 1, 1),
                    end_date=date(2015, 1, 1),
                ),
                dict(
                    patient_id=1,
                    practice_pseudo_id=789,
                    start_date=date(2015, 1, 1),
                    end_date=date(2020, 1, 1),
                ),
            ]
        },
        # Registration with NULL end date
        {
            core.practice_registrations: [
                dict(
                    patient_id=2,
                    practice_pseudo_id=123,
                    start_date=date(2000, 1, 1),
                    end_date=None,
                ),
            ]
        },
        # Overlapping: choose most recent
        {
            core.practice_registrations: [
                dict(
                    patient_id=3,
                    practice_pseudo_id=456,
                    start_date=date(2000, 1, 1),
                    end_date=date(2015, 1, 1),
                ),
                dict(
                    patient_id=3,
                    practice_pseudo_id=789,
                    start_date=date(2005, 1, 1),
                    end_date=date(2015, 1, 1),
                ),
            ]
        },
        # Overlapping: choose longest
        {
            core.practice_registrations: [
                dict(
                    patient_id=4,
                    practice_pseudo_id=123,
                    start_date=date(2000, 1, 1),
                    end_date=date(2012, 1, 1),
                ),
                dict(
                    patient_id=4,
                    practice_pseudo_id=456,
                    start_date=date(2000, 1, 1),
                    end_date=date(2015, 1, 1),
                ),
            ]
        },
        # Tie-break: choose largest pseudo ID
        {
            core.practice_registrations: [
                dict(
                    patient_id=5,
                    practice_pseudo_id=789,
                    start_date=date(2000, 1, 1),
                    end_date=date(2015, 1, 1),
                ),
                dict(
                    patient_id=5,
                    practice_pseudo_id=456,
                    start_date=date(2000, 1, 1),
                    end_date=date(2015, 1, 1),
                ),
            ]
        },
    )

    reg = core.practice_registrations.for_patient_on("2010-01-01")

    dataset = Dataset()
    dataset.define_population(core.practice_registrations.exists_for_patient())
    dataset.practice_pseudo_id = reg.practice_pseudo_id
    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "practice_pseudo_id": 456},
        {"patient_id": 2, "practice_pseudo_id": 123},
        {"patient_id": 3, "practice_pseudo_id": 789},
        {"patient_id": 4, "practice_pseudo_id": 456},
        {"patient_id": 5, "practice_pseudo_id": 789},
    ]


def test_practice_registrations_spanning(
    in_memory_engine,
):
    in_memory_engine.populate(
        # Successive registrations continuous in time period
        {
            core.practice_registrations: [
                dict(
                    patient_id=1,
                    practice_pseudo_id=123,
                    start_date=date(2000, 1, 1),
                    end_date=date(2005, 1, 1),
                ),
                dict(
                    patient_id=1,
                    practice_pseudo_id=456,
                    start_date=date(2005, 1, 1),
                    end_date=date(2015, 1, 1),
                ),
                dict(
                    patient_id=1,
                    practice_pseudo_id=789,
                    start_date=date(2015, 1, 1),
                    end_date=date(2020, 1, 1),
                ),
            ]
        },
        # Registration with NULL end date
        {
            core.practice_registrations: [
                dict(
                    patient_id=2,
                    practice_pseudo_id=123,
                    start_date=date(2000, 1, 1),
                    end_date=None,
                ),
            ]
        },
        # Registration with end date after time period ends
        {
            core.practice_registrations: [
                dict(
                    patient_id=3,
                    practice_pseudo_id=123,
                    start_date=date(2000, 1, 1),
                    end_date=date(2020, 1, 1),
                ),
            ]
        },
        # Registration with start date after time period starts
        {
            core.practice_registrations: [
                dict(
                    patient_id=4,
                    practice_pseudo_id=123,
                    start_date=date(2010, 2, 1),
                    end_date=date(2020, 1, 1),
                ),
            ]
        },
        # Registration with start date and end date inside time period
        {
            core.practice_registrations: [
                dict(
                    patient_id=5,
                    practice_pseudo_id=123,
                    start_date=date(2010, 2, 1),
                    end_date=date(2010, 12, 1),
                ),
            ]
        },
        # Discontinuous registration in time period
        {
            core.practice_registrations: [
                dict(
                    patient_id=6,
                    practice_pseudo_id=123,
                    start_date=date(2000, 1, 1),
                    end_date=date(2010, 6, 1),
                ),
                dict(
                    patient_id=6,
                    practice_pseudo_id=123,
                    start_date=date(2010, 7, 1),
                    end_date=date(2020, 1, 1),
                ),
            ]
        },
    )

    dataset = Dataset()
    dataset.define_population(core.practice_registrations.exists_for_patient())
    dataset.has_spanning_practice_registration = (
        core.practice_registrations.spanning("2010-01-01", "2011-01-01")
    ).exists_for_patient()
    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "has_spanning_practice_registration": True},
        {"patient_id": 2, "has_spanning_practice_registration": True},
        {"patient_id": 3, "has_spanning_practice_registration": True},
        {"patient_id": 4, "has_spanning_practice_registration": False},
        {"patient_id": 5, "has_spanning_practice_registration": False},
        {"patient_id": 6, "has_spanning_practice_registration": False},
    ]
