import dataclasses

from ..dsl import EventFrame, PatientFrame
from ..query_model import Table as QMTable
from .constraints import BaseConstraint, ChoiceConstraint, UniqueConstraint
from .types import BaseType, Choice


@dataclasses.dataclass
class Column:

    type: BaseType  # noqa: A003
    description: str = ""
    help: str = ""  # noqa: A003
    constraints: list[BaseConstraint] = dataclasses.field(default_factory=list)


class BackendContractError(Exception):
    pass


class TableContract:

    columns = None

    def __init_subclass__(cls, **kwargs):
        cls.columns = {}
        for key, value in vars(cls).items():
            if isinstance(value, Column):
                cls.columns[key] = value

    @classmethod
    def validate_implementation(cls, backend, table_name, table):
        """
        Validates that a given backend table has the necessary columns to
        implement a specific contract
        Args:
            backend: Backend the contract is validated against
            table_name: Name of the table
            table: SQLTable
        """
        missing_columns = set(cls.columns) - set(table.columns)
        if missing_columns:
            raise BackendContractError(
                f"\n'{backend.__name__}.{table_name}' does not correctly implement the"
                f" contract for '{cls.__name__}'\n\n"
                f"Missing columns: {', '.join(missing_columns)}"
            )
        backend_table = getattr(backend, table_name)
        for column in cls.columns:
            backend_column_type = backend_table.columns[column].type
            contract_column_type = cls.columns[column].type
            allowed_types = [
                allowed_type.name
                for allowed_type in contract_column_type.allowed_backend_types
            ]

            if backend_column_type not in allowed_types:
                raise BackendContractError(
                    f"\n'{backend.__name__}.{table_name}' does not correctly implement the"
                    f" contract for '{cls.__name__}'\n\n"
                    f"Column {column} is defined with an invalid type '{backend_column_type}'.\n\n"
                    f"Allowed types are: {', '.join(allowed_types)}"
                )

    @classmethod
    def validate_data(cls, backend, table_name):
        """Validate backend data against any column constraints defined in the table contract"""
        backend_table = getattr(backend, table_name)
        for column_name in cls.columns:
            contract_column = cls.columns[column_name]
            constraints = contract_column.constraints
            if isinstance(contract_column.type, Choice):
                constraints = [
                    ChoiceConstraint(contract_column.type.choices),
                    *constraints,
                ]
            for constraint in constraints:
                constraint.validate(backend_table, column_name)

    @classmethod
    def build_dsl_frame(cls):
        """Build a PatientFrame or EventFrame for querying tables that implement this
        contract."""

        cols = {
            name: column.type.dsl_column(name) for name, column in cls.columns.items()
        }
        qm_table = QMTable(cls)

        if any(isinstance(c, UniqueConstraint) for c in cls.patient_id.constraints):
            frame_cls = type(cls.__name__, (PatientFrame,), cols)
            # TODO: revisit this!  For now, PatientFrame is instantiated with a
            # query_model.Row.  As things stand, this will generate SQL with an
            # unnecessary PARTITION OVER, which may carry a performance penalty.
            return frame_cls(qm_table.first_by("patient_id"))
        else:
            frame_cls = type(cls.__name__, (EventFrame,), cols)
            return frame_cls(qm_table)
