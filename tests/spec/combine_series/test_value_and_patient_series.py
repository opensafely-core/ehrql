from databuilder.query_language import Dataset, IdSeries, IntSeries, build_patient_table

from ..helpers import transpose

p = build_patient_table(
    "p",
    {
        "patient_id": IdSeries,
        "i": IntSeries,
    },
)


def test_combine_value_and_patient_series(in_memory_engine):
    in_memory_engine.setup(
        {
            p: (
                [1, 101],
                [2, 201],
            ),
        }
    )

    dataset = Dataset()
    dataset.use_unrestricted_population()
    dataset.v = 1 + p.i

    results = transpose(in_memory_engine.extract(dataset))

    assert results["v"] == {
        1: (1 + 101),
        2: (1 + 201),
    }
