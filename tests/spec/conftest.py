import pytest

from databuilder.query_language import Dataset

from ..lib.mock_backend import E, P
from .tables import p


@pytest.fixture
def spec_test(engine):
    def run_test(table_data, series, expected_results):
        # Create SQLAlchemy model instances for each row of each table in table_data.
        input_data = []
        for table, s in table_data.items():
            model = {
                "p": P,
                "e": E,
            }[table.qm_node.name]
            input_data.extend(model(**row) for row in parse_table(s))

        # Ensure there is a P instance for every row in table e.  This lets us set the
        # population without needing dataset.use_unrestricted_population to work.
        patient_ids = {item.PatientId for item in input_data if isinstance(item, P)}
        event_patient_ids = {
            item.PatientId for item in input_data if isinstance(item, E)
        }
        for patient_id in event_patient_ids - patient_ids:
            input_data.append(P(PatientId=patient_id))

        # Populate database tables.
        engine.setup(*input_data)

        # Create a Dataset whose population is every patient in table p, with a single
        # variable which is the series under test.
        dataset = Dataset()
        dataset.set_population(~p.patient_id.isnull())
        dataset.v = series

        # Extract data, and check it's as expected.
        results = {r["patient_id"]: r["v"] for r in engine.extract(dataset)}
        assert results == expected_results

    return run_test


def parse_table(s):
    """Parse string containing table data, returning list of dicts.

    >>> parse_table(
    ...     '''
    ...       |  i1 |  i2
    ...     --+-----+-----
    ...     1 | 101 | 111
    ...     2 | 201 |
    ...     ''',
    ... )
    [{'PatientId': 1, 'i1': 101, 'i2': 111}, {'PatientId': 2, 'i1': 201, 'i2': None}]
    """

    header, _, *lines = s.strip().splitlines()
    col_names = [token.strip() for token in header.split("|")]
    col_names[0] = "PatientId"
    rows = [parse_row(col_names, line) for line in lines]
    return rows


def parse_row(col_names, line):
    """Parse string containing row data, returning list of values.

    >>> parse_row(
    ...     ['PatientId', 'i1', 'i2'],
    ...     "1 | 101 | 111",
    ... )
    {'PatientId': 1, 'i1': 101, 'i2': 111}
    """

    return {
        col_name: parse_value(col_name, token.strip())
        for col_name, token in zip(col_names, line.split("|"))
    }


def parse_value(col_name, value):
    """Parse string returning value of correct type for column.

    The desired type is determined by the name of the column.  An empty string indicates
    a null value.
    """

    if col_name == "PatientId" or col_name[0] == "i":
        parse = int
    elif col_name[0] == "b":
        parse = lambda v: {"T": True, "F": False}[v]  # noqa E731
    else:
        assert False

    return parse(value) if value else None
