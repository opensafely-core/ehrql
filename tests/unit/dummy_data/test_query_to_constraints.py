from datetime import date

from ehrql import create_dataset
from ehrql.dummy_data.query_info import (
    normalize_constraints,
    query_to_column_constraints,
)
from ehrql.query_language import compile
from ehrql.tables import Constraint
from ehrql.tables.core import patients


def test_or_query_includes_constraints_on_each_side():
    dataset = create_dataset()

    dataset.define_population(
        ((patients.date_of_birth.year == 1970) & (patients.sex == "male"))
        | ((patients.date_of_birth.year == 1963) & (patients.sex == "male"))
    )

    variable_definitions = compile(dataset)
    constraints = query_to_column_constraints(variable_definitions["population"])

    assert len(constraints) == 1

    (column,) = constraints.keys()
    assert column.name == "sex"
    (column_constraints,) = constraints.values()
    assert column_constraints == [Constraint.Categorical(values=("male",))]


def test_combine_date_range_constraints():
    dataset = create_dataset()
    index_date = "2023-10-01"

    dataset = create_dataset()

    was_adult = (patients.age_on(index_date) >= 18) & (
        patients.age_on(index_date) <= 100
    )

    was_born_in_particular_range = (patients.date_of_birth < date(2000, 1, 1)) & (
        patients.date_of_birth > date(1970, 1, 1)
    )

    dataset.define_population(was_adult & was_born_in_particular_range)

    variable_definitions = compile(dataset)
    constraints = query_to_column_constraints(variable_definitions["population"])

    assert len(constraints) == 1

    (column,) = constraints.keys()
    assert column.name == "date_of_birth"
    (column_constraints,) = constraints.values()
    assert normalize_constraints(column_constraints) == (
        Constraint.GeneralRange(
            minimum=date(1970, 1, 1),
            maximum=date(2000, 1, 1),
            includes_minimum=False,
            includes_maximum=False,
        ),
    )


def test_or_query_does_not_includes_constraints_on_only_one_size():
    dataset = create_dataset()

    dataset.define_population(
        (patients.date_of_birth.year == 1970) | (patients.sex == "male")
    )

    variable_definitions = compile(dataset)
    constraints = query_to_column_constraints(variable_definitions["population"])

    assert len(constraints) == 0
