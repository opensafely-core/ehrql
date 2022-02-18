from datetime import datetime

from databuilder.backends import TPPBackend
from databuilder.query_language import Dataset
from databuilder.tables import patients
from tests.lib.tpp_schema import patient
from tests.lib.util import extract


def test_dataset(database):
    database.setup(
        patient(dob=datetime(1943, 5, 5)),
        patient(dob=datetime(2000, 1, 1)),
        patient(dob=datetime(2010, 5, 5)),
    )

    dataset = dataset_definition()

    results = extract(dataset, TPPBackend, database)

    assert len(results) == 2
    assert {r["year_of_birth"] for r in results} == {2000, 2010}


def dataset_definition():
    year_of_birth = patients.date_of_birth.year
    dataset = Dataset()
    dataset.set_population(year_of_birth >= 2000)
    dataset.year_of_birth = year_of_birth
    return dataset
