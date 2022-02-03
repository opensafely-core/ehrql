from databuilder.query_language import (
    Column,
    Dataset,
    DateSeries,
    IdSeries,
    PatientTable,
)


# This table definition is here as a convenience.
# TODO: instantiate tables with a contract, and import tables from tests.lib.tables
class Patients(PatientTable):
    patient_id = IdSeries(Column("patient_id"))
    date_of_birth = DateSeries(Column("date_of_birth"))


patients = Patients("patients")


def test_simple_dataset() -> None:
    year_of_birth = patients.date_of_birth.year
    dataset = Dataset()
    dataset.set_population(year_of_birth <= 2000)  # TODO: why does this not typecheck?
    dataset.year_of_birth = year_of_birth

    assert dataset.compile() == {
        "year_of_birth": ...,
        "population": ...,
    }
