from databuilder.query_model import (
    AggregateByPatient,
    Filter,
    Function,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    Value,
)

from .lib.mock_backend import Patients, RegistrationHistory, patient

# TODO
# IMPORTANT NOTE!!
# The tests here are temporary tests added to support modifications we needed to make to the query engine before the
# long-term testing approach has been agreed and implemented. They should be deleted as soon as possible once we've
# settled on a replacement.


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


def test_population_with_boolean_column(engine):
    engine.setup(
        patient(1, some_bool=True),
        patient(2, some_bool=False),
    )

    class DatasetDefinition:
        population = SelectColumn(SelectPatientTable("patients"), "some_bool")

    assert len(engine.extract(DatasetDefinition)) == 1


def test_population_with_boolean_function(engine):
    engine.setup(
        patient(1, some_int=1),
        patient(2, some_int=2),
    )

    class DatasetDefinition:
        population = Function.GT(
            SelectColumn(SelectPatientTable("patients"), "some_int"), Value(1)
        )

    assert len(engine.extract(DatasetDefinition)) == 1


def test_population_with_event_table(engine):
    engine.setup(
        Patients(PatientId=1),
        RegistrationHistory(PatientId=1, EndDate="2999-12-31"),
        Patients(PatientId=2),
        RegistrationHistory(PatientId=2, EndDate="1999-12-31"),
    )

    class DatasetDefinition:
        population = AggregateByPatient.Exists(
            Filter(
                SelectTable("practice_registrations"),
                Function.GT(
                    SelectColumn(SelectTable("practice_registrations"), "date_end"),
                    Value("2020-01-01"),
                ),
            )
        )

    assert len(engine.extract(DatasetDefinition)) == 1
