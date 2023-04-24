from datetime import date

from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.query_engines.in_memory_database import InMemoryDatabase
from ehrql.query_language import EventFrame, Series, table
from ehrql.utils.orm_utils import make_orm_models


@table
class events(EventFrame):
    date = Series(date)


def test_pick_one_row_per_patient():
    # This test verifies that picking one row per patient works without first having
    # applied QM transformations to all variables in a dataset.
    database = InMemoryDatabase()
    database.setup(make_orm_models({events: [{"patient_id": 1, "date": "2023-01-01"}]}))
    engine = InMemoryQueryEngine(database)
    engine.cache = {}
    frame = events.sort_by(events.date).first_for_patient()
    engine.visit(frame.qm_node)
