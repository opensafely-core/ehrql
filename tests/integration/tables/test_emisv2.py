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
    ]
