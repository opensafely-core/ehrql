from datetime import date

from databuilder.ehrql import Dataset
from databuilder.tables.beta import tpp


def tests_patients_age_on(in_memory_engine):
    in_memory_engine.populate(
        {
            tpp.patients: [
                dict(patient_id=1, date_of_birth=date(1980, 1, 1)),
                dict(patient_id=2, date_of_birth=date(1800, 1, 1)),
                dict(patient_id=3, date_of_birth=date(2010, 1, 1)),
                dict(patient_id=4, date_of_birth=date(2010, 1, 2)),
            ]
        }
    )

    dataset = Dataset()
    dataset.define_population(tpp.patients.exists_for_patient())
    dataset.age_2010 = tpp.patients.age_on("2010-01-01")
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
    dataset.define_population(tpp.practice_registrations.exists_for_patient())
    dataset.practice_pseudo_id = reg.practice_pseudo_id
    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "practice_pseudo_id": 456},
        {"patient_id": 2, "practice_pseudo_id": 123},
        {"patient_id": 3, "practice_pseudo_id": 789},
        {"patient_id": 4, "practice_pseudo_id": 456},
        {"patient_id": 5, "practice_pseudo_id": 789},
    ]


def test_addresses_for_patient_on(in_memory_engine):
    in_memory_engine.populate(
        # Simple case: successive addresses
        {
            tpp.addresses: [
                dict(
                    patient_id=1,
                    address_id=100,
                    start_date=date(2000, 1, 1),
                    end_date=date(2005, 1, 1),
                ),
                dict(
                    patient_id=1,
                    address_id=101,
                    start_date=date(2005, 1, 1),
                    end_date=date(2015, 1, 1),
                ),
                dict(
                    patient_id=1,
                    address_id=102,
                    start_date=date(2015, 1, 1),
                    end_date=date(2020, 1, 1),
                ),
            ]
        },
        # Address with NULL end date
        {
            tpp.addresses: [
                dict(
                    patient_id=2,
                    address_id=103,
                    start_date=date(2000, 1, 1),
                    end_date=None,
                ),
            ]
        },
        # Overlapping: choose address with postcode
        {
            tpp.addresses: [
                dict(
                    patient_id=3,
                    address_id=104,
                    start_date=date(2000, 1, 1),
                    end_date=date(2015, 1, 1),
                    has_postcode=False,
                ),
                dict(
                    patient_id=3,
                    address_id=105,
                    start_date=date(2000, 1, 1),
                    end_date=date(2015, 1, 1),
                    has_postcode=True,
                ),
            ]
        },
        # Overlapping: choose most recent
        {
            tpp.addresses: [
                dict(
                    patient_id=4,
                    address_id=106,
                    start_date=date(2000, 1, 1),
                    end_date=date(2015, 1, 1),
                ),
                dict(
                    patient_id=4,
                    address_id=107,
                    start_date=date(2005, 1, 1),
                    end_date=date(2015, 1, 1),
                ),
            ]
        },
        # Overlapping: choose longest
        {
            tpp.addresses: [
                dict(
                    patient_id=5,
                    address_id=108,
                    start_date=date(2000, 1, 1),
                    end_date=date(2012, 1, 1),
                ),
                dict(
                    patient_id=5,
                    address_id=109,
                    start_date=date(2000, 1, 1),
                    end_date=date(2015, 1, 1),
                ),
            ]
        },
        # Tie-break: choose largest address ID
        {
            tpp.addresses: [
                dict(
                    patient_id=6,
                    address_id=110,
                    start_date=date(2000, 1, 1),
                    end_date=date(2015, 1, 1),
                    has_postcode=True,
                ),
                dict(
                    patient_id=6,
                    address_id=111,
                    start_date=date(2000, 1, 1),
                    end_date=date(2015, 1, 1),
                    has_postcode=True,
                ),
            ]
        },
    )

    address = tpp.addresses.for_patient_on("2010-01-01")

    dataset = Dataset()
    dataset.define_population(tpp.addresses.exists_for_patient())
    dataset.address_id = address.address_id
    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "address_id": 101},
        {"patient_id": 2, "address_id": 103},
        {"patient_id": 3, "address_id": 105},
        {"patient_id": 4, "address_id": 107},
        {"patient_id": 5, "address_id": 109},
        {"patient_id": 6, "address_id": 111},
    ]
