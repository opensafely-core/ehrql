from databuilder.query_language import (
    BoolSeries,
    Dataset,
    IdSeries,
    IntSeries,
    build_event_table,
)

from ..helpers import transpose

e = build_event_table(
    "e",
    {
        "patient_id": IdSeries,
        "i": IntSeries,
        "b": BoolSeries,
    },
)


def test_take_with_column(in_memory_engine):
    in_memory_engine.setup(
        {
            e: (
                [1, 101, True],
                [1, 102, True],
                [1, 103, None],
                [2, 201, True],
                [2, 202, None],
                [2, 203, False],
                [3, 301, None],
                [3, 302, False],
            ),
        }
    )

    dataset = Dataset()
    dataset.use_unrestricted_population()
    dataset.v = e.take(e.b).i.sum_for_patient()

    results = transpose(in_memory_engine.extract(dataset))

    assert results["v"] == {1: (101 + 102), 2: 201, 3: None}
