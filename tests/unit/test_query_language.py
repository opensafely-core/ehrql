from databuilder.query_language import Dataset, DateSeries, IdSeries
from databuilder.query_model import Function, SelectColumn, SelectPatientTable, Value


# TODO: Instantiate tables with contracts and import them from tests.lib.tables
class Table:
    def __init_subclass__(cls, select=None, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        cls._select = select

    @classmethod
    def select(cls):
        return cls._select(name=cls.__name__.lower())


class Column:
    def __init__(self, series_cls):
        self.series_cls = series_cls

    def __set_name__(self, owner, name):
        # We could instantiate the series class with qm_node=None on initialization, and
        # store a reference to the instance rather than the class. However, we must bind
        # the instance to the query model here, because here we know the owner and the
        # name.
        self.series = self.series_cls(
            qm_node=SelectColumn(source=owner.select(), name=name)
        )

    def __get__(self, instance, owner=None):
        return self.series


class PatientTable(Table, select=SelectPatientTable):
    pass


class Patients(PatientTable):
    patient_id = Column(IdSeries)
    date_of_birth = Column(DateSeries)


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
