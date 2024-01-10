# noqa: INP001
from ehrql.tables.core import patients


patients.date_of_birth == "2000-01-01" | patients.date_of_birth == "1990-01-01"
