import dataclasses
from re import match
from typing import Any

from ehrql.utils.regex_utils import validate_regex


class BaseConstraint:
    def __init_subclass__(cls, **kwargs):
        assert hasattr(cls, "description")
        dataclasses.dataclass(cls, frozen=True)


class Constraint:
    class Categorical(BaseConstraint):
        values: tuple

        def __post_init__(self):
            # Accept values as list rather than a tuple as they don't suffer from the
            # trailing comma problem
            _setattrs(self, values=tuple(self.values))

        @property
        def description(self):
            return f"Possible values: {', '.join(f'`{v}`' for v in self.values)}"

        def validate(self, value):
            return value in self.values if value is not None else True

    class NotNull(BaseConstraint):
        description = "Never `NULL`"

        def validate(self, value):
            return value is not None

    class Unique(BaseConstraint):
        description = "Always unique"

        def validate(self, value):
            # We can't validate a single value
            return True

    class FirstOfMonth(BaseConstraint):
        description = "Always the first day of a month"

        def validate(self, value):
            return value.day == 1 if value else True

    class Regex(BaseConstraint):
        regex: str

        def __post_init__(self):
            validate_regex(self.regex)

        @property
        def description(self):
            return f"Matches regular expression: `{self.regex}`"

        def validate(self, value):
            return bool(match(self.regex, value)) if value is not None else True

    class ClosedRange(BaseConstraint):
        minimum: int
        maximum: int
        step: int = 1

        @property
        def description(self):
            if self.step == 1:
                return f"Always >= {self.minimum} and <= {self.maximum}"
            return f"Always >= {self.minimum}, <= {self.maximum}, and a multiple of {self.step}"

        def validate(self, value):
            return self.minimum <= value <= self.maximum if value is not None else True

    class GeneralRange(BaseConstraint):
        minimum: Any = None
        maximum: Any = None

        includes_minimum: bool = True
        includes_maximum: bool = True

        @property
        def description(self):
            parts = []
            if self.minimum is not None:
                if self.includes_minimum:
                    parts.append(f">= {self.minimum}")
                else:
                    parts.append(f"> {self.minimum}")
            if self.maximum is not None:
                if self.includes_maximum:
                    parts.append(f"<= {self.maximum}")
                else:
                    parts.append(f"< {self.maximum}")
            if parts:
                return "Always " + ", ".join(parts)
            else:
                return "Any value"

        def validate(self, value):
            if value is None:
                return True
            if self.minimum is not None:
                if self.minimum > value:
                    return False
                if self.minimum == value:
                    return self.includes_minimum
            if self.maximum is not None:
                if self.maximum < value:
                    return False
                if self.maximum == value:
                    return self.includes_maximum
            return True


@dataclasses.dataclass(frozen=True)
class Column:
    type_: type
    constraints: tuple[BaseConstraint] = ()

    def __post_init__(self):
        _setattrs(
            self,
            # Accept constraints as list rather than a tuple as they don't suffer from
            # the trailing comma problem
            constraints=tuple(self.constraints),
            # We build an internal lookup table of constraints by their type
            _constraints_by_type={},
        )
        # Enforce that we get only one instance of each type of constraint and populate
        # the lookup table
        for constraint in self.constraints:
            cls = type(constraint)
            # Supplying the class rather than the instance seems like an easy mistake to
            # make so we'll guard against that here
            if cls is type:
                raise ValueError(
                    f"Constraint should be instance not class e.g. "
                    f"'{constraint.__qualname__}()' not '{constraint.__qualname__}'"
                )
            if cls in self._constraints_by_type:
                raise ValueError(f"'{cls.__qualname__}' specified more than once")
            self._constraints_by_type[cls] = constraint

    def get_constraint_by_type(self, cls):
        return self._constraints_by_type.get(cls)

    def __repr__(self):
        # Gives us `self == eval(repr(self))`
        module = self.type_.__module__
        prefix = f"{module}." if module != "builtins" else ""
        type_repr = f"{prefix}{self.type_.__name__}"
        return (
            f"{self.__class__.__name__}({type_repr}, constraints={self.constraints!r})"
        )


class TableSchema:
    "Defines a mapping of column names to column definitions"

    @classmethod
    def from_primitives(cls, **kwargs):
        return cls(**{name: Column(type_) for name, type_ in kwargs.items()})

    def __init__(self, **kwargs):
        if "patient_id" in kwargs:
            raise ValueError(
                "`patient_id` is an implicitly included column on every table "
                "and must not be explicitly specified"
            )
        self.schema = kwargs

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return self.schema == other.schema
        return NotImplemented

    def __hash__(self):
        return hash(tuple(self.schema.items()))

    def __repr__(self):
        # Gives us `self == eval(repr(self))` as for dataclasses
        kwargs = [f"{key}={value!r}" for key, value in self.schema.items()]
        return f"{self.__class__.__name__}({', '.join(kwargs)})"

    def get_column(self, name):
        return self.schema[name]

    def get_column_type(self, name):
        return self.schema[name].type_

    def get_column_constraint_by_type(self, name, constraint_type):
        return self.schema[name].get_constraint_by_type(constraint_type)

    def get_column_categories(self, name):
        categorical = self.get_column_constraint_by_type(name, Constraint.Categorical)
        if categorical:
            return categorical.values

    @property
    def column_names(self):
        return list(self.schema.keys())

    @property
    def column_types(self):
        return [(name, column.type_) for name, column in self.schema.items()]


# We need this to customise the initialisation of frozen dataclasses. Using frozen
# dataclasses gets us so much for free that I think it's worth this little bit of
# unpleasantness.
def _setattrs(obj, **attrs):
    for key, value in attrs.items():
        object.__setattr__(obj, key, value)
