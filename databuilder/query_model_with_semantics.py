from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Union

# --------------------
# First a few value types identifying the operations and literal types in the model.
# --------------------
class BinaryFunction(Enum):
    EQ = "eq"
    NE = "ne"
    IN = "in"
    NOT_IN = "not_in"
    # ... | lt | le | gt | ge | and | or | date_diff | date_add | date_sub | date_delta_add | date_delta_sub)

class UnaryFunction(Enum):
    IS_NULL = "is_null"
    NOT_NULL = "not_null"
    ROUND_TO_FIRST_OF_MONTH = "round_to_first_of_month"
    ROUND_TO_FIRST_OF_YEAR = "round_to_first_of_year"

@dataclass
class CodeList:
    codes: set[str]

Value = Union[str, int, bool, float, date, CodeList]

# --------------------
# Abstract types that can appear in the query graph
# --------------------

# Every node in the graph has this type
class Node:
    ...

# This is used to track the distinction between patient- and event-level types
class Dimension(Enum):
    EVENT = "event"
    PATIENT = "patient"
    HIGHER = "higher"  # TODO: undefined what happens when you combine event frames

# Used to track the origin of frames and series to enforce the constraint that we only combine columns from the same
# table.
Root = Union["Table", "Join"]

# Every node that depends on values calculated from the database has this type. The fields on this type do not need
# to be serialized, they are just required to maintain invariants during construction and could be calculated for any
# well-formed graph.
@dataclass
class BoundNode(Node):
    root: Root  # each bound node knows which table it originated from
    dimension: Dimension  # and whether it represents patient- or event-level data

# Every composition represented by the graph has a simple type with respect to frames and series, for both inputs and
# outputs, so we can represent frames and series as classes although they too are really only needed to enforce
# invariants at construction time.
class Frame(BoundNode):
    ...
class Series(BoundNode):
    ...

# --------------------
# The only non-bound nodes are these leaf nodes
# --------------------

@dataclass
class Column(Node):
    name: str

# Used for injecting value types into functions
@dataclass
class PartialBinaryFunction(Node):
    function: BinaryFunction
    left: Value

# --------------------
# Table is the only bound leaf node. This is a "concrete" frame that maps to an actual table.
# --------------------
@dataclass
class Table(Frame):
    root: Root = field(compare=False)
    name: str

    def __init__(self, name: str, dimension: Dimension):
        super().__init__(self, dimension)
        self.name = name

# --------------------
# All the remaining nodes types are bound nodes that compose frames and series in various ways. The types of those
# compositions are summarized here.
#
# Functions from frames to frames:
#
#     Filter(predicate: Series, frame: Frame) -> Frame
#           The predicate is any calculation on columns in the underlying table which gives a boolean.
#
#     Sort(target: Series, frame: Frame) -> Frame
#           The target is any calculation on columns in the underlying table which gives something ordered. This is 
#           more general than expected, but this allows us to have just one operation (Select) which pulls a column out 
#           of a table.
#
#     Pick(position: Position, frame: Frame) -> Frame
#           This is the operation that takes the first or last of a sorted event frame and returns a patient frame. I'm 
#           not terribly happy with this name.
#
#     Join(left: Frame, right: Frame) -> Frame
#           Combining frames. This creates a new root so that subsequent operations can combine series from the two 
#           frames.
#
# Transforming from frames to series:
#
#     Select(column: Column, frame: Frame) -> Series
#           Pick a single column out of a frame to from a series.
#
#     Aggregate(aggregation: Aggregation, series: Series, frame: Frame) -> Series
#           SQL aggregation. The only other way to get a series from a frame.
#
# Functions from series to series:
# 
#     Combine(operation: BinaryFunction, left: Series, right: Series) -> Series
#           Combine two series to create a new one.
#
#     Map(mapping: Mapping, series: Series) -> Series
#           Transform one series into another. (Perhaps "transform" would be a better name.)
#
# Each of these operations enforces a precise set of constraints on its arguments -- both on their dimensions and on
# their roots. And each one has its own way of calculating its own dimension and root from those of the arguments. This
# logic is encapsulated in the constructors below.
# --------------------

@dataclass
class Filter(Frame):
    predicate: Series
    frame: Frame

    def __init__(self, predicate: Series, frame: Frame):
        super().__init__(frame.root, Dimension.EVENT)

        assert predicate.root == frame.root
        assert predicate.dimension == Dimension.EVENT
        assert frame.dimension == Dimension.EVENT
        # TODO: precondition: predicate must be boolean

        self.predicate = predicate
        self.frame = frame

@dataclass
class Sort(Frame):
    target: Series
    frame: Frame

    def __init__(self, target: Series, frame: Frame):
        super().__init__(frame.root, Dimension.EVENT)

        assert target.root == frame.root
        assert target.dimension == Dimension.EVENT
        assert frame.dimension == Dimension.EVENT
        # TODO: precondition: property must have an orderable type

        self.target = target
        self.frame = frame

class Position(Enum):
    FIRST = "first"
    LAST = "last"

@dataclass
class Pick(Frame):
    position: Position
    frame: Frame

    def __init__(self, position: Position, frame: Frame):
        super().__init__(frame.root, Dimension.PATIENT)

        assert frame.dimension == Dimension.EVENT
        # TODO: precondition: frame must be sorted

        self.position = position
        self.frame = frame

