import importlib
import os

import pytest

from cohortextractor2.backends.base import BaseBackend, Column, MappedTable
from cohortextractor2.concepts import types
from cohortextractor2.concepts.table_contract import BackendContractError
from cohortextractor2.concepts.table_contract import Column as ColumnContract
from cohortextractor2.concepts.table_contract import TableContract
from cohortextractor2.query_engines.base_sql import BaseSQLQueryEngine


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

    assert BasicBackend.tables == {
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
    backends = [cls.__name__ for cls in BaseBackend.__subclasses__()]

    backend_no = 0

    for backend in backends:

        # location of backend class
        folder_dir = "cohortextractor2/backends/"
        file_of_backend_class = backend[:-7].lower()

        # exclude mocked or test backends
        path_to_folder = os.path.join(
            os.getcwd(), folder_dir, f"{file_of_backend_class}.py"
        )

        if os.path.exists(path_to_folder):

            # get the class from cohortextractor.backends
            backend_class = getattr(
                importlib.import_module(
                    f"cohortextractor2.backends.{file_of_backend_class}"
                ),
                backend,
            )

            backend_class.validate_all_contracts()
            backend_no += 1

    # Checks at least 3 backends
    assert backend_no >= 3
