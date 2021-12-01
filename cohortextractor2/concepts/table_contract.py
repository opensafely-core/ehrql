import dataclasses

from .constraints import BaseConstraint, ChoiceConstraint
from .types import BaseType, Choice


@dataclasses.dataclass
class Column:

    type: BaseType  # noqa: A003
    description: str  # noqa: A003
    help: str  # noqa: A003
    constraints: list[BaseConstraint] = dataclasses.field(
        default_factory=list
    )  # noqa: A003


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
