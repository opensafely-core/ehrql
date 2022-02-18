from typing import Protocol

from .. import dsl
from ..query_language import DateSeries, IdSeries, StrSeries
from ..sqlalchemy_types import TYPES_BY_NAME


class BaseType(Protocol):
    """
    Base class for Column types defined in a Contract
    """

    # Subclasses must specify the backend Column types that they allow, as
    # tuples of one or more keys from databuilder.sqlalchemy_types.TYPES_BY_NAME
    allowed_backend_types: tuple[TYPES_BY_NAME, ...]


class Boolean(BaseType):
    allowed_backend_types = (TYPES_BY_NAME.boolean,)
    dsl_column = dsl.BoolColumn


class Choice(BaseType):
    """
    A type which restricts column values to a limited set of choices.
    """

    allowed_backend_types = (TYPES_BY_NAME.integer, TYPES_BY_NAME.varchar)
    dsl_column = dsl.StrColumn
    series = StrSeries

    def __init__(self, *choices):
        self.choices = choices


class Code(BaseType):
    allowed_backend_types = (TYPES_BY_NAME.code,)
    dsl_column = dsl.CodeColumn


class Date(BaseType):
    """A type representing a date"""

    allowed_backend_types = (TYPES_BY_NAME.date, TYPES_BY_NAME.datetime)
    dsl_column = dsl.DateColumn
    series = DateSeries


class Float(BaseType):
    allowed_backend_types = (TYPES_BY_NAME.float,)
    dsl_column = dsl.FloatColumn


class Integer(BaseType):
    allowed_backend_types = (TYPES_BY_NAME.integer,)
    dsl_column = dsl.IntColumn


class PseudoPatientId(BaseType):
    """A type representing a pseudonymised patient ID"""

    allowed_backend_types = (TYPES_BY_NAME.integer, TYPES_BY_NAME.varchar)
    dsl_column = dsl.IdColumn
    series = IdSeries


class String(BaseType):
    allowed_backend_types = (TYPES_BY_NAME.varchar,)
    dsl_column = dsl.StrColumn
