from databuilder.query_language import Dataset, DateSeries, IdSeries
from databuilder.query_model import Function, SelectColumn, SelectPatientTable, Value
from databuilder.tables import Column, PatientTable


# TODO: import tables from tests.lib.tables
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
