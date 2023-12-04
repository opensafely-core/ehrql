# A tiny example of a generative test case defined in a standalone file so that we can
# check that the `test_query_model_example_file` function works correctly
from ehrql.query_model.nodes import (
    AggregateByPatient,
    Column,
    SelectColumn,
    SelectPatientTable,
    TableSchema,
)


p0 = SelectPatientTable(
    "p0",
    TableSchema(
        i1=Column(int),
    ),
)

population = AggregateByPatient.Exists(p0)
variable = SelectColumn(p0, "i1")
data = []
