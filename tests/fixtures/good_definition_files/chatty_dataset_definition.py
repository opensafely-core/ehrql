# noqa: INP001
import sys

from ehrql import create_dataset
from ehrql.tables.core import patients


print("I am a bit chatty", file=sys.stderr)

dataset = create_dataset()
dataset.year_of_birth = patients.date_of_birth.year
dataset.define_population(patients.exists_for_patient())
