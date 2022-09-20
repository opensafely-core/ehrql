import dataclasses
from functools import singledispatch
from typing import Optional, TypeVar

from databuilder.query_model import (
    AggregateByPatient,
    SelectColumn,
    get_root_frame,
    get_series_type,
)

T = TypeVar("T")


@dataclasses.dataclass(frozen=True)
class ColumnSpec:
    type: type[T]  # noqa: A003
    nullable: bool = True
    categories: Optional[tuple[T]] = None


def get_column_specs(variable_definitions):
    """
    Given a dict of variable definitions return a dict of ColumnSpec objects, given the
    types (and other associated metadata) of all the columns in the output
    """
    # TODO: It may not be universally true that IDs are ints. Internally the EMIS IDs
    # are SHA512 hashes stored as hex strings which we convert to ints. But we can't
    # guarantee always to be able to pull this trick.
    column_specs = {"patient_id": ColumnSpec(int, nullable=False)}
    for name, series in variable_definitions.items():
        if name == "population":
            continue
        type_ = get_series_type(series)
        categories = get_categories(series)
        if hasattr(type_, "_primitive_type"):
            type_ = type_._primitive_type()
            if categories:
                categories = tuple(c._to_primitive_type() for c in categories)
        column_specs[name] = ColumnSpec(type_, nullable=True, categories=categories)
    return column_specs


@singledispatch
def get_categories(series):
    # As a default, we assume that operations destroy category information and then
    # define specific implementations for operations which preserve categories
    return None


@get_categories.register(SelectColumn)
def get_categories_for_select_column(series):
    # When selecting a column we can ask the underlying table schema for the
    # corresponding categories
    root = get_root_frame(series.source)
    return root.schema.get_column_categories(series.name)


@get_categories.register(AggregateByPatient.Min)
@get_categories.register(AggregateByPatient.Max)
def get_categories_for_min_max(series):
    # The min/max aggregations preserve the categories of their inputs
    return get_categories(series.source)
