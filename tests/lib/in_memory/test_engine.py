import sqlalchemy

from databuilder.query_model import Function, SelectColumn, SelectPatientTable, Value
from tests.lib.in_memory import InMemoryDatabase, InMemoryQueryEngine
from tests.lib.mock_backend import Base, PatientLevelTable, backend_factory, next_id

# End-to-end acceptance tests for the in-memory query engine.
#
# These are not intended to be exhaustive, just to verify some difficult cases that earlier versions had trouble
# with. Exhaustive testing is provided by the specc and by the comparison with the other query engines in the
# generative tests.


def test_nested_unary_operations():
    # This tower of unary functions drove out the existing implementation for joins and consequent null handling.
    query = {
        "v": Function.EQ(
            lhs=SelectColumn(
                source=SelectPatientTable(
                    name="patient_level_table",
                ),
                name="b1",
            ),
            rhs=Function.IsNull(
                source=Function.Not(
                    source=Function.IsNull(
                        source=SelectColumn(
                            source=SelectPatientTable(
                                name="patient_level_table1",
                            ),
                            name="i1",
                        )
                    )
                )
            ),
        ),
        "population": Value(True),
    }

    d = InMemoryDatabase()
    d.setup(PatientLevelTable(PatientId=1, b1=False), PatientLevelTable1(PatientId=2))

    e = InMemoryQueryEngine(query, backend_factory(InMemoryQueryEngine)(d.host_url()))
    with e.execute_query() as results:
        print(results)
        results = list(results)
        assert len(results) == 2
        assert results[0]["v"] is True
        assert results[1]["v"] is None


def test_universe_only_includes_patients_in_mentioned_tables():
    # A patient in an unused table should not appear in the results.
    query = {
        "v": SelectColumn(
            source=SelectPatientTable(
                name="patient_level_table",
            ),
            name="i1",
        ),
        "population": Value(True),
    }

    d = InMemoryDatabase()
    d.setup(PatientLevelTable(PatientId=1, i1=0), PatientLevelTable1(PatientId=2))

    e = InMemoryQueryEngine(query, backend_factory(InMemoryQueryEngine)(d.host_url()))
    with e.execute_query() as results:
        print(results)
        results = list(results)
        assert len(results) == 1
        assert results[0]["v"] == 0


class PatientLevelTable1(Base):
    __tablename__ = "patient_level_table1"
    Id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, default=next_id)
    PatientId = sqlalchemy.Column(sqlalchemy.Integer)
    i1 = sqlalchemy.Column(sqlalchemy.Integer)
    i2 = sqlalchemy.Column(sqlalchemy.Integer)
    b1 = sqlalchemy.Column(sqlalchemy.Boolean)
    b2 = sqlalchemy.Column(sqlalchemy.Boolean)
