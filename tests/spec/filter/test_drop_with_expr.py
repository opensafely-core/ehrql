from databuilder.query_language import Dataset, IdSeries, IntSeries, build_event_table

from ..helpers import transpose

e = build_event_table(
    "e",
    {
        "patient_id": IdSeries,
        "i1": IntSeries,
        "i2": IntSeries,
    },
)


def test_drop_with_expr(in_memory_engine):
    in_memory_engine.setup(
        {
            e: (
                [1, 101, 111],
                [1, 102, 112],
                [1, 103, 113],
                [2, 201, 211],
                [2, 202, 212],
                [2, 203, 213],
                [3, 301, None],
            ),
        }
    )

    dataset = Dataset()
    dataset.use_unrestricted_population()
    condition = (e.i1 + e.i2) < 413
    dataset.v = e.drop(condition).i1.sum_for_patient()

    results = transpose(in_memory_engine.extract(dataset))

    assert results["v"] == {1: None, 2: (202 + 203), 3: 301}
