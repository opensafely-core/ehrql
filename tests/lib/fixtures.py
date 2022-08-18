trivial_dataset_definition = """
from databuilder.query_language import Dataset
from databuilder.tables.beta.tpp import patients

dataset = Dataset()
year = patients.date_of_birth.year
dataset.set_population(year >= 1900)
dataset.year = year
"""

invalid_dataset_definition = "this is nonsense"

no_dataset_attribute_dataset_definition = """
from databuilder.query_language import Dataset
from databuilder.tables.beta.tpp import patients

my_dataset = Dataset()
year = patients.date_of_birth.year
my_dataset.set_population(year >= 1900)
"""

invalid_dataset_attribute_dataset_definition = """
from databuilder.query_language import Dataset
from databuilder.tables.beta.tpp import patients

dataset = patients
"""
