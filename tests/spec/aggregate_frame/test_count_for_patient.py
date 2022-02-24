from databuilder.query_language import (
    Dataset,
    IdSeries,
    build_event_table,
    build_patient_table,
)

from ..helpers import transpose

p = build_patient_table(
    "p",
    {
        "patient_id": IdSeries,
    },
)


e = build_event_table(
    "e",
    {
        "patient_id": IdSeries,
    },
)


def test_count_for_patient(in_memory_engine):
    in_memory_engine.setup(
        {
            p: ([1], [2], [3]),
            e: ([1], [1], [2]),
        },
    )

    dataset = Dataset()
    dataset.use_unrestricted_population()
    dataset.v = e.count_for_patient()

    results = transpose(in_memory_engine.extract(dataset))

    assert results["v"] == {
        1: 2,
        2: 1,
        3: 0,
    }
