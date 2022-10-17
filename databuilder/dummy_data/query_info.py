import dataclasses
from collections import defaultdict
from typing import Optional

from databuilder.query_model import (
    Function,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    Value,
    get_input_nodes,
    get_root_frame,
)


@dataclasses.dataclass
class ColumnInfo:
    """
    Captures information about a column as used in a particular dataset definition
    """

    name: str
    type: type  # NOQA: A003
    categories: Optional[tuple]
    values_used: set = dataclasses.field(default_factory=set)

    def __post_init__(self):
        if hasattr(self.type, "_primitive_type"):
            self.type = self.type._primitive_type()

    def record_value(self, value):
        if hasattr(value, "_to_primitive_type"):
            value = value._to_primitive_type()
        self.values_used.add(value)


@dataclasses.dataclass
class TableInfo:
    """
    Captures information about a table as used in a particular dataset definition
    """

    name: str
    has_one_row_per_patient: bool
    columns: dict[str, ColumnInfo] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class QueryInfo:
    """
    Captures information about a dataset definition, including the specific tables and
    columns used and the values expected in those columns
    """

    tables: dict[str, TableInfo]

    @classmethod
    def from_variable_definitions(cls, variable_definitions):
        all_nodes = walk_tree(*variable_definitions.values())
        by_type = get_nodes_by_type(all_nodes)

        tables = {
            # Create a TableInfo object …
            table.name: TableInfo(
                name=table.name,
                has_one_row_per_patient=isinstance(table, SelectPatientTable),
            )
            # … for every table used in the query (sorted for consistency)
            for table in sort_by_name(
                by_type[SelectTable] | by_type[SelectPatientTable]
            )
        }

        column_info_by_column: dict[SelectColumn, ColumnInfo] = {}

        # For every column used in the query (sorted for consistency) …
        for column in sort_by_name(by_type[SelectColumn]):
            table = get_root_frame(column.source)
            name = column.name
            table_info = tables[table.name]
            column_info = table_info.columns.get(name)
            if column_info is None:
                # … insert a ColumnInfo object into the appropriate table
                column_info = ColumnInfo(
                    name=name,
                    type=table.schema.get_column_type(name),
                    categories=table.schema.get_column_categories(name),
                )
                table_info.columns[name] = column_info
            # Record the ColumnInfo object associated with each SelectColumn node
            column_info_by_column[column] = column_info

        # Record values used in equality and substring comparisons
        for node in by_type[Function.EQ] | by_type[Function.StringContains]:
            # The query model in theory supports "1 == x" style comparisons (i.e.  with
            # the column on the RHS) but there's no way to generate such constructions
            # using ehrQL so we only bother handling the "x == 1" orientation here.
            if not (isinstance(node.lhs, SelectColumn) and isinstance(node.rhs, Value)):
                continue
            column_info = column_info_by_column[node.lhs]
            column_info.record_value(node.rhs.value)

        # Record values used in containment comparisons
        for node in by_type[Function.In]:
            if not (isinstance(node.lhs, SelectColumn) and isinstance(node.rhs, Value)):
                continue
            column_info = column_info_by_column[node.lhs]
            for value in node.rhs.value:
                column_info.record_value(value)

        return cls(tables=tables)


def get_nodes_by_type(nodes):
    by_type = defaultdict(set)
    for node in nodes:
        by_type[type(node)].add(node)
    return by_type


def walk_tree(*nodes):
    for node in nodes:
        yield node
        yield from walk_tree(*get_input_nodes(node))


def sort_by_name(iterable):
    return sorted(iterable, key=lambda i: i.name)
