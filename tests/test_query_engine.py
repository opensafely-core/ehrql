from databuilder.query_model import (
    AggregateByPatient,
    Function,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
)

from .lib.mock_backend import patient


# IMPORTANT NOTE!!
# This is a quick test to get coverage of the new YearFromDate function. It it NOT to be
# considered as the basis of a new testing strategy or taken as a template for other
# tests. Rather, it should be deleted as soon as possible once we've settled on a
# replacement.
def test_year_from_date(engine):
    engine.setup(
        patient(1, dob="1987-09-11"),
    )

    patients = SelectPatientTable("patients")
    registrations = SelectTable("practice_registrations")

    class DatasetDefinition:
        population = AggregateByPatient.Exists(registrations)
        year_of_birth = Function.YearFromDate(SelectColumn(patients, "date_of_birth"))

    assert engine.extract(DatasetDefinition) == [
        {"patient_id": 1, "year_of_birth": 1987}
    ]
