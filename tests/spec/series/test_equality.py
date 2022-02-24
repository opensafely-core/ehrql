from databuilder.query_language import Dataset, IdSeries, IntSeries, build_patient_table

from ..helpers import transpose

p = build_patient_table(
    "p",
    {
        "patient_id": IdSeries,
        "i1": IntSeries,
        "i2": IntSeries,
    },
)


def test_equality(in_memory_engine, subtests):
    in_memory_engine.setup(
        {
            p: (
                [1, 101, 101],
                [2, 102, 112],
                [3, 103, None],
                [4, None, None],
            ),
        }
    )

    dataset = Dataset()
    dataset.use_unrestricted_population()
    dataset.eq = p.i1 == p.i2
    dataset.ne = p.i1 != p.i2

    results = transpose(in_memory_engine.extract(dataset))

    with subtests.test("eq"):
        assert results["eq"] == {1: True, 2: False, 3: None, 4: None}

    with subtests.test("ne"):
        assert results["ne"] == {1: False, 2: True, 3: None, 4: None}
