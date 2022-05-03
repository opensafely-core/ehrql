import contextlib
import operator

from databuilder import query_model as qm
from databuilder.query_engines.base import BaseQueryEngine

from .database import Column, Table

T = True
F = False
N = None


class InMemoryQueryEngine(BaseQueryEngine):
    """A query engine for use in tests.

    Along with the in-memory database, this is intended to support fast query language
    tests, and a to provide a reference implementation for other engines.
    """

    @contextlib.contextmanager
    def execute_query(self):
        name_to_col = {
            "patient_id": Column(
                {patient: [patient] for patient in self.all_patients},
                default=None,
            )
        }

        for name, node in self.column_definitions.items():
            col = self.visit(node)
            assert not col.any_patient_has_multiple_values()
            name_to_col[name] = col

        table = Table(name_to_col)
        table = table.filter(table["population"])
        records = []
        for record in table.to_records():
            del record["population"]
            records.append(record)

        yield records

    @property
    def database(self):
        # Hack!  When other engine classes are instantiated, they are passed the URL to
        # a database to connect to.  Since our database is just an object in our
        # process, we instantiate this engine with an instance of the database.  See
        # InMemoryDatabase.host_url.
        return self.backend.database_url

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
        return Column(
            {patient: [node.value] for patient in self.all_patients},
            default=None,
        )

    def visit_SelectTable(self, node):
        return self.tables[node.name]

    def visit_SelectPatientTable(self, node):
        return self.tables[node.name]

    def visit_SelectColumn(self, node):
        return self.visit(node.source)[node.name]

    def visit_Filter(self, node):
        return self.visit(node.source).filter(self.visit(node.condition))

    def visit_Sort(self, node):
        sort_index = self.visit(node.sort_by).sort_index()
        return self.visit(node.source).sort(sort_index)

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
        assert False

    def visit_Max(self, node):
        assert False

    def visit_Sum(self, node):
        col = self.visit(node.source)
        return col.aggregate_values(sum, None)

    def visit_CombineAsSet(self, node):
        assert False

    def visit_unary_op_with_null(self, node, op):
        series = self.visit(node.source)
        return series.unary_op_with_null(op)

    def visit_binary_op_with_null(self, node, op):
        lhs = self.visit(node.lhs)
        rhs = self.visit(node.rhs)
        return lhs.binary_op_with_null(op, rhs)

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

        lhs = self.visit(node.lhs)
        rhs = self.visit(node.rhs)
        return lhs.binary_op(op, rhs)

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

        lhs = self.visit(node.lhs)
        rhs = self.visit(node.rhs)
        return lhs.binary_op(op, rhs)

    def visit_Not(self, node):
        def op(value):
            return {
                T: F,
                N: N,
                F: T,
            }[value]

        return self.visit(node.source).unary_op(op)

    def visit_IsNull(self, node):
        def op(value):
            return value is None

        return self.visit(node.source).unary_op(op)

    def visit_Negate(self, node):
        return self.visit_unary_op_with_null(node, operator.neg)

    def visit_Add(self, node):
        return self.visit_binary_op_with_null(node, operator.add)

    def visit_Subtract(self, node):
        return self.visit_binary_op_with_null(node, operator.sub)

    def visit_RoundToFirstOfMonth(self, node):
        assert False

    def visit_RoundToFirstOfYear(self, node):
        assert False

    def visit_DateAdd(self, node):
        assert False

    def visit_DateSubtract(self, node):
        assert False

    def visit_DateDifferenceInYears(self, node):
        assert False

    def visit_YearFromDate(self, node):
        assert False

    def visit_In(self, node):
        assert False

    def visit_Categorise(self, node):
        assert False
