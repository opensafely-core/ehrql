from datetime import date

from ehrql import Dataset
from ehrql.tables import emis


def test_patients_age_on(in_memory_engine):
    in_memory_engine.populate(
        {
            emis.patients: [
                dict(patient_id=1, date_of_birth=date(1980, 1, 1)),
                dict(patient_id=2, date_of_birth=date(1800, 1, 1)),
                dict(patient_id=3, date_of_birth=date(2010, 1, 1)),
                dict(patient_id=4, date_of_birth=date(2010, 1, 2)),
            ]
        }
    )

    dataset = Dataset()
    dataset.define_population(emis.patients.exists_for_patient())
    dataset.age_2010 = emis.patients.age_on("2010-01-01")
    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "age_2010": 30},
        {"patient_id": 2, "age_2010": 210},
        {"patient_id": 3, "age_2010": 0},
        {"patient_id": 4, "age_2010": -1},
    ]


def test_practice_registrations_spanning(
    in_memory_engine,
):
    in_memory_engine.populate(
        # Registrations before time period
        {
            emis.patients: [
                dict(
                    patient_id="1",
                    registration_start_date=date(2000, 1, 1),
                    registration_end_date=date(2005, 1, 1),
                ),
            ]
        },
        # Registration from before time period, and with NULL end date
        {
            emis.patients: [
                dict(
                    patient_id="2",
                    registration_start_date=date(2000, 1, 1),
                    registration_end_date=None,
                ),
            ]
        },
        # Registration with end date after time period ends
        {
            emis.patients: [
                dict(
                    patient_id="3",
                    registration_start_date=date(2000, 1, 1),
                    registration_end_date=date(2020, 1, 1),
                ),
            ]
        },
        # Registration with start date after time period starts
        {
            emis.patients: [
                dict(
                    patient_id="4",
                    registration_start_date=date(2010, 2, 1),
                    registration_end_date=date(2020, 1, 1),
                ),
            ]
        },
        # Registration with start date and end date inside time period
        {
            emis.patients: [
                dict(
                    patient_id="5",
                    registration_start_date=date(2010, 2, 1),
                    registration_end_date=date(2010, 12, 1),
                ),
            ]
        },
    )

    dataset = Dataset()
    dataset.define_population(
        emis.patients.has_practice_registration_spanning("2010-01-01", "2011-01-01")
    )
    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": "2"},
        {"patient_id": "3"},
    ]
