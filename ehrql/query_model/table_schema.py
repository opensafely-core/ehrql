import dataclasses
import datetime
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

    class DateAfter(BaseConstraint):
        column_names: tuple[str]

        def __post_init__(self):
            if isinstance(self.column_names, str):
                # Guard against a single column name being supplied as a string
                raise TypeError(
                    "'column_names' must be a tuple or list of column names"
                )
            # Accept values as list rather than a tuple as they don't suffer from the
            # trailing comma problem
            _setattrs(self, column_names=tuple(self.column_names))

        @property
        def description(self):
            return f"Date must be on or after the date value in column(s) {', '.join(self.column_names)}"

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
    dummy_data_constraints: tuple[BaseConstraint] = ()

    def __post_init__(self):
        _setattrs(
            self,
            # Accept constraints as list rather than a tuple as they don't suffer from
            # the trailing comma problem
            constraints=tuple(self.constraints),
            dummy_data_constraints=tuple(self.dummy_data_constraints),
            # We build an internal lookup table of constraints by their type
            _constraints_by_type={},
            _dummy_data_constraints_by_type={},
        )
        # Populate the lookup tables
        self._constraints_by_type.update(
            self._build_constraints_by_type(self.constraints)
        )
        self._dummy_data_constraints_by_type.update(
            self._build_constraints_by_type(self.dummy_data_constraints)
        )
        if self.get_constraint_by_type(Constraint.DateAfter):
            raise ValueError(
                "'Constraint.DateAfter' can only be specified as a dummy data constraint."
            )

    def get_constraint_by_type(self, cls):
        return self._constraints_by_type.get(cls)

    def __repr__(self):
        # Gives us `self == eval(repr(self))`
        module = self.type_.__module__
        prefix = f"{module}." if module != "builtins" else ""
        type_repr = f"{prefix}{self.type_.__name__}"
        return (
            f"{self.__class__.__name__}({type_repr}, constraints={self.constraints!r}, "
            f"dummy_data_constraints={self.dummy_data_constraints!r})"
        )

    def _build_constraints_by_type(self, constraints):
        constraints_by_type = {}
        for c in constraints:
            cls = type(c)
            # Supplying the class rather than the instance seems like an easy mistake to
            # make so we'll guard against that here
            if cls is type:
                raise ValueError(
                    f"Constraint should be instance not class e.g. "
                    f"'{c.__qualname__}()' not '{c.__qualname__}'"
                )
            # Enforce that we get only one instance of each type of constraint
            if cls in (
                self._constraints_by_type
                | self._dummy_data_constraints_by_type
                | constraints_by_type
            ):
                raise ValueError(f"'{cls.__qualname__}' specified more than once")
            if cls is Constraint.DateAfter and self.type_ is not datetime.date:
                raise ValueError(
                    f"'Constraint.DateAfter' cannot be specified on a column with "
                    f"type '{self.type_.__name__}'."
                )
            constraints_by_type[cls] = c
        return constraints_by_type

    @property
    def column_and_dummy_data_constraints(self):
        return self.constraints + self.dummy_data_constraints


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
        self._validate_date_after_constraints(kwargs)
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

    @staticmethod
    def _validate_date_after_constraints(schema):
        def get_names_of_dependent_columns(column):
            if date_after := column._dummy_data_constraints_by_type.get(
                Constraint.DateAfter
            ):
                return date_after.column_names
            return []

        def get_transitive_dependencies(column_name, visited):
            if column_name in visited:
                return None  # Cycle detected

            dependencies = []
            for direct_dep in get_names_of_dependent_columns(schema[column_name]):
                transitive_deps = get_transitive_dependencies(
                    direct_dep, visited + [column_name]
                )
                if transitive_deps is None:
                    return None  # Cycle detected in recursion
                dependencies.extend([direct_dep] + transitive_deps)
            return dependencies

        for name, column in schema.items():
            declared_dependent_columns = get_names_of_dependent_columns(column)
            for dep_name in declared_dependent_columns:
                dep_col = schema.get(dep_name)
                if dep_col is None:
                    raise ValueError(
                        f"Column '{name}' has a 'Constraint.DateAfter' dummy data constraint "
                        f"referring to non-existent column '{dep_name}'"
                    )
                if dep_col.type_ is not datetime.date:
                    raise ValueError(
                        f"Column '{name}' cannot be a date after '{dep_name}' "
                        f"as '{dep_name}' is not a date column"
                    )
                constraints_diff = set(
                    column.column_and_dummy_data_constraints
                ).symmetric_difference(set(dep_col.column_and_dummy_data_constraints))
                if not all(
                    isinstance(c, Constraint.DateAfter)
                    or isinstance(c, Constraint.NotNull)
                    for c in constraints_diff
                ):
                    raise ValueError(
                        f"Columns '{name}' and '{dep_name}' have incompatible constraints "
                        f"for a 'Constraint.DateAfter' relationship"
                    )

            # Check for cycles and undeclared transitive dependencies
            transitive_dependencies = get_transitive_dependencies(name, [])
            if transitive_dependencies is None:
                raise ValueError(
                    f"Column '{name}' has a cyclic dependency in its 'Constraint.DateAfter' "
                    f"dummy data constraints"
                )
            for transitive_dep_name in transitive_dependencies:
                if transitive_dep_name not in declared_dependent_columns:
                    raise ValueError(
                        f"Column '{transitive_dep_name}' is not declared in "
                        f"column '{name}'s 'Constraint.DateAfter', but is "
                        f"transitively required to be before '{name}'"
                    )


# We need this to customise the initialisation of frozen dataclasses. Using frozen
# dataclasses gets us so much for free that I think it's worth this little bit of
# unpleasantness.
def _setattrs(obj, **attrs):
    for key, value in attrs.items():
        object.__setattr__(obj, key, value)
