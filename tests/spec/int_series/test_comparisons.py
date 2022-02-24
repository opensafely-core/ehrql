from databuilder.query_language import Dataset, IdSeries, IntSeries, build_patient_table

from ..helpers import transpose

p = build_patient_table(
    "p",
    {
        "patient_id": IdSeries,
        "i": IntSeries,
    },
)


def test_comparisons(in_memory_engine, subtests):
    in_memory_engine.setup(
        {
            p: (
                [1, 101],
                [2, 201],
                [3, 301],
                [4, None],
            ),
        }
    )

    dataset = Dataset()
    dataset.use_unrestricted_population()
    dataset.lt = p.i < 201
    dataset.le = p.i <= 201
    dataset.gt = p.i > 201
    dataset.ge = p.i >= 201

    results = transpose(in_memory_engine.extract(dataset))

    with subtests.test("lt"):
        assert results["lt"] == {1: True, 2: False, 3: False, 4: None}

    with subtests.test("le"):
        assert results["le"] == {1: True, 2: True, 3: False, 4: None}

    with subtests.test("gt"):
        assert results["gt"] == {1: False, 2: False, 3: True, 4: None}

    with subtests.test("ge"):
        assert results["ge"] == {1: False, 2: True, 3: True, 4: None}
