from ehrql import Dataset
from ehrql.query_model.graphs import build_graph
from ehrql.tables.tpp import patients


def test_build_graph():
    dataset = Dataset()
    year = patients.date_of_birth.year
    dataset.define_population(year >= 1940)
    dataset.year = year

    # We just want to check that nothing blows up
    build_graph(dataset._compile())
