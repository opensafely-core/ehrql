import datetime

from databuilder.dsl import IdColumn
from databuilder.query_language import Dataset, DateColumn, PatientTable

# This table definition is here as a convenience.
# TODO: instantiate tables with a contract, and import tables from tests.lib.tables
from databuilder.query_model import Function, SelectColumn, SelectPatientTable, Value


class Patients(PatientTable):
    name = "patients"

    patient_id = IdColumn("patient_id")
    date_of_birth = DateColumn("date_of_birth")


patients = Patients()


def test_simple_dataset() -> None:
    year_of_birth = patients.date_of_birth
    dataset = Dataset()
    dataset.set_population(
        year_of_birth <= datetime.date(2000, 1, 1)
    )  # TODO: why does this not typecheck?
    dataset.year_of_birth = year_of_birth

    assert dataset.compile() == {
        "year_of_birth": SelectColumn(
            name="date_of_birth", source=SelectPatientTable("patients")
        ),
        "population": ...,
    }


def test_get_column_from_patient_table():
    # SELECT date_of_birth FROM patients
    assert patients.date_of_birth.compile() == SelectColumn(
        name="date_of_birth", source=SelectPatientTable("patients")
    )


def test_date_comparison():
    assert (
        patients.date_of_birth <= datetime.date(2000, 1, 1)
    ).compile() == Function.LE(
        lhs=SelectColumn(name="date_of_birth", source=SelectPatientTable("patients")),
        rhs=Value(datetime.date(2000, 1, 1)),
    )
