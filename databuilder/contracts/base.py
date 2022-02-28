import dataclasses

from . import types
from .constraints import BaseConstraint, NotNullConstraint, UniqueConstraint
from .types import BaseType


@dataclasses.dataclass
class Column:
    type: BaseType  # noqa: A003
    description: str = ""
    notes_for_implementors: str = ""
    implementation_notes_to_add_to_description: str = ""
    constraints: list[BaseConstraint] = dataclasses.field(default_factory=list)
    required: bool = True


# many contracts need this column so lets just define it once.
PatientIDColumn = Column(
    type=types.PseudoPatientId(),
    description=(
        "Patient's pseudonymous identifier, for linkage."
        "This will not normally be output, or operated on by researchers."
    ),
    constraints=[NotNullConstraint(), UniqueConstraint()],
)


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
    def validate_implementation(cls, backend, table_name):
        """
        Validates that a given backend table has the necessary columns to
        implement a specific contract
        Args:
            backend: Backend the contract is validated against
            table_name: Name of the table
        """

        def _raise_backend_contract_error(msg):
            msg = (
                f"\n'{backend.__name__}.{table_name}' does not correctly implement the"
                f" contract for '{cls.__name__}'\n\n"
            ) + msg
            raise BackendContractError(msg)

        table = getattr(backend, table_name)

        if table_name != cls._name:
            _raise_backend_contract_error(f"Attribute should be called '{cls._name}'")

        missing_columns = set(cls.columns) - set(table.columns)
        if missing_columns:
            _raise_backend_contract_error(
                f"Missing columns: {', '.join(missing_columns)}"
            )

        for column in cls.columns:
            backend_column_type = table.columns[column].type
            contract_column_type = cls.columns[column].type
            allowed_types = [
                allowed_type.name
                for allowed_type in contract_column_type.allowed_backend_types
            ]

            if backend_column_type not in allowed_types:
                _raise_backend_contract_error(
                    f"Column {column} is defined with an invalid type '{backend_column_type}'.\n\n"
                    f"Allowed types are: {', '.join(allowed_types)}"
                )

    @classmethod
    def validate_table(cls, table_cls):
        """Validate that a table is defined with the correct attributes.
        This uses asserts rather than raising other exceptions, since any invalid tables
        must be identified and fixed by the development team.
        Note that we could use similar logic to generate a table from a contract.
        However, doing so would mean that we wouldn't be able to typecheck dataset definitions.
        """
        contract_column_names = set(cls.columns)
        table_column_names = set(table_cls.name_to_series_cls)
        assert contract_column_names == table_column_names
        for col_name, column in cls.columns.items():
            assert (
                column.type.series == table_cls.name_to_series_cls[col_name]
            ), f"{col_name} doesn't match {column}"
