from databuilder.query_language import Dataset, IdSeries, IntSeries, build_patient_table

from ..helpers import transpose

p = build_patient_table(
    "p",
    {
        "patient_id": IdSeries,
        "i": IntSeries,
    },
)


def test_add(in_memory_engine):
    in_memory_engine.setup(
        {
            p: (
                [1, 101],
                [2, None],
            ),
        }
    )

    dataset = Dataset()
    dataset.use_unrestricted_population()
    dataset.v1 = p.i + 1
    dataset.v2 = 1 + p.i

    results = transpose(in_memory_engine.extract(dataset))

    assert results["v1"] == {1: (101 + 1), 2: None}
    assert results["v2"] == {1: (1 + 101), 2: None}
