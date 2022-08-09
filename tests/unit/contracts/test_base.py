import datetime

import pytest

from databuilder.backends.base import BaseBackend, Column, MappedTable
from databuilder.contracts import types
from databuilder.contracts.base import BackendContractError
from databuilder.contracts.base import Column as ColumnContract
from databuilder.contracts.base import TableContract
from databuilder.query_engines.base_sql import BaseSQLQueryEngine


class PatientsContract(TableContract):
    _name = "patients"

    patient_id = ColumnContract(type=types.PseudoPatientId())
    date_of_birth = ColumnContract(type=types.Date())
    sex = ColumnContract(type=types.Choice("F", "M"))


def test_validate_implementation_success():
    class GoodBackend(BaseBackend):
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

    PatientsContract.validate_implementation(GoodBackend, "patients")


def test_validate_implementation_failure_misnamed_table():
    class BadBackend(BaseBackend):
        query_engine_class = BaseSQLQueryEngine
        patient_join_column = "patient_id"

        patience = MappedTable(
            implements=PatientsContract,
            source="Patient",
            columns=dict(
                date_of_birth=Column("date", source="DateOfBirth"),
            ),
        )

    with pytest.raises(
        BackendContractError, match="Attribute should be called 'patients'"
    ):
        PatientsContract.validate_implementation(BadBackend, "patience")


def test_validate_implementation_failure_missing_column():
    class BadBackend(BaseBackend):
        query_engine_class = BaseSQLQueryEngine
        patient_join_column = "patient_id"

        patients = MappedTable(
            implements=PatientsContract,
            source="Patient",
            columns=dict(
                date_of_birth=Column("date", source="DateOfBirth"),
            ),
        )

    with pytest.raises(BackendContractError, match="Missing columns: sex"):
        PatientsContract.validate_implementation(BadBackend, "patients")


def test_validate_implementation_failure_invalid_type():
    class BadBackend(BaseBackend):
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

    with pytest.raises(
        BackendContractError,
        match="Column date_of_birth is defined with an invalid type 'integer'.\n\nAllowed types are: date",
    ):
        PatientsContract.validate_implementation(BadBackend, "patients")


def test_validate_schema():
    PatientsContract.validate_schema(
        {
            "sex": str,
            "date_of_birth": datetime.date,
        }
    )


def test_validate_schema_wrong_columns():
    with pytest.raises(AssertionError):
        PatientsContract.validate_schema(
            {
                "sex": str,
                "date_of_birth": datetime.date,
                "extra_column": int,
            }
        )


def test_validate_schema_wrong_types():
    with pytest.raises(AssertionError):
        PatientsContract.validate_schema(
            {
                "sex": str,
                "date_of_birth": str,
            }
        )
