from datetime import datetime

from tests.lib.tpp_schema import patient

dataset_definition = """
from databuilder.query_language import Dataset
from databuilder.tables import patients
from databuilder.definition import register

dataset = Dataset()
year = patients.date_of_birth.year
dataset.set_population(year >= 1900)
dataset.year = year
register(dataset)
"""


def test_generate_dataset(study, database):
    database.setup(patient(dob=datetime(1943, 5, 5)))

    study.setup_from_string(dataset_definition)
    study.run(database, "tpp")
    results = study.results()

    assert len(results) == 1
    assert results[0]["year"] == "1943"
