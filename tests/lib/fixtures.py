trivial_dataset_definition = """
from databuilder.ehrql import Dataset
from databuilder.tables.beta.tpp import patients

dataset = Dataset()
year = patients.date_of_birth.year
dataset.define_population(year >= 1940)
dataset.year = year
"""

no_dataset_attribute_dataset_definition = """
from databuilder.ehrql import Dataset
from databuilder.tables.beta.tpp import patients

my_dataset = Dataset()
year = patients.date_of_birth.year
my_dataset.define_population(year >= 1900)
"""

invalid_dataset_attribute_dataset_definition = """
from databuilder.ehrql import Dataset
from databuilder.tables.beta.tpp import patients

dataset = patients
"""

invalid_dataset_query_model_error_definition = """
from databuilder.ehrql import Dataset
from databuilder.tables.beta.tpp import patients

# Odd construction is required to get an error that comes from inside library code.
dataset.column = patients.date_of_birth.year + (patients.sex.is_null())
"""

parameterised_dataset_definition = """
from argparse import ArgumentParser
from databuilder.ehrql import Dataset
from databuilder.tables.beta.tpp import patients

parser = ArgumentParser()
parser.add_argument("--year", type=int)
args = parser.parse_args()

dataset = Dataset()
year = patients.date_of_birth.year
dataset.define_population(year >= args.year)
dataset.year = year
"""
