from databuilder.query_language import Dataset, IdSeries, IntSeries, build_event_table

from ..helpers import transpose

e = build_event_table(
    "e",
    {
        "patient_id": IdSeries,
        "i": IntSeries,
    },
)


def test_combine_event_series_and_value(in_memory_engine):
    in_memory_engine.setup(
        {
            e: (
                [1, 101],
                [1, 102],
                [2, 201],
                [2, 202],
            ),
        }
    )

    dataset = Dataset()
    dataset.use_unrestricted_population()
    dataset.v = (e.i + 1).sum_for_patient()

    results = transpose(in_memory_engine.extract(dataset))

    assert results["v"] == {
        1: (101 + 1) + (102 + 1),
        2: (201 + 1) + (202 + 1),
    }
