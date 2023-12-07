# noqa: INP001
from ehrql import INTERVAL, Measures, years
from ehrql.tables.core import patients


measures = Measures()

measures.define_measure(
    "births",
    numerator=patients.date_of_birth.is_during(INTERVAL),
    denominator=patients.exists_for_patient(),
    group_by={"sex": patients.sex},
    intervals=years(2).starting_on("2020-01-01"),
)
