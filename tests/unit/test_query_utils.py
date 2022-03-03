from databuilder.query_language import Dataset
from databuilder.query_utils import get_column_definitions
from databuilder.tables import patients


def test_get_column_definitions_preserves_order():
    dataset = Dataset()
    dataset.set_population(True)
    dataset.foo = patients.date_of_birth.year
    dataset.baz = patients.date_of_birth.year + 100
    dataset.bar = patients.date_of_birth.year - 100

    column_definitions = get_column_definitions(dataset)
    columns = list(column_definitions.keys())
    assert columns == ["population", "foo", "baz", "bar"]
