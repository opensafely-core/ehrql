from databuilder.query_language import (
    Dataset,
    IdSeries,
    IntSeries,
    build_event_table,
    build_patient_table,
)

from ..helpers import transpose

p = build_patient_table(
    "p",
    {
        "patient_id": IdSeries,
        "i": IntSeries,
    },
)


e = build_event_table(
    "e",
    {
        "patient_id": IdSeries,
        "i": IntSeries,
    },
)


def test_combine_patient_series_and_event_series(in_memory_engine):
    in_memory_engine.setup(
        {
            p: (
                [1, 101],
                [2, 201],
            ),
            e: (
                [1, 111],
                [1, 112],
                [2, 211],
                [2, 212],
            ),
        }
    )

    dataset = Dataset()
    dataset.use_unrestricted_population()
    dataset.v = (p.i + e.i).sum_for_patient()

    results = transpose(in_memory_engine.extract(dataset))

    assert results["v"] == {
        1: (101 + 111) + (101 + 112),
        2: (201 + 211) + (201 + 212),
    }
