"""
This contains just enough of erhQL to be able to extract the following dataset:

    year_of_birth = patients.date_of_birth.year
    dataset = Dataset()
    dataset.set_population(year_of_birth <= 2000)
    dataset.year_of_birth = year_of_birth
"""


from __future__ import annotations

from .query_model import Function, SelectColumn, SelectPatientTable, Value


class Dataset:
    def __init__(self):
        self.variables = {}

    def set_population(self, population: BoolSeries) -> None:
        self.population = population

    def __setattr__(self, name: str, value: object) -> None:
        if isinstance(value, Series) or isinstance(value, Column):
            # TODO: add check that series is patient series not event series
            self.variables[name] = value
        else:
            super().__setattr__(name, value)

    def compile(self) -> dict[str, qm.Node]:  # noqa A003
        return {name: variable.qm_node for name, variable in self.variables.items()}


class Table:
    def __init__(self, qm_node):
        self.qm_node = qm_node

        for key in dir(self):
            field = getattr(self, key)
            if isinstance(field, Column):
                field.table = self


class PatientTable(Table):
    def __init__(self):
        super().__init__(SelectPatientTable(name=self.__name__))


class DateOperations:
    def __le__(self, other):
        return BoolSeries(Function.LE(lhs=self.qm_node, rhs=Value(other)))


class Series:
    def __init__(self, qm_node):
        self.qm_node = qm_node


class IdSeries(Series):
    pass


class BoolSeries(Series):
    pass


class DateSeries(Series, DateOperations):
    pass


class Column:
    def __init__(self, name: str, series_type):
        self.name = name
        self.series_type = series_type

    @property
    def qm_node(self):
        return SelectColumn(name=self.name, source=self.table.qm_node)


class DateColumn(Column, DateOperations):
    def __init__(self, name):
        super().__init__(name, DateSeries)
