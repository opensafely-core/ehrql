from datetime import date

from databuilder.ehrql import Dataset
from databuilder.query_language import EventFrame, Series, table

from .variables_lib import create_sequential_variables


@table
class events(EventFrame):
    date = Series(date)
    value = Series(int)


def test_create_sequential_variables(in_memory_engine):
    engine = in_memory_engine

    engine.populate(
        {events: [dict(patient_id=1, date=date(2020, n * 2, 1)) for n in range(1, 5)]},
        {events: [dict(patient_id=2, date=date(2020, n * 3, 1)) for n in range(1, 4)]},
    )

    dataset = Dataset()
    dataset.set_population(events.exists_for_patient())

    frame = events.take(events.date.is_on_or_after("2020-04-01"))
    create_sequential_variables(
        dataset, "date_{n}", frame, column="date", num_variables=3
    )

    results = engine.extract(dataset)
    assert results == [
        {
            "patient_id": 1,
            "date_1": date(2020, 4, 1),
            "date_2": date(2020, 6, 1),
            "date_3": date(2020, 8, 1),
        },
        {
            "patient_id": 2,
            "date_1": date(2020, 6, 1),
            "date_2": date(2020, 9, 1),
            "date_3": None,
        },
    ]


def test_create_sequential_variables_with_different_sort_column(in_memory_engine):
    engine = in_memory_engine

    engine.populate(
        {
            events: [
                dict(patient_id=1, date=date(2020, n * 2, 1), value=n)
                for n in range(1, 5)
            ]
        },
        {
            events: [
                dict(patient_id=2, date=date(2020, n * 3, 1), value=n)
                for n in range(1, 4)
            ]
        },
    )

    dataset = Dataset()
    dataset.set_population(events.exists_for_patient())

    frame = events.take(events.date.is_on_or_after("2020-04-01"))
    create_sequential_variables(
        dataset, "value_{n}", frame, column="value", sort_column="date", num_variables=3
    )

    results = engine.extract(dataset)
    assert results == [
        {
            "patient_id": 1,
            "value_1": 2,
            "value_2": 3,
            "value_3": 4,
        },
        {
            "patient_id": 2,
            "value_1": 2,
            "value_2": 3,
            "value_3": None,
        },
    ]
