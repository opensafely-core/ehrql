import datetime

import pytest

from ehrql import Dataset


@pytest.fixture(params=["execute", "dump_sql"])
def spec_test(request, engine):
    # Test that we can insert the data, run the query, and get the expected results
    def run_test_execute(table_data, series, expected_results, population=None):
        # Populate database tables.
        engine.populate(
            {
                table: parse_table(table._qm_node.schema, s)
                for table, s in table_data.items()
            }
        )

        # Create a Dataset with the specified population and a single variable which is
        # the series under test.
        dataset = make_dataset(table_data, population)
        dataset.v = series

        # If we're comparing floats then we want only approximate equality to account
        # for rounding differences
        if series._type is float:
            expected_results = pytest.approx(expected_results, rel=1e-5)

        # Extract data, and check it's as expected.
        results = [(r["patient_id"], r["v"]) for r in engine.extract(dataset)]
        results_dict = dict(results)
        assert len(results) == len(results_dict), "Duplicate patient IDs found"
        assert results_dict == expected_results

        # Assert types are as expected
        for patient_id, value in results_dict.items():
            if value is not None:
                assert isinstance(value, series._type), (
                    f"Expected {series._type} got {type(value)} in "
                    f"result {{{patient_id}: {value}}}"
                )

    # Test that we can generate SQL with literal parmeters for debugging purposes
    def run_test_dump_sql(table_data, series, expected_results, population=None):
        # Create a Dataset with the specified population and a single variable which is
        # the series under test.
        dataset = make_dataset(table_data, population)
        dataset.v = series

        # Check that we can generate SQL without error
        assert engine.dump_dataset_sql(dataset)

    mode = request.param

    if mode == "execute":
        return run_test_execute
    elif mode == "dump_sql":
        if engine.name == "in_memory":
            pytest.skip("in_memory engine produces no SQL")
        return run_test_dump_sql
    else:
        assert False


def make_dataset(table_data, population=None):
    # To reduce noise in the tests we provide a default population which contains all
    # patients in any tables referenced in the data
    if population is None:
        population = False
        for table in table_data.keys():
            population = table.exists_for_patient() | population
    dataset = Dataset()
    dataset.define_population(population)
    return dataset


def parse_table(schema, s):
    """Parse string containing table data, returning list of dicts.

    See test_conftest.py for examples.
    """

    header, _, *lines = s.strip().splitlines()
    col_names = [token.strip() for token in header.split("|")]
    col_names[0] = "patient_id"
    column_types = dict(
        patient_id=int, **{name: type_ for name, type_ in schema.column_types}
    )
    rows = [parse_row(column_types, col_names, line) for line in lines]
    return rows


def parse_row(column_types, col_names, line):
    """Parse string containing row data, returning list of values.

    See test_conftest.py for examples.
    """

    return {
        col_name: parse_value(column_types[col_name], token.strip())
        for col_name, token in zip(col_names, line.split("|"))
    }


def parse_value(type_, value):
    """Parse string returning value of correct type for column.

    An empty string indicates a null value.
    """
    if not value:
        return None

    if hasattr(type_, "_primitive_type"):
        type_ = type_._primitive_type()

    if type_ is bool:
        parse = lambda v: {"T": True, "F": False}[v]  # noqa E731
    elif type_ == datetime.date:
        parse = datetime.date.fromisoformat
    else:
        parse = type_

    return parse(value)
