import dataclasses
from collections import defaultdict
from datetime import date, timedelta
from functools import cached_property, lru_cache

from ehrql.query_model.introspection import all_unique_nodes, get_table_nodes
from ehrql.query_model.nodes import (
    Column,
    Function,
    InlinePatientTable,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    TableSchema,
    Value,
    get_root_frame,
)
from ehrql.query_model.table_schema import Constraint


@dataclasses.dataclass
class ColumnInfo:
    """
    Captures information about a column as used in a particular dataset definition
    """

    name: str
    type: type  # NOQA: A003
    constraints: tuple = ()
    _values_used: set = dataclasses.field(default_factory=set)

    @classmethod
    def from_column(cls, name, column, extra_constraints=()):
        type_ = column.type_
        if hasattr(type_, "_primitive_type"):
            type_ = type_._primitive_type()
        return cls(
            name,
            type_,
            constraints=normalize_constraints(
                tuple(column.constraints) + tuple(extra_constraints)
            ),
        )

    def __post_init__(self):
        self._constraints_by_type = {type(c): c for c in self.constraints}

    def record_value(self, value):
        if hasattr(value, "_to_primitive_type"):
            value = value._to_primitive_type()
        self._values_used.add(value)

    @cached_property
    def values_used(self):
        return sorted(self._values_used)

    def get_constraint(self, type_):
        return self._constraints_by_type.get(type_)


@dataclasses.dataclass
class TableInfo:
    """
    Captures information about a table as used in a particular dataset definition
    """

    name: str
    has_one_row_per_patient: bool
    columns: dict[str, ColumnInfo] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_table(cls, table):
        return cls(
            name=table.name,
            has_one_row_per_patient=isinstance(table, SelectPatientTable),
        )

    @cached_property
    def table_node(self):
        """
        Return a query model table node whose schema contains just the subset of the
        original schema which is actually used in the query
        """
        cls = {False: SelectTable, True: SelectPatientTable}[
            self.has_one_row_per_patient
        ]
        schema = TableSchema(
            **{
                col_info.name: Column(col_info.type, constraints=col_info.constraints)
                for col_info in self.columns.values()
            }
        )
        return cls(self.name, schema=schema)


