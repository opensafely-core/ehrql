import datetime
import operator

from databuilder import query_model as qm
from databuilder.query_engines.base import BaseQueryEngine

from .database import PatientColumn, PatientTable, apply_function, handle_null

T = True
F = False
N = None


class InMemoryQueryEngine(BaseQueryEngine):
    """A query engine for use in tests.

    Along with the in-memory database, this is intended to support fast query language
    tests, and a to provide a reference implementation for other engines.
    """

    def get_results(self, variable_definitions):
        name_to_col = {
            "patient_id": PatientColumn(
                {patient: patient for patient in self.all_patients},
                default=None,
            )
        }

        for name, node in variable_definitions.items():
            col = self.visit(node)
            assert isinstance(col, PatientColumn)
            name_to_col[name] = col

        table = PatientTable(name_to_col)
        table = table.filter(table["population"])

        for record in table.to_records():
            del record["population"]
            yield record

    @property
    def database(self):
        # Hack!  When other engine classes are instantiated, they are passed the URL to
        # a database to connect to.  Since our database is just an object in our
        # process, we instantiate this engine with an instance of the database.  See
        # InMemoryDatabase.host_url.
        return self.dsn

    @property
    def tables(self):
        return self.database.tables

    @property
    def all_patients(self):
        return self.database.all_patients

    def visit(self, node):
        visitor = getattr(self, f"visit_{type(node).__name__}")
        return visitor(node)

    def visit_Code(self, node):
        assert False

    def visit_Value(self, node):
        if isinstance(node.value, frozenset):
            value = frozenset(self.convert_value(v) for v in node.value)
        else:
            value = self.convert_value(node.value)
        return PatientColumn(
            {patient: value for patient in self.all_patients},
            default=None,
        )

    def convert_value(self, value):
        if hasattr(value, "_to_primitive_type"):
            return value._to_primitive_type()
        else:
            return value

    def visit_SelectTable(self, node):
        return self.tables[node.name]

    def visit_SelectPatientTable(self, node):
        return self.tables[node.name]

    def visit_SelectColumn(self, node):
        return self.visit(node.source)[node.name]

    def visit_Filter(self, node):
        return self.visit(node.source).filter(self.visit(node.condition))

    def visit_Sort(self, node):
        source = self.visit(node.source)
        sort_index = self.visit(node.sort_by).sort_index()
        return source.sort(sort_index)

    def visit_PickOneRowPerPatient(self, node):
        ix = {
            qm.Position.FIRST: 0,
            qm.Position.LAST: -1,
        }[node.position]
        return self.visit(node.source).pick_at_index(ix)

    def visit_Exists(self, node):
        return self.visit(node.source).exists()

    def visit_Count(self, node):
        return self.visit(node.source).count()

    def visit_Min(self, node):
        col = self.visit(node.source)
        return col.aggregate_values(min, default=None)

    def visit_Max(self, node):
        col = self.visit(node.source)
        return col.aggregate_values(max, default=None)

    def visit_Sum(self, node):
        col = self.visit(node.source)
        return col.aggregate_values(sum, default=None)

    def visit_CombineAsSet(self, node):
        assert False

    def visit_unary_op(self, node, op):
        series = self.visit(node.source)
        return apply_function(op, series)

    def visit_unary_op_with_null(self, node, op):
        return self.visit_unary_op(node, handle_null(op))

    def visit_binary_op(self, node, op):
        lhs = self.visit(node.lhs)
        rhs = self.visit(node.rhs)
        return apply_function(op, lhs, rhs)

    def visit_binary_op_with_null(self, node, op):
        return self.visit_binary_op(node, handle_null(op))

    def visit_EQ(self, node):
        return self.visit_binary_op_with_null(node, operator.eq)

    def visit_NE(self, node):
        return self.visit_binary_op_with_null(node, operator.ne)

    def visit_LT(self, node):
        return self.visit_binary_op_with_null(node, operator.lt)

    def visit_LE(self, node):
        return self.visit_binary_op_with_null(node, operator.le)

    def visit_GT(self, node):
        return self.visit_binary_op_with_null(node, operator.gt)

    def visit_GE(self, node):
        return self.visit_binary_op_with_null(node, operator.ge)

    def visit_And(self, node):
        def op(lhs, rhs):
            return {
                (T, T): T,
                (T, N): N,
                (T, F): F,
                (N, T): N,
                (N, N): N,
                (N, F): F,
                (F, T): F,
                (F, N): F,
                (F, F): F,
            }[lhs, rhs]

        return self.visit_binary_op(node, op)

    def visit_Or(self, node):
        def op(lhs, rhs):
            return {
                (T, T): T,
                (T, N): T,
                (T, F): T,
                (N, T): T,
                (N, N): N,
                (N, F): N,
                (F, T): T,
                (F, N): N,
                (F, F): F,
            }[lhs, rhs]

        return self.visit_binary_op(node, op)

    def visit_Not(self, node):
        def op(value):
            return {
                T: F,
                N: N,
                F: T,
            }[value]

        return self.visit_unary_op(node, op)

    def visit_IsNull(self, node):
        def op(value):
            return value is None

        return self.visit_unary_op(node, op)

    def visit_Negate(self, node):
        return self.visit_unary_op_with_null(node, operator.neg)

    def visit_Add(self, node):
        return self.visit_binary_op_with_null(node, operator.add)

    def visit_Subtract(self, node):
        return self.visit_binary_op_with_null(node, operator.sub)

    def visit_CastToInt(self, node):
        return self.visit_unary_op_with_null(node, int)

    def visit_CastToFloat(self, node):
        return self.visit_unary_op_with_null(node, float)

    def visit_DateAddDays(self, node):
        def date_add_days(date, num_days):
            return date + datetime.timedelta(days=num_days)

        return self.visit_binary_op_with_null(node, date_add_days)

    def visit_DateDifferenceInYears(self, node):
        def year_diff(start, end):
            year_diff = end.year - start.year
            if (end.month, end.day) < (start.month, start.day):
                return year_diff - 1
            else:
                return year_diff

        return self.visit_binary_op_with_null(node, year_diff)

    def visit_YearFromDate(self, node):
        return self.visit_unary_op_with_null(node, operator.attrgetter("year"))

    def visit_MonthFromDate(self, node):
        return self.visit_unary_op_with_null(node, operator.attrgetter("month"))

    def visit_DayFromDate(self, node):
        return self.visit_unary_op_with_null(node, operator.attrgetter("day"))

    def visit_ToFirstOfYear(self, node):
        def to_first_of_year(date):
            return date.replace(day=1, month=1)

        return self.visit_unary_op_with_null(node, to_first_of_year)

    def visit_ToFirstOfMonth(self, node):
        def to_first_of_month(date):
            return date.replace(day=1)

        return self.visit_unary_op_with_null(node, to_first_of_month)

    def visit_StringContains(self, node):
        return self.visit_binary_op_with_null(node, operator.contains)

    def visit_In(self, node):
        def op(lhs, rhs):
            return lhs in rhs

        return self.visit_binary_op_with_null(node, op)

    def visit_Case(self, node):
        cases = [
            (self.visit(condition), self.visit(value))
            for condition, value in node.cases.items()
        ]
        if node.default is None:
            default = PatientColumn({}, None)
        else:
            default = self.visit(node.default)
        # Flatten arguments into a single list for easier handling
        arguments = [default, *[i for pair in cases for i in pair]]
        return apply_function(case_flattened, *arguments)


def case_flattened(default, *cases):
    """
    Implements CASE WHEN x THEN y ELSE x END logic but takes its arguments in a
    flattened form:

        default, condition_1, value_1, condition_2, value_2, ... condition_N, value_N

    This means it can be passed directly to `apply_function_to_columns` without needing
    to do any special argument handling.
    """
    for condition, value in zip(cases[::2], cases[1::2]):
        if condition:
            return value
    return default
