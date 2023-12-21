# noqa: INP001
from datetime import date

from ehrql import Dataset
from ehrql.tables.core import patients


dataset = Dataset()
dataset.define_population(patients.date_of_birth.is_on_or_after("2000-01-01"))

test_data = {
    # Correctly not expected in population
    1: {
        "patients": {"date_of_birth": date(1999, 12, 31)},
        "expected_in_population": False,
    },
}
