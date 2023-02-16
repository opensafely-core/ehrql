from datetime import date

from databuilder.ehrql import Dataset
from databuilder.tables.beta import tpp


def test_practice_registrations_for_patient_on(in_memory_engine):
    in_memory_engine.populate(
        # Simple case: successive registrations
        {
            tpp.practice_registrations: [
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
            tpp.practice_registrations: [
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
            tpp.practice_registrations: [
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
            tpp.practice_registrations: [
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
            tpp.practice_registrations: [
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

    reg = tpp.practice_registrations.for_patient_on("2010-01-01")

    dataset = Dataset()
    dataset.set_population(tpp.practice_registrations.exists_for_patient())
    dataset.practice_pseudo_id = reg.practice_pseudo_id
    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "practice_pseudo_id": 456},
        {"patient_id": 2, "practice_pseudo_id": 123},
        {"patient_id": 3, "practice_pseudo_id": 789},
        {"patient_id": 4, "practice_pseudo_id": 456},
        {"patient_id": 5, "practice_pseudo_id": 789},
    ]
