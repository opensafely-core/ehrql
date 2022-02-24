from databuilder.query_language import Dataset, IdSeries, IntSeries, build_patient_table

from ..helpers import transpose

p = build_patient_table(
    "p",
    {
        "patient_id": IdSeries,
        "i": IntSeries,
    },
)


def test_arithmetic(in_memory_engine, subtests):
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
    dataset.negate = -p.i
    dataset.add1 = p.i + 1
    dataset.add2 = 1 + p.i
    dataset.subtract1 = p.i - 1
    dataset.subtract2 = 1 - p.i

    results = transpose(in_memory_engine.extract(dataset))

    with subtests.test("negate"):
        assert results["negate"] == {1: -101, 2: None}

    with subtests.test("add"):
        assert results["add1"] == {1: (101 + 1), 2: None}
        assert results["add2"] == {1: (1 + 101), 2: None}

    with subtests.test("subtract"):
        assert results["subtract1"] == {1: (101 - 1), 2: None}
        assert results["subtract2"] == {1: (1 - 101), 2: None}
