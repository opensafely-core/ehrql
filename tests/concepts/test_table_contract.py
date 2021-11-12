import pytest

from cohortextractor.backends.base import BaseBackend, Column, MappedTable
from cohortextractor.concepts import types
from cohortextractor.concepts.table_contract import BackendContractError
from cohortextractor.concepts.table_contract import Column as ColumnContract
from cohortextractor.concepts.table_contract import TableContract
from cohortextractor.query_engines.base_sql import BaseSQLQueryEngine


def test_basic_validation_that_table_implements_patients_contract():
    # Basic table contract
    class PatientsContract(TableContract):
        patient_id = ColumnContract(type=types.PseudoPatientId(), help="")
        date_of_birth = ColumnContract(type=types.Date(), help="")
        sex = ColumnContract(type=types.Choice("F", "M"), help="")

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
