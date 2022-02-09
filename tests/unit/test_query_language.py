from databuilder.query_language import Dataset, DateSeries, IdSeries
from databuilder.query_model import (
    Function,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    Value,
)


class Table:
    def __init_subclass__(cls, select=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._select = select

    @classmethod
    def select(cls):
        return cls._select(cls.__name__.lower())


class PatientTable(Table, select=SelectPatientTable):
    pass


class EventTable(Table, select=SelectTable):
    pass


class Column:
    def __init__(self, series_type):
        self.series_type = series_type

    def __set_name__(self, owner, name):
        self.series = self.series_type(SelectColumn(name=name, source=owner.select()))

    def __get__(self, obj, objtype=None):
        return self.series


def id_column():
    return Column(IdSeries)


def date_column():
    return Column(DateSeries)


# This table is here as a convenience
# TODO: Instantiate tables with contracts and import them from tests.lib.tables
class Patients(PatientTable):
    patient_id = id_column()
    date_of_birth = date_column()


patients = Patients()


def test_dataset() -> None:
    year_of_birth = patients.date_of_birth.year
    dataset = Dataset()
    dataset.set_population(year_of_birth <= 2000)
    dataset.year_of_birth = year_of_birth

    assert dataset.compile() == {
        "year_of_birth": Function.YearFromDate(
            source=SelectColumn(
                name="date_of_birth", source=SelectPatientTable("patients")
            )
        ),
        "population": Function.LE(
            lhs=Function.YearFromDate(
                source=SelectColumn(
                    name="date_of_birth", source=SelectPatientTable("patients")
                )
            ),
            rhs=Value(2000),
        ),
    }
