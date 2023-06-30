from datetime import date

from ehrql import Dataset
from ehrql.tables.beta import core


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


def test_ons_deaths_any_cause_of_death_is_in(in_memory_engine):
    in_memory_engine.populate(
        {
            core.ons_deaths: [
                dict(patient_id=1, cause_of_death_01="A000"),
                dict(patient_id=2, cause_of_death_08="B000"),
                dict(patient_id=3, cause_of_death_15="A000"),
            ]
        }
    )

    dataset = Dataset()
    dataset.define_population(core.ons_deaths.exists_for_patient())

    dataset.cause_of_death_is_in_codelist = (
        core.ons_deaths.any_cause_of_death_is_in(["A000"]).count_distinct_for_patient()
        > 0
    )

    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "cause_of_death_is_in_codelist": True},
        {"patient_id": 2, "cause_of_death_is_in_codelist": False},
        {"patient_id": 3, "cause_of_death_is_in_codelist": True},
    ]
