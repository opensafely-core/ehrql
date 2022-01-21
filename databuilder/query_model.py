import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Literal, Union


class AggregationFunction(Enum):
    EXISTS = "exists"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    SUM = "sum"


class Function(Enum):
    EQ = "eq"
    NE = "ne"
    LT = "lt"
    LE = "le"
    GT = "gt"
    GE = "ge"

    IN = "in"
    NOT_IN = "not_in"

    AND = "and"
    OR = "or"
    NOT = "not"

    IS_NULL = "is_null"

    DATE_DIFFERENCE = "date_difference"
    ROUND_TO_FIRST_OF_MONTH = "round_to_first_of_month"
    ROUND_TO_FIRST_OF_YEAR = "round_to_first_of_year"
    DATE_ADD = "date_add"
    DATE_SUBTRACT = "date_subtract"
    DATE_DELTA_ADD = "date_delta_add"
    DATE_DELTA_SUBTRACT = "date_delta_subtract"


# Singleton to represent the default join column (currently "patient_id"). By not
# allowing this to be referenced using a string we avoid inadvertently hardcoding this
# into our codebase
DEFAULT_JOIN_COLUMN = object()


class QueryNode:
    """
    Abstract base class for every node in the Query Model
    """


class TableValue(QueryNode):
    """
    Abstract base class for all operations whose output is something table-like
    """


class ColumnValue(QueryNode):
    """
    Abstract base class for all operations whose output is something column-like
    """


# These are the basic types we accept as arguments in the Query Model
Scalar = Union[None, bool, int, float, str, datetime.datetime, datetime.date]
StaticValue = Union[Scalar, tuple[Scalar]]

Argument = Union[ColumnValue, StaticValue]


@dataclass(frozen=True)
class SelectTable(TableValue):
    name: str


@dataclass(frozen=True)
class SelectColumn(ColumnValue):
    source: TableValue
    name: Union[str, Literal[DEFAULT_JOIN_COLUMN]]


@dataclass(frozen=True)
class Filter(TableValue):
    source: TableValue
    condition: ColumnValue


@dataclass(frozen=True)
class SortAndSelectFirst(TableValue):
    source: TableValue
    sort_columns: tuple[ColumnValue]
    descending: bool = False


@dataclass(frozen=True)
class Aggregate(ColumnValue):
    function: AggregationFunction
    arguments: tuple[Argument]


@dataclass(frozen=True)
class ApplyFunction(ColumnValue):
    function: Function
    arguments: tuple[Argument]


@dataclass(frozen=True)
class Categorise(ColumnValue):
    categories: dict[Argument, ColumnValue]
    default: Argument

    def __hash__(self):
        # `categories` is a dict and so not hashable by default, but we treat it as
        # immutable once created so we're fine to make it hashable
        return hash((tuple(self.categories.items()), self.default))


@dataclass(frozen=True)
class Codelist(QueryNode):
    codes: tuple
    system: str
    has_categories: bool = False

    def __post_init__(self):
        if self.has_categories:
            raise NotImplementedError("Categorised codelists are currently unsupported")

    def __repr__(self):
        if len(self.codes) > 5:
            codes = self.codes[:5] + ("...",)
        else:
            codes = self.codes
        return f"Codelist(system={self.system}, codes={codes})"
