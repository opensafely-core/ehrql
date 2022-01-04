import pytest

from databuilder.backends.base import BaseBackend, Column, MappedTable
from databuilder.contracts import types
from databuilder.contracts.base import BackendContractError
from databuilder.contracts.base import Column as ColumnContract
from databuilder.contracts.base import TableContract
from databuilder.query_engines.base_sql import BaseSQLQueryEngine


def test_backend_tables():
    """Test that a backend registers its table names"""

    class BasicBackend(BaseBackend):
        backend_id = "basic_test_backend"
        query_engine_class = BaseSQLQueryEngine
        patient_join_column = "patient_id"

        patients = MappedTable(
            source="Patient",
            columns=dict(
                date_of_birth=Column("date", source="DateOfBirth"),
            ),
        )

        clinical_events = MappedTable(
            source="coded_events",
            columns=dict(
                code=Column("code", source="EventCode"),
                date=Column("date", source="Date"),
            ),
        )

    assert set(BasicBackend.tables) == {
        "patients",
        "clinical_events",
    }


class PatientsContract(TableContract):
    """
    A test contract that backends can be validates against
    """

    patient_id = ColumnContract(type=types.PseudoPatientId(), help="", description="")
    date_of_birth = ColumnContract(type=types.Date(), help="", description="")
    sex = ColumnContract(type=types.Choice("F", "M"), help="", description="")


def test_bad_backend_with_validate_contract():

    # Create a Backend which will fail to implement a contract
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

    bad_backend = BadBackend(database_url="test")

    with pytest.raises(BackendContractError, match="Missing columns: sex"):
        bad_backend.validate_all_contracts()


def test_good_backend_with_validate_contract():
    # Create a Backend which will implement a contract
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

    good_backend = GoodBackend(database_url="test")
    good_backend.validate_all_contracts()


def test_validate_all_backends():
    """
    Loops through all the backends, excluding test ones,
    and validates they meet any contract that they claim to
    """
    backends = [
        backend
        for backend in BaseBackend.__subclasses__()
        if backend.__module__.startswith("databuilder.backends.")
    ]

    for backend in backends:
        backend.validate_all_contracts()

    # Checks at least 3 backends
    assert len(backends) >= 3


def test_get_table_implementing():
    class Backend(BaseBackend):
        backend_id = "test_backend"
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

        events = MappedTable(
            source="Event",
            columns=dict(
                date=Column("date", source="Date"),
                code=Column("varchar", source="Code"),
            ),
        )

    backend = Backend(database_url="test")
    table = backend.get_table_implementing(PatientsContract)
    assert table.source == "Patient"
