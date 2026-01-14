from datetime import date

from ehrql import Dataset
from ehrql.tables import tpp


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


def test_practice_registrations_spanning_with_systm_one(
    in_memory_engine,
):
    in_memory_engine.populate(
        # Spanning registration with SystmOne covering period
        {
            tpp.practice_registrations: [
                dict(
                    patient_id=1,
                    practice_pseudo_id=123,
                    start_date=date(2008, 1, 1),
                    end_date=date(2012, 1, 1),
                    practice_systmone_go_live_date=date(2009, 1, 1),
                ),
            ]
        },
        # Spanning registration with SystmOne starting mid-way through period
        {
            tpp.practice_registrations: [
                dict(
                    patient_id=2,
                    practice_pseudo_id=456,
                    start_date=date(2008, 1, 1),
                    end_date=date(2012, 1, 1),
                    practice_systmone_go_live_date=date(2010, 6, 1),
                ),
            ]
        },
    )

    dataset = Dataset()
    dataset.define_population(tpp.practice_registrations.exists_for_patient())
    dataset.has_spanning_practice_registration = (
        tpp.practice_registrations.spanning_with_systmone("2010-01-01", "2011-01-01")
    ).exists_for_patient()
    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "has_spanning_practice_registration": True},
        {"patient_id": 2, "has_spanning_practice_registration": False},
    ]


def test_addresses_imd_quintile(in_memory_engine):
    in_memory_engine.populate(
        {
            tpp.addresses: [
                dict(patient_id=1, imd_rounded=3284, start_date=date(2008, 1, 1)),
                dict(patient_id=2, imd_rounded=3285, start_date=date(2008, 1, 1)),
                dict(patient_id=3, imd_rounded=1, start_date=date(2008, 1, 1)),
                dict(patient_id=4, imd_rounded=32844, start_date=date(2008, 1, 1)),
                dict(patient_id=5, imd_rounded=0, start_date=date(2008, 1, 1)),
                dict(patient_id=6, start_date=date(2008, 1, 1)),
            ]
        },
    )

    dataset = Dataset()
    dataset.define_population(tpp.addresses.exists_for_patient())
    address_on = tpp.addresses.for_patient_on("2010-01-01")
    dataset.imd_quintile = address_on.imd_quintile
    dataset.imd_decile = address_on.imd_decile

    results = in_memory_engine.extract(dataset)

    assert results == [
        {
            "patient_id": 1,
            "imd_quintile": "1 (most deprived)",
            "imd_decile": "1 (most deprived)",
        },
        {"patient_id": 2, "imd_quintile": "1 (most deprived)", "imd_decile": "2"},
        {
            "patient_id": 3,
            "imd_quintile": "1 (most deprived)",
            "imd_decile": "1 (most deprived)",
        },
        {
            "patient_id": 4,
            "imd_quintile": "5 (least deprived)",
            "imd_decile": "10 (least deprived)",
        },
        {
            "patient_id": 5,
            "imd_quintile": "1 (most deprived)",
            "imd_decile": "1 (most deprived)",
        },
        {"patient_id": 6, "imd_quintile": "unknown", "imd_decile": "unknown"},
    ]


def test_decision_support_values_electronic_frailty_index(
    in_memory_engine,
):
    in_memory_engine.populate(
        {
            tpp.decision_support_values: [
                dict(
                    patient_id=1,
                    calculation_date=date(2012, 1, 1),
                    numeric_value=25.0,
                    algorithm_description="UK Electronic Frailty Index (eFI)",
                    algorithm_version="1.0",
                ),
                dict(
                    patient_id=1,
                    calculation_date=date(2010, 1, 1),
                    numeric_value=30.0,
                    algorithm_description="UK Electronic Frailty Index (eFI)",
                    algorithm_version="1.5",
                ),
                dict(
                    patient_id=1,
                    calculation_date=date(2010, 1, 1),
                    numeric_value=25.0,
                    algorithm_description="A different index",
                    algorithm_version="1.0",
                ),
            ]
        },
    )

    dataset = Dataset()
    dataset.define_population(tpp.decision_support_values.exists_for_patient())
    first_efi = (
        tpp.decision_support_values.electronic_frailty_index()
        .sort_by(tpp.decision_support_values.calculation_date)
        .first_for_patient()
    )
    dataset.efi = first_efi.numeric_value
    dataset.efi_year = first_efi.calculation_date.year
    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "efi": 25.0, "efi_year": 2012},
    ]