@dataclass
class Join(Frame):
    root: Root = field(compare=False)
    left: Frame
    right: Frame

    def __init__(self, left: Frame, right: Frame):
        dimensions = {left.dimension, right.dimension}
        if dimensions == {Dimension.PATIENT}:
            dimension = Dimension.PATIENT
        elif dimensions == {Dimension.PATIENT, Dimension.EVENT}:
            dimension = Dimension.EVENT
        elif dimensions == {Dimension.EVENT}:
            dimension = Dimension.HIGHER
        else:
            assert False

        super().__init__(self, dimension)

        self.left = left
        self.right = right

@dataclass
class Select(Series):
    column: Column
    frame: Frame

    def __init__(self, column: Column, frame: Frame):
        super().__init__(frame.root, frame.dimension)

        self.column = column
        self.frame = frame

class Aggregation(Enum):
    EXISTS = "exists"
    # ... | min | max | count | sum

@dataclass
class Aggregate(Series):
    aggregation: Aggregation
    series: Series
    frame: Frame

    def __init__(self, aggregation: Aggregation, series: Series, frame: Frame):
        super().__init__(frame.root, Dimension.PATIENT)

        assert series.root == frame.root
        assert series.dimension == Dimension.EVENT
        assert frame.dimension == Dimension.EVENT

        self.aggregation = aggregation
        self.series = series
        self.frame = frame

@dataclass
class Combine(Series):
    operation: BinaryFunction
    left: Series
    right: Series

    def __init__(self, operation: BinaryFunction, left: Series, right: Series):
        super().__init__(left.root, left.dimension)

        assert left.dimension == right.dimension
        assert left.root == right.root

        self.operation = operation
        self.left = left
        self.right = right

Mapping = Union[UnaryFunction, PartialBinaryFunction]

@dataclass
class Map(Series):
    mapping: Mapping
    series: Series

    def __init__(self, mapping: Mapping, series: Series):
        super().__init__(series.root, series.dimension)
        self.mapping = mapping
        self.series = series

# --------------------
# This is a construction helper that checks that we've reduced all variables to patient series. Need not be serialized.
# --------------------
@dataclass
class Var:
    series: Series

    def __init__(self, series: Series):
        assert series.dimension == Dimension.PATIENT
        self.series = series

# --------------------
# And finally some examples, with the corresponding DSL definitions.
# --------------------

# cohort.v1 = tables.bar.select_column("foo") == 42
v1 = Var(
    Map(
        PartialBinaryFunction(
            BinaryFunction.EQ,
            42),
        Select(Column("foo"), Table("bar", Dimension.PATIENT))))

# cohort.v2 = tables.bar.select_column("foo").is_not_null()
v2 = Var(
    Map(
        UnaryFunction.NOT_NULL,
        Select(Column("foo"), Table("bar", Dimension.PATIENT))))

# cohort.v3 = tables.bar.select_column("foo") == tables.bar.select_column("fumble")
v3 = Var(
    Combine(
        BinaryFunction.EQ,
        Select(Column("foo"), Table("bar", Dimension.PATIENT)),
        Select(Column("fumble"), Table("bar", Dimension.PATIENT))))

# cohort.v4 = tables.boo.filter(tables.boo.foible != "boink")
#                       .sort_by(tables.boo.zam).first_for_patient()
#                       .select_column(tables.boo.foo)
v4 = Var(Select(
    Column("foo"),
    Pick(
        Position.FIRST,
        Sort(
            Select(Column("zam"), Table("boo", Dimension.EVENT)),
            Filter(
                Map(
                    PartialBinaryFunction(BinaryFunction.NE, "boink"),
                    Select(Column("foible"), Table("boo", Dimension.EVENT))),
                Table("boo", Dimension.EVENT))))))

# last_covid_diagnosis = tables.events.filter(tables.events.code.is_in(covid_codelist))
#                                     .sort_by(tables.events.date).last_by_patient()
#                                     .select_column(date)
# cohort.covid_death = tables.patients.select_column("date_of_death") == last_covid_diagnosis
#
# I've written this out as a "denormalized" tree, but a graph could have reuse instead of duplication -- as long as
# our serialization format can handle it.
v5 = Var(Combine(
    BinaryFunction.EQ,
    Select(
        Column("l.date_of_death"),
        Join(
            Table("patients", Dimension.PATIENT),
            Pick(
                Position.LAST,
                Sort(
                    Select(Column("date"), Table("events", Dimension.EVENT)),
                    Filter(
                        Map(
                            PartialBinaryFunction(BinaryFunction.IN, CodeList({"a", "b"})),
                            Select(Column("code"), Table("events", Dimension.EVENT))),
                        Table("events", Dimension.EVENT)))))),
    Select(
        Column("r.date"),
        Join(
            Table("patients", Dimension.PATIENT),
            Pick(
                Position.LAST,
                Sort(
                    Select(Column("date"), Table("events", Dimension.EVENT)),
                    Filter(
                        Map(
                            PartialBinaryFunction(BinaryFunction.IN, CodeList({"a", "b"})),
                            Select(Column("code"), Table("events", Dimension.EVENT))),
                        Table("events", Dimension.EVENT))))))))
