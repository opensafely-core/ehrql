from typing import Protocol

from ..sqlalchemy_types import TYPES_BY_NAME


class BaseType(Protocol):
    """
    Base class for Column types defined in a Contract
    """

    # Subclasses must specify the backend Column types that they allow, as
    # tuples of one or more keys from databuilder.sqlalchemy_types.TYPES_BY_NAME
    allowed_backend_types: tuple[TYPES_BY_NAME, ...]


class PseudoPatientId(BaseType):
    """A type representing a pseudonymised patient ID"""

    allowed_backend_types = (TYPES_BY_NAME.integer, TYPES_BY_NAME.varchar)


class Date(BaseType):
    """A type representing a date"""

    allowed_backend_types = (TYPES_BY_NAME.date,)


class Choice(BaseType):
    """
    A type which restricts column values to a limited set of choices.
    """

    allowed_backend_types = (TYPES_BY_NAME.integer, TYPES_BY_NAME.varchar)

    def __init__(self, *choices):
        self.choices = choices
