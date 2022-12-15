import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen=True)
class Column:
    type_: type
    categories: Optional[tuple] = None

    def __repr__(self):
        # Gives us `self == eval(repr(self))`
        module = self.type_.__module__
        prefix = f"{module}." if module != "builtins" else ""
        type_repr = f"{prefix}{self.type_.__name__}"
        return f"{self.__class__.__name__}({type_repr}, categories={self.categories!r})"


class TableSchema:
    "Defines a mapping of column names to column definitions"

    @classmethod
    def from_primitives(cls, **kwargs):
        return cls(**{name: Column(type_) for name, type_ in kwargs.items()})

    def __init__(self, **kwargs):
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

    def get_column_type(self, name):
        return self.schema[name].type_

    def get_column_categories(self, name):
        return self.schema[name].categories

    @property
    def column_names(self):
        return list(self.schema.keys())

    @property
    def column_types(self):
        return [(name, column.type_) for name, column in self.schema.items()]
