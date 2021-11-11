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
