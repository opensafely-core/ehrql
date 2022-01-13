import pytest

from databuilder.backends.base import BaseBackend, Column, MappedTable
from databuilder.contracts import types
from databuilder.contracts.base import BackendContractError
from databuilder.contracts.base import Column as ColumnContract
from databuilder.contracts.base import TableContract
from databuilder.contracts.constraints import ChoiceConstraint
from databuilder.query_engines.base_sql import BaseSQLQueryEngine

from ..lib.mock_backend import patient


def test_basic_validation_that_table_implements_patients_contract():
    # Basic table contract
    class PatientsContract(TableContract):
        patient_id = ColumnContract(
            type=types.PseudoPatientId(), description="", help="", constraints=[]
        )
        date_of_birth = ColumnContract(
            type=types.Date(), description="", help="", constraints=[]
        )
        sex = ColumnContract(
            type=types.Choice("F", "M"), description="", help="", constraints=[]
        )

    # Unhappy path
    with pytest.raises(BackendContractError, match="Missing columns: sex"):

        class BadBackend(BaseBackend):
            backend_id = "bad_test_backend"
            query_engine_class = BaseSQLQueryEngine
            patient_join_column = "patient_id"

            patients = MappedTable(
                implements=PatientsContract,
                source="Patient",
                columns=dict(
                    date_of_birth=Column("date", source="DateOfBirth"),
                ),
            )

        PatientsContract.validate_implementation(
            BadBackend, "patients", BadBackend.patients
        )

    # Happy path
    class GoodBackend(BaseBackend):
        backend_id = "good_test_backend"
        query_engine_class = BaseSQLQueryEngine
        patient_join_column = "patient_id"

        patients = MappedTable(
            implements=PatientsContract,
            source="Patient",
            columns=dict(
                date_of_birth=Column("date", source="DateOfBirth"),
                sex=Column("varchar", source="Sex"),
            ),
        )

    assert GoodBackend("db://")


def test_basic_validation_for_patients_contract_column_types():
    # Basic table contract
    class PatientsContract(TableContract):
        patient_id = ColumnContract(
            type=types.PseudoPatientId(), description="", help="", constraints=[]
        )
        date_of_birth = ColumnContract(
            type=types.Date(), description="", help="", constraints=[]
        )
        sex = ColumnContract(
            type=types.Choice("F", "M"), description="", help="", constraints=[]
        )

    # Unhappy path
    with pytest.raises(
        BackendContractError,
        match="Column date_of_birth is defined with an invalid type 'integer'.\n\nAllowed types are: date",
    ):

        class BadBackend(BaseBackend):
            backend_id = "bad_test_backend"
            query_engine_class = BaseSQLQueryEngine
            patient_join_column = "patient_id"

            patients = MappedTable(
                implements=PatientsContract,
                source="Patient",
                columns=dict(
                    date_of_birth=Column("integer", source="DateOfBirth"),
                    sex=Column("varchar", source="Sex"),
                ),
            )

        PatientsContract.validate_implementation(
            BadBackend, "patients", BadBackend.patients
        )


def test_basic_validation_for_patients_contract_column_constraints(engine):
    engine.setup(
        patient(
            1,
            dob="1990-01-01",
        ),
        patient(2, dob="1991-02-01"),
        patient(3, dob="1992-03-01", sex="X"),
    )

    # Basic table contract
    class PatientsContract(TableContract):
        patient_id = ColumnContract(
            type=types.PseudoPatientId(), description="", help="", constraints=[]
        )
        date_of_birth = ColumnContract(
            type=types.Date(), description="", help="", constraints=[]
        )
        sex = ColumnContract(
            type=types.Choice("F", "M"),
            description="",
            help="",
            constraints=[ChoiceConstraint()],
        )

    # Happy path is all there is for now
    class GoodBackend(BaseBackend):
        backend_id = "good_test_backend"
        query_engine_class = BaseSQLQueryEngine
        patient_join_column = "patient_id"

        patients = MappedTable(
            implements=PatientsContract,
            source="Patient",
            columns=dict(
                date_of_birth=Column("date", source="DateOfBirth"),
                sex=Column("varchar", source="Sex"),
            ),
        )

    backend = GoodBackend(database_url=engine.database.host_url())
    comment = "Note: This test is expected to fail when TableContract.validate_data is implemented"
    assert PatientsContract.validate_data(backend, "patients") is None, comment
