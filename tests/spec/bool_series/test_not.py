from databuilder.query_language import (
    BoolSeries,
    Dataset,
    IdSeries,
    build_patient_table,
)

from ..helpers import transpose

p = build_patient_table(
    "p",
    {
        "patient_id": IdSeries,
        "b": BoolSeries,
    },
)


def test_not(in_memory_engine):
    in_memory_engine.setup(
        {
            p: (
                [1, True],
                [2, None],
                [3, False],
            ),
        }
    )

    dataset = Dataset()
    dataset.use_unrestricted_population()
    dataset.not_ = ~p.b

    results = transpose(in_memory_engine.extract(dataset))

    assert results["not_"] == {1: False, 2: None, 3: True}
