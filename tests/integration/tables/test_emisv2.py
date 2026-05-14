from datetime import date

from ehrql import Dataset
from ehrql.tables import emisv2


def test_patients_age_on(in_memory_engine):
    in_memory_engine.populate(
        {
            emisv2.patients: [
                dict(patient_id=1, date_of_birth=date(1980, 1, 1)),
                dict(patient_id=2, date_of_birth=date(1800, 1, 1)),
                dict(patient_id=3, date_of_birth=date(2010, 1, 1)),
                dict(patient_id=4, date_of_birth=date(2010, 1, 2)),
            ]
        }
    )

    dataset = Dataset()
    dataset.define_population(emisv2.patients.exists_for_patient())
    dataset.age_2010 = emisv2.patients.age_on("2010-01-01")
    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "age_2010": 30},
        {"patient_id": 2, "age_2010": 210},
        {"patient_id": 3, "age_2010": 0},
        {"patient_id": 4, "age_2010": -1},
    ]


def test_practice_registrations_for_patient_on(in_memory_engine):
    in_memory_engine.populate(
        # There will only ever be one registration per patient, because
        # practice registrations are derived from the patients table.
        {
            emisv2.practice_registrations: [
                # registered on 2010-01-01
                dict(
                    patient_id=1, start_date=date(2005, 1, 1), end_date=date(2015, 1, 1)
                ),
                # registration starts on 2010-01-01, null end date
                dict(patient_id=2, start_date=date(2010, 1, 1), end_date=None),
                # registration ends on 2010-01-01
                dict(
                    patient_id=3, start_date=date(2000, 1, 1), end_date=date(2010, 1, 1)
                ),
                # registered after 2010-01-01, not included
                dict(
                    patient_id=4, start_date=date(2011, 1, 1), end_date=date(2015, 1, 1)
                ),
                # deregistered before 2010-01-01, not included
                dict(
                    patient_id=5, start_date=date(2000, 1, 1), end_date=date(2009, 1, 1)
                ),
            ]
        },
    )

    reg = emisv2.practice_registrations.for_patient_on("2010-01-01")

    dataset = Dataset()
    dataset.define_population(emisv2.practice_registrations.exists_for_patient())
    dataset.start_date = reg.start_date
    dataset.end_date = reg.end_date
    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "start_date": date(2005, 1, 1), "end_date": date(2015, 1, 1)},
        {"patient_id": 2, "start_date": date(2010, 1, 1), "end_date": None},
        {"patient_id": 3, "start_date": date(2000, 1, 1), "end_date": date(2010, 1, 1)},
        {"patient_id": 4, "start_date": None, "end_date": None},
        {"patient_id": 5, "start_date": None, "end_date": None},
    ]


def test_practice_registrations_exists_for_patient_on(
    in_memory_engine,
):
    in_memory_engine.populate(
        # There will only ever be one registration per patient, because
        # practice registrations are derived from the patients table.
        {
            emisv2.practice_registrations: [
                # registration covers both 2010-01-01 and 2015-01-01
                dict(
                    patient_id=1, start_date=date(2005, 1, 1), end_date=date(2015, 1, 1)
                ),
                # registration covers 2010-01-01 only as deregistered before 2015-01-01
                dict(
                    patient_id=2, start_date=date(2010, 1, 1), end_date=date(2011, 1, 1)
                ),
                # registration covers 2015-01-01 only, NULL end date
                dict(patient_id=3, start_date=date(2015, 1, 1), end_date=None),
                # registered after both dates
                dict(patient_id=4, start_date=date(2016, 1, 1), end_date=None),
            ]
        },
    )

    dataset = Dataset()
    dataset.define_population(emisv2.practice_registrations.exists_for_patient())
    dataset.is_registered_2010_01_01 = (
        emisv2.practice_registrations.exists_for_patient_on("2010-01-01")
    )
    dataset.is_registered_2015_01_01 = (
        emisv2.practice_registrations.exists_for_patient_on("2015-01-01")
    )

    results = in_memory_engine.extract(dataset)

    assert results == [
        {
            "patient_id": 1,
            "is_registered_2010_01_01": True,
            "is_registered_2015_01_01": True,
        },
        {
            "patient_id": 2,
            "is_registered_2010_01_01": True,
            "is_registered_2015_01_01": False,
        },
        {
            "patient_id": 3,
            "is_registered_2010_01_01": False,
            "is_registered_2015_01_01": True,
        },
        {
            "patient_id": 4,
            "is_registered_2010_01_01": False,
            "is_registered_2015_01_01": False,
        },
    ]


