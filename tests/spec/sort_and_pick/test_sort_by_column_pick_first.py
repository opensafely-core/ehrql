from databuilder.query_language import Dataset, IdSeries, IntSeries, build_event_table

from ..helpers import transpose

e = build_event_table(
    "e",
    {
        "patient_id": IdSeries,
        "i": IntSeries,
    },
)


def test_sort_by_column_pick_first(in_memory_engine):
    in_memory_engine.setup(
        {
            e: (
                [1, 101],
                [1, 102],
                [1, 103],
                [2, 203],
                [2, 202],
                [2, 201],
            ),
        }
    )

    dataset = Dataset()
    dataset.use_unrestricted_population()
    dataset.v = e.sort_by(e.i).first_for_patient().i

    results = transpose(in_memory_engine.extract(dataset))

    assert results["v"] == {1: 101, 2: 201}
