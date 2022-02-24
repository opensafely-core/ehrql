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


def test_drop_with_column(in_memory_engine):
    in_memory_engine.setup(
        {
            e: (
                [1, 101, True],
                [1, 102, True],
                [1, 103, None],
                [2, 201, True],
                [2, 202, None],
                [2, 203, False],
                [3, 301, True],
                [3, 302, True],
            ),
        }
    )

    dataset = Dataset()
    dataset.use_unrestricted_population()
    dataset.v = e.drop(e.b).i.sum_for_patient()

    results = transpose(in_memory_engine.extract(dataset))

    assert results["v"] == {1: 103, 2: (202 + 203), 3: None}
