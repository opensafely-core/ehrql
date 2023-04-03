from ..tables import p


title = "Map from one set of values to another"

table_data = {
    p: """
          |  i1
        --+-----
        1 | 101
        2 | 201
        3 | 301
        4 |
        """,
}


def test_map_values(spec_test):
    spec_test(
        table_data,
        p.i1.map_values({101: "a", 201: "b", 301: "a"}, default="c"),
        {
            1: "a",
            2: "b",
            3: "a",
            4: "c",
        },
    )
