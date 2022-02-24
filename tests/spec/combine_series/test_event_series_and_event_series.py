from databuilder.query_language import Dataset, IdSeries, IntSeries, build_event_table

from ..helpers import transpose

e = build_event_table(
    "e",
    {
        "patient_id": IdSeries,
        "i1": IntSeries,
        "i2": IntSeries,
    },
)


def test_combine_event_series_and_event_series(in_memory_engine):
    in_memory_engine.setup(
        {
            e: (
                [1, 101, 111],
                [1, 102, 112],
                [2, 201, 211],
                [2, 202, 212],
            ),
        }
    )

    dataset = Dataset()
    dataset.use_unrestricted_population()
    dataset.v = (e.i1 + e.i2).sum_for_patient()

    results = transpose(in_memory_engine.extract(dataset))

    assert results["v"] == {
        1: (101 + 111) + (102 + 112),
        2: (201 + 211) + (202 + 212),
    }
