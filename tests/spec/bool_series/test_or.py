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


def test_or(in_memory_engine):
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
    dataset.or_ = p.b1 | p.b2

    results = transpose(in_memory_engine.extract(dataset))

    assert results["or_"] == {
        1: True,
        2: True,
        3: True,
        4: True,
        5: None,
        6: None,
        7: True,
        8: None,
        9: False,
    }
