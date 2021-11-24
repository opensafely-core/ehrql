import dataclasses

from cohortextractor.concepts.types import BaseType


@dataclasses.dataclass
class Column:

    type: BaseType  # noqa: A003
    help: str  # noqa: A003


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
                    f"Column {column} is defined with an invalid type.\n\n"
                    f"Allowed types are: {', '.join(allowed_types)}"
                )
