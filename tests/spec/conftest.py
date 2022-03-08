import pytest

from databuilder.query_language import Dataset


@pytest.fixture
def spec_test(in_memory_engine):
    def run_test(table_data, series, expected_results):
        in_memory_engine.setup(
            {
                table: parse_table(table.name_to_series_cls.keys(), s)
                for table, s in table_data.items()
            }
        )

        dataset = Dataset()
        dataset.use_unrestricted_population()
        dataset.v = series
        results = {r["patient_id"]: r["v"] for r in in_memory_engine.extract(dataset)}
        assert results == expected_results

    return run_test


def parse_table(all_col_names, s):
    """Parse string containing table data, returning list of lists.

    >>> parse_table(
    ...     ['patient_id', 'i1', 'i2', 'i3'],
    ...     '''
    ...       |  i1 |  i2
    ...     --+-----+-----
    ...     1 | 101 | 111
    ...     1 | 102 | 112
    ...     2 | 201 |
    ...     ''',
    ... )
    [[1, 101, 111, None], [1, 102, 112, None], [2, 201, None, None]]
    """

    header, _, *lines = s.strip().splitlines()
    col_names = [token.strip() for token in header.split("|")]
    col_names[0] = "patient_id"
    rows = [parse_row(all_col_names, col_names, line) for line in lines]
    return rows


def parse_row(all_col_names, col_names, line):
    """Parse string containing row data, returning list of values.

    >>> parse_row(
    ...     ['patient_id', 'i1', 'i2', 'i3'],
    ...     ['patient_id', 'i1', 'i2'],
    ...     "1 | 101 | 111",
    ... )
    [1, 101, 111, None]
    """

    col_name_to_value = {
        col_name: parse_value(col_name, token.strip())
        for col_name, token in zip(col_names, line.split("|"))
    }
    return [col_name_to_value.get(name) for name in all_col_names]


def parse_value(col_name, value):
    """Parse string returning value of correct type for column.

    The desired type is determined by the name of the column.  An empty string indicates
    a null value.
    """

    if col_name == "patient_id" or col_name[0] == "i":
        parse = int
    elif col_name[0] == "b":
        parse = lambda v: {"T": True, "F": False}[v]  # noqa E731
    else:
        assert False

    return parse(value) if value else None
