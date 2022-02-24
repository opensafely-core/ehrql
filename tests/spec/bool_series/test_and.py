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
        "b1": BoolSeries,
        "b2": BoolSeries,
    },
)


def test_and(in_memory_engine):
    in_memory_engine.setup(
        {
            p: (
                [1, True, True],
                [2, True, None],
                [3, True, False],
                [4, None, True],
                [5, None, None],
                [6, None, False],
                [7, False, True],
                [8, False, None],
                [9, False, False],
            ),
        }
    )

    dataset = Dataset()
    dataset.use_unrestricted_population()
    dataset.and_ = p.b1 & p.b2

    results = transpose(in_memory_engine.extract(dataset))

    assert results["and_"] == {
        1: True,
        2: None,
        3: False,
        4: None,
        5: None,
        6: False,
        7: False,
        8: False,
        9: False,
    }
