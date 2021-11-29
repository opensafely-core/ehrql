from __future__ import annotations

from dataclasses import dataclass
from pprint import pprint
from typing import Generic, TypeVar, overload, Type


@dataclass
class Expression:
    ...


@dataclass
class Operator:
    ...


class Add(Operator):
    ...


class Sub(Operator):
    ...


class GT(Operator):
    ...


@dataclass
class BinaryExpression(Expression):
    operator: Operator
    left: Expression
    right: Expression


@dataclass
class Constant(Expression):
    value: int


@dataclass
class Root(Expression):
    table: str
    column: str


class Value:
    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def compile(self) -> Expression:
        return self.expression


ValueT = TypeVar("ValueT", bound=Value)


class BooleanValue(Value):
    ...


class IntValue(Value):
    def __add__(self, other: int | IntValue) -> IntValue:
        right: Expression
        if isinstance(other, int):
            right = Constant(other)
        else:
            right = other.expression
        return IntValue(BinaryExpression(Add(), self.expression, right))

    def __gt__(self, other: int | IntValue) -> BooleanValue:
        right: Expression
        if isinstance(other, int):
            right = Constant(other)
        else:
            right = other.expression
        return BooleanValue(BinaryExpression(GT(), self.expression, right))


class DateValue(Value):
    def __add__(self, days: int) -> DateValue:
        return DateValue(BinaryExpression(Sub(), self.expression, Constant(days)))

    @overload
    def __sub__(self, other: int) -> DateValue:
        ...

    @overload
    def __sub__(self, other: DateValue) -> IntValue:
        ...

    def __sub__(self, other: int | DateValue) -> DateValue | IntValue:
        if isinstance(other, int):
            return DateValue(BinaryExpression(Sub(), self.expression, Constant(other)))
        return IntValue(BinaryExpression(Sub(), self.expression, other.expression))


class Column(Generic[ValueT]):
    def __init__(self, name: str, value_type: Type[ValueT]) -> None:
        self.name = name
        self.value_type = value_type


class Table:
    def __init__(self, name: str) -> None:
        self.name = name

    def get(self, column: Column[ValueT]) -> ValueT:
        return column.value_type(Root(self.name, column.name))


class Birthdays(Table):
    def __init__(self) -> None:
        super().__init__("birthdays")

    birthday = Column("birthday", DateValue)
    deserves_presents = Column("deserves_presents", BooleanValue)
    cakes = Column("cakes", IntValue)


birthdays = Birthdays()


class Dataset:
    def compile(self) -> dict[str, Expression]:
        return {
            n: v.expression for n, v in self.__dict__.items() if isinstance(v, Value)
        }

    def __setattr__(self, key: str, value: Value) -> None:
        super().__setattr__(key, value)


dataset = Dataset()

dataset.presents = birthdays.get(birthdays.deserves_presents)

dataset.cakes = birthdays.get(birthdays.cakes)
dataset.more_cakes = dataset.cakes + 1
dataset.combined_number = dataset.cakes + dataset.cakes
dataset.comparison = dataset.cakes > dataset.cakes + 1

dataset.a_date = birthdays.get(birthdays.birthday)
dataset.another_date = dataset.a_date + 10
dataset.and_another = dataset.another_date - 5
dataset.days_between = dataset.another_date - dataset.a_date

pprint(dataset.compile())
