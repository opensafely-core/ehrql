"""
This contains just enough of erhQL to be able to extract the following dataset:

    year_of_birth = patients.date_of_birth.year
    dataset = Dataset()
    dataset.set_population(year_of_birth <= 2000)
    dataset.year_of_birth = year_of_birth
"""


from __future__ import annotations

from . import query_model as qm
from .query_model import SelectColumn, SelectPatientTable


class Dataset:
    def set_population(self, population: BoolSeries) -> None:
        self.population = population

    def __setattr__(self, name: str, series: Series) -> None:
        # TODO: add check that series is patient series not event series
        super().__setattr__(name, series)

    def compile(self) -> dict[str, qm.Node]:  # noqa A003
        variables = {}
        for name, definition in self._variables():
            variables[name] = definition.compile()
        return {}

    def _variables(self):
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, Series) or isinstance(attr, Column):
                yield name, attr


class TableMeta(type):
    def __setattr__(cls, name, value):
        if isinstance(value, Column):
            value.table = cls
        return super().__setattr__(name, value)


class PatientTable(metaclass=TableMeta):
    def __init__(self, name: str):
        self.name = name

    def compile(self):  # noqa A003
        return SelectPatientTable(name=self.name)


class Column:
    def __init__(self, name: str, series_type):
        self.name = name
        self.series_type = series_type

    def compile(self):  # noqa A003
        return self.series_type(
            SelectColumn(name=self.name, source=self.table.compile())
        ).compile()


class DateColumn(Column):
    def __init__(self, name):
        super().__init__(name, DateSeries)


class Series:
    def __init__(self, qm_node: qm.Node):
        self.qm_node = qm_node

    def compile(self):  # noqa A003
        return self.qm_node


class IdSeries(Series):
    pass


class BoolSeries(Series):
    pass


class IntSeries(Series):
    def __lte__(self, other: int | IntSeries) -> BoolSeries:
        return BoolSeries(qm_node=...)


class DateSeries(Series):
    @property
    def year(self) -> IntSeries:
        return IntSeries(qm_node=...)

    def __le__(self, other):
        return BoolSeries()
