from datetime import date

import pytest

from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.query_engines.in_memory_database import InMemoryDatabase
from ehrql.query_language import EventFrame, Series, table
from ehrql.query_model import nodes as qm


@table
class events(EventFrame):
    date = Series(date)


def test_pick_one_row_per_patient():
    # This test verifies that picking one row per patient works without first having
    # applied QM transformations to all variables in a dataset.
    database = InMemoryDatabase(
        {
            events._qm_node: [
                (1, date(2023, 1, 1)),
            ],
        }
    )
    engine = InMemoryQueryEngine(database)
    engine.cache = {}
    frame = events.sort_by(events.date).first_for_patient()
    engine.visit(frame._qm_node)


def test_cast_to_int_raises_for_values_outside_int64_range():
    engine = InMemoryQueryEngine(InMemoryDatabase())
    engine.cache = {}
    positive = qm.Function.CastToInt(source=qm.Value(1e100))
    negative = qm.Function.CastToInt(source=qm.Value(-1e100))

    with pytest.raises(OverflowError, match="Numerical result out of range"):
        engine.visit(positive)
    with pytest.raises(OverflowError, match="Numerical result out of range"):
        engine.visit(negative)
