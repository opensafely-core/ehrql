from databuilder.contracts import universal
from databuilder.query_language import DateSeries, IdSeries, StrSeries
from databuilder.query_model import SelectColumn, SelectPatientTable

# mypy: ignore-errors


class Table:
    def __init_subclass__(cls, select=None, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        cls._select = select
        # We allow tables to be defined without contracts to simplify testing.
        if hasattr(cls, "__contract__"):
            cls.__contract__.validate_table(cls)

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
    __contract__ = universal.Patients

    patient_id = IdSeries(
        SelectColumn(name="patient_id", source=SelectPatientTable("patients"))
    )
    date_of_birth = DateSeries(
        SelectColumn(name="date_of_birth", source=SelectPatientTable("patients"))
    )
    date_of_death = DateSeries(
        SelectColumn(name="date_of_death", source=SelectPatientTable("patients"))
    )
    sex = StrSeries(SelectColumn(name="sex", source=SelectPatientTable("patients")))


patients = Patients()