def test_practice_registrations_spanning(
    in_memory_engine,
):
    in_memory_engine.populate(
        # There will only ever be one registration per patient, because
        # practice registrations are derived from the patients table.
        {
            emisv2.practice_registrations: [
                # Registration covers time period
                dict(
                    patient_id=1, start_date=date(2005, 1, 1), end_date=date(2015, 1, 1)
                ),
                # Registration with NULL end date
                dict(patient_id=2, start_date=date(2000, 1, 1), end_date=None),
                # Registration is exactly the same as time period
                dict(
                    patient_id=3, start_date=date(2010, 1, 1), end_date=date(2011, 1, 1)
                ),
                # Registration with start date after time period starts
                dict(
                    patient_id=4, start_date=date(2010, 2, 1), end_date=date(2020, 1, 1)
                ),
                # Registration with start date and end date inside time period
                dict(
                    patient_id=5,
                    start_date=date(2010, 2, 1),
                    end_date=date(2010, 12, 1),
                ),
            ]
        },
    )

    dataset = Dataset()
    dataset.define_population(emisv2.practice_registrations.exists_for_patient())
    dataset.has_spanning_practice_registration = (
        emisv2.practice_registrations.spanning("2010-01-01", "2011-01-01")
    ).exists_for_patient()
    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "has_spanning_practice_registration": True},
        {"patient_id": 2, "has_spanning_practice_registration": True},
        {"patient_id": 3, "has_spanning_practice_registration": True},
        {"patient_id": 4, "has_spanning_practice_registration": False},
        {"patient_id": 5, "has_spanning_practice_registration": False},
    ]


def test_addresses_for_patient_on(in_memory_engine):
    in_memory_engine.populate(
        # There will only ever be one address per patient, because
        # addresses are derived from the patients table.
        {
            # registered on 2010-01-01
            emisv2.addresses: [
                dict(
                    patient_id=1,
                    start_date=date(2005, 1, 1),
                    end_date=date(2015, 1, 1),
                    imd_rounded=100,
                )
            ]
        },
        {
            # registered on 2010-01-01, null end date
            emisv2.addresses: [
                dict(
                    patient_id=2,
                    start_date=date(2000, 1, 1),
                    end_date=None,
                    imd_rounded=200,
                ),
            ]
        },
        {
            # registered after 2010-01-01, not included
            emisv2.addresses: [
                dict(
                    patient_id=3,
                    start_date=date(2011, 1, 1),
                    end_date=date(2015, 1, 1),
                    imd_rounded=300,
                )
            ]
        },
        {
            # deregistered before 2010-01-01, not included
            emisv2.addresses: [
                dict(
                    patient_id=4,
                    start_date=date(2000, 1, 1),
                    end_date=date(2009, 1, 1),
                    imd_rounded=400,
                )
            ]
        },
    )

    address = emisv2.addresses.for_patient_on("2010-01-01")

    dataset = Dataset()
    dataset.define_population(emisv2.addresses.exists_for_patient())
    dataset.imd_rounded = address.imd_rounded
    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "imd_rounded": 100},
        {"patient_id": 2, "imd_rounded": 200},
        {"patient_id": 3, "imd_rounded": None},
        {"patient_id": 4, "imd_rounded": None},
    ]
