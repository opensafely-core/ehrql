"""
This contains just enough of erhQL to be able to extract the following dataset:

    year_of_birth = patients.date_of_birth.year
    dataset = Dataset()
    dataset.set_population(year_of_birth <= 2000)
    dataset.year_of_birth = year_of_birth
"""


from __future__ import annotations

from . import query_model as qm


class Dataset:
    def set_population(self, population: BoolSeries) -> None:
        self.population = population

    def __setattr__(self, name: str, series: Series) -> None:
        # TODO: add check that series is patient series not event series
        super().__setattr__(name, series)

    def compile(self) -> dict[str, qm.Node]:  # noqa A003
        return ...


class PatientTable:
    def __init__(self, name: str):
        self.name = name


class Column:
    def __init__(self, name: str):
        self.name = name


class Series:
    def __init__(self, qm_node: qm.Node):
        self.qm_node = qm_node


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
