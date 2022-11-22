import sqlalchemy.orm

from databuilder.query_model import (
    AggregateByPatient,
    PickOneRowPerPatient,
    Position,
    SelectColumn,
    SelectTable,
    Sort,
    TableSchema,
)
from databuilder.utils import orm_utils

schema = TableSchema.from_primitives(i=int, b=bool)
base = sqlalchemy.orm.declarative_base()
EventsTable = orm_utils.orm_class_from_schema(base, "events", schema, False)


def test_sort_booleans_null_first(engine):
    # The transforms add sorts for unsorted selected columns. Here we're checking the semantics
    # of the sort added for boolean columns (which are handled explicitly because some databases
    # don't allow sorting on booleans.
    #
    # The desired sort order is: NULL, False, True.
    #
    # Each of these patients has two records with different boolean values so we do pairwise
    # comparisons. The integer column is there only so we can specify a sort on it in the query
    # model.
    engine.setup(
        [
            EventsTable(patient_id=0, row_id=0, i=0, b=False),
            EventsTable(patient_id=0, row_id=1, i=0, b=True),
            EventsTable(patient_id=1, row_id=2, i=0, b=None),
            EventsTable(patient_id=1, row_id=3, i=0, b=True),
            EventsTable(patient_id=2, row_id=4, i=0, b=None),
            EventsTable(patient_id=2, row_id=5, i=0, b=False),
        ]
    )

    # Sort the events by i and pick the b from the last row.
    events = SelectTable("events", schema)
    by_i = Sort(events, SelectColumn(events, "i"))
    variable = SelectColumn(
        PickOneRowPerPatient(source=by_i, position=Position.LAST),
        "b",
    )
    population = AggregateByPatient.Exists(events)

    assert engine.extract_qm(dict(v=variable, population=population)) == [
        dict(patient_id=0, v=True),  # True sorts after False
        dict(patient_id=1, v=True),  # True sorts after NULL
        dict(patient_id=2, v=False),  # False sorts after NULL
    ]
