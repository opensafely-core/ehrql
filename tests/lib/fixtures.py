trivial_dataset_definition = """
from databuilder.query_language import Dataset
from databuilder.tables import patients
from databuilder.definition import register

dataset = Dataset()
year = patients.date_of_birth.year
dataset.set_population(year >= 1900)
dataset.year = year
register(dataset)
"""

invalid_dataset_definition = "this is nonsense"
