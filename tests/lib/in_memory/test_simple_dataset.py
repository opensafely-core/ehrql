from datetime import date

from databuilder.query_language import (
    Dataset,
    DateSeries,
    IdSeries,
    build_patient_table,
)

patients = build_patient_table(
    "patients",
    {
        "patient_id": IdSeries,
        "date_of_birth": DateSeries,
    },
)


def test_simple_dataset(in_memory_engine):
    in_memory_engine.setup(
        {
            patients: (
                [1, date(1999, 1, 1)],
                [2, date(2000, 1, 1)],
                [3, date(2001, 1, 1)],
                [4, None],
            ),
        }
    )
    year_of_birth = patients.date_of_birth.year
    dataset = Dataset()
    dataset.set_population(year_of_birth <= 2000)
    dataset.year_of_birth = year_of_birth

    results = in_memory_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "year_of_birth": 1999},
        {"patient_id": 2, "year_of_birth": 2000},
    ]
