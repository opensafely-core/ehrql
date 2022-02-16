"""
This contains just enough of ehrQL to be able to extract the following dataset:

    year_of_birth = patients.date_of_birth.year
    dataset = Dataset()
    dataset.set_population(year_of_birth <= 2000)
    dataset.year_of_birth = year_of_birth
"""
from __future__ import annotations

from .query_model import Function, Node, Value


class Dataset:
    def __init__(self):
        self.variables = {}

    def set_population(self, population: BoolSeries) -> None:
        self.population = population

    def __setattr__(self, name: str, value: object) -> None:
        if isinstance(value, Series):
            # TODO: Check that value is patient series not event series, remembering
            # that value can have a source property (it's a SelectColumn) or lhs/rhs
            # properties (it's a ComparisonFunction)
            self.variables[name] = value
        else:
            super().__setattr__(name, value)

    def compile(self) -> dict[str, Node]:  # noqa A003
        return {name: variable.qm_node for name, variable in self.variables.items()}


class Series:
    def __init__(self, qm_node):
        self.qm_node = qm_node


class IdSeries(Series):
    pass


class BoolSeries(Series):
    pass


class IntSeries(Series):
    def __le__(self, other):
        return BoolSeries(Function.LE(lhs=self.qm_node, rhs=Value(other)))

    def __ge__(self, other):
        return BoolSeries(Function.GE(lhs=self.qm_node, rhs=Value(other)))


class DateSeries(Series):
    @property
    def year(self):
        return IntSeries(Function.YearFromDate(source=self.qm_node))


class StrSeries(Series):
    pass