@dataclasses.dataclass
class QueryInfo:
    """
    Captures information about a dataset definition, including the specific tables and
    columns used and the values expected in those columns
    """

    tables: dict[str, TableInfo]
    population_table_names: list[str]
    other_table_names: list[str]

    @classmethod
    def from_variable_definitions(cls, variable_definitions):
        all_nodes = all_unique_nodes(*variable_definitions.values())
        by_type = get_nodes_by_type(all_nodes)

        extra_constraints = query_to_column_constraints(
            variable_definitions["population"]
        )

        tables = {
            # Create a TableInfo object …
            table.name: TableInfo.from_table(table)
            # … for every table used in the query (sorted for consistency)
            for table in sort_by_name(
                by_type[SelectTable] | by_type[SelectPatientTable]
            )
        }

        column_info_by_column: dict[SelectColumn, ColumnInfo] = {}

        # For every column used in the query (sorted for consistency) …
        for column in sort_by_name(by_type[SelectColumn]):
            table = get_root_frame(column.source)
            # We're only interested in "standard" tables here
            if isinstance(table, InlinePatientTable):
                continue
            elif isinstance(table, SelectTable | SelectPatientTable):
                pass
            else:
                assert False
            name = column.name
            table_info = tables[table.name]
            column_info = table_info.columns.get(name)
            if column_info is None:
                # … insert a ColumnInfo object into the appropriate table
                column_info = ColumnInfo.from_column(
                    name,
                    table.schema.get_column(name),
                    extra_constraints=extra_constraints.get(column, ()),
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
            if column_info := column_info_by_column.get(node.lhs):
                column_info.record_value(node.rhs.value)

        # Record values used in containment comparisons
        for node in by_type[Function.In]:
            if not (isinstance(node.lhs, SelectColumn) and isinstance(node.rhs, Value)):
                continue
            if column_info := column_info_by_column.get(node.lhs):
                for value in node.rhs.value:
                    column_info.record_value(value)

        # Record which tables are used in determining population membership and which
        # are not
        population_table_names = {
            node.name for node in get_table_nodes(variable_definitions["population"])
        }

        other_table_names = tables.keys() - population_table_names

        return cls(
            tables=tables,
            population_table_names=sorted(population_table_names),
            other_table_names=sorted(other_table_names),
        )


def get_nodes_by_type(nodes):
    by_type = defaultdict(set)
    for node in nodes:
        by_type[type(node)].add(node)
    return by_type


def sort_by_name(iterable):
    return sorted(iterable, key=lambda i: i.name)


@lru_cache
def query_to_column_constraints(query):
    """Converts a query (typically a population definition) into
    constraints that would have to be applied to a record in order
    to satisfy it."""
    match query:
        case Function.And(lhs=lhs, rhs=rhs):
            left = query_to_column_constraints(lhs)
            right = query_to_column_constraints(rhs)
            keys = set(left) | set(right)
            return {k: left.get(k, []) + right.get(k, []) for k in keys}
        case Function.Or(lhs=lhs, rhs=rhs):
            left = query_to_column_constraints(lhs)
            right = query_to_column_constraints(rhs)
            result = {}
            for k, v in left.items():
                try:
                    result[k] = list(set(v) & set(right[k]))
                except KeyError:
                    pass
            for k, v in list(result.items()):
                if not v:
                    del result[k]
            return result
        case Function.EQ(
            lhs=SelectColumn() as lhs,
            rhs=Value(value=value),
        ):
            return {lhs: [Constraint.Categorical(values=(value,))]}
        case Function.EQ(
            lhs=Function.YearFromDate(source=SelectColumn() as column),
            rhs=Value(value=year),
        ):
            return {
                column: [
                    Constraint.GeneralRange(
                        minimum=date(year, 1, 1),
                        maximum=date(year, 12, 31),
                    )
                ]
            }
        case Function.In(
            lhs=SelectColumn() as lhs,
            rhs=Value(value=values),
        ):
            return {lhs: [Constraint.Categorical(values=values)]}
        case Function.GE(
            lhs=Function.DateDifferenceInYears(
                lhs=Value(value=reference_date), rhs=column
            ),
            rhs=Value(value=difference),
        ):
            return {
                column: [
                    Constraint.GeneralRange(
                        maximum=reference_date - timedelta(days=365 * difference)
                    )
                ]
            }
        case Function.LE(
            lhs=Function.DateDifferenceInYears(
                lhs=Value(value=reference_date), rhs=column
            ),
            rhs=Value(value=difference),
        ):
            return {
                column: [
                    Constraint.GeneralRange(
                        minimum=reference_date.replace(
                            year=reference_date.year - difference
                        )
                    )
                ]
            }
        case Function.LT(
            lhs=Function.DateAddYears(
                lhs=SelectColumn() as column,
                rhs=Value(value=difference),
            ),
            rhs=Value(value=reference_date),
        ):
            return {
                column: [
                    Constraint.GeneralRange(
                        maximum=reference_date.replace(
                            year=reference_date.year - difference
                        ),
                        includes_maximum=False,
                    )
                ]
            }
        case Function.GT(lhs=SelectColumn() as column, rhs=Value(value=min_value)):
            return {
                column: [
                    Constraint.GeneralRange(minimum=min_value, includes_minimum=False)
                ]
            }
        case Function.GE(lhs=SelectColumn() as column, rhs=Value(value=min_value)):
            return {
                column: [
                    Constraint.GeneralRange(minimum=min_value, includes_minimum=True)
                ]
            }
        case Function.LT(lhs=SelectColumn() as column, rhs=Value(value=max_value)):
            return {
                column: [
                    Constraint.GeneralRange(maximum=max_value, includes_maximum=False)
                ]
            }
        case Function.LE(lhs=SelectColumn() as column, rhs=Value(value=max_value)):
            return {
                column: [
                    Constraint.GeneralRange(maximum=max_value, includes_maximum=True)
                ]
            }
        case Function.IsNull(source=SelectColumn() as column):
            return {column: [Constraint.NotNull()]}

    return {}


def normalize_constraints(constraints):
    group_by_type = defaultdict(list)
    for constraint in constraints:
        group_by_type[type(constraint)].append(constraint)
    if len(group_by_type[Constraint.Categorical]) > 1:
        constraint, *rest = group_by_type[Constraint.Categorical]
        for more in rest:
            constraint = Constraint.Categorical(
                values=set(constraint.values) & set(more.values)
            )
        group_by_type[Constraint.Categorical] = [constraint]
    if len(ranges := group_by_type[Constraint.GeneralRange]) > 1:
        minimum = None
        maximum = None
        for r in ranges:
            if minimum is None:
                minimum = r.minimum
            elif r.minimum is not None:
                minimum = max(minimum, r.minimum)
            if maximum is None:
                maximum = r.maximum
            elif r.maximum is not None:
                maximum = min(maximum, r.maximum)

        includes_minimum = minimum is None or all(r.validate(minimum) for r in ranges)
        includes_maximum = maximum is None or all(r.validate(maximum) for r in ranges)
        group_by_type[Constraint.GeneralRange] = [
            Constraint.GeneralRange(
                minimum=minimum,
                maximum=maximum,
                includes_maximum=includes_maximum,
                includes_minimum=includes_minimum,
            )
        ]

    return tuple(
        [constraint for group in group_by_type.values() for constraint in group]
    )
