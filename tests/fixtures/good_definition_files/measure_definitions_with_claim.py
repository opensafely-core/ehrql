# noqa: INP001
from ehrql import INTERVAL, claim_permissions, create_measures, years
from ehrql.tables.core import patients


claim_permissions("some_permission", "another_permission")

measures = create_measures()

measures.define_measure(
    "births",
    numerator=patients.date_of_birth.is_during(INTERVAL),
    denominator=patients.exists_for_patient(),
    intervals=years(2).starting_on("2020-01-01"),
)
