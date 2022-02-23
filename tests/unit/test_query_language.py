from datetime import date

import pytest

from databuilder.query_language import compile  # noqa A003
from databuilder.query_language import (
    Dataset,
    DateSeries,
    IdSeries,
    IntSeries,
    build_patient_table,
)
from databuilder.query_model import (
    Function,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    TableSchema,
    Value,
)

patients = build_patient_table(
    "patients",
    {
        "patient_id": IdSeries,
        "date_of_birth": DateSeries,
    },
)


def test_dataset():
    year_of_birth = patients.date_of_birth.year
    dataset = Dataset()
    dataset.set_population(year_of_birth <= 2000)
    dataset.year_of_birth = year_of_birth

    assert compile(dataset) == {
        "year_of_birth": Function.YearFromDate(
            source=SelectColumn(
                name="date_of_birth", source=SelectPatientTable("patients")
            )
        ),
        "population": Function.LE(
            lhs=Function.YearFromDate(
                source=SelectColumn(
                    name="date_of_birth", source=SelectPatientTable("patients")
                )
            ),
            rhs=Value(2000),
        ),
    }


# The problem: We'd like to test that operations on query language (QL) elements return
# the correct query model (QM) elements. We like tests that emphasise what is being
# tested, and de-emphasise the scaffolding. We dislike test code that looks like
# production code.

# We'd like Series objects with specific "inner" types. How these Series objects are
# instantiated isn't important.
qm_table = SelectTable(
    name="table",
    schema=TableSchema(int_column=int, date_column=date),
)
qm_int_series = SelectColumn(source=qm_table, name="int_column")
qm_date_series = SelectColumn(source=qm_table, name="date_column")


def assert_produces(ql_element, qm_element):
    assert ql_element.qm_node == qm_element


class TestIntSeries:
    def test_le_value(self):
        assert_produces(
            IntSeries(qm_int_series) <= 2000,
            Function.LE(qm_int_series, Value(2000)),
        )

    def test_le_value_reverse(self):
        assert_produces(
            2000 >= IntSeries(qm_int_series),
            Function.LE(qm_int_series, Value(2000)),
        )

    @pytest.mark.xfail(reason="LE comparison with IntSeries not supported")
    def test_le_intseries(self):
        assert_produces(
            IntSeries(qm_int_series) <= IntSeries(qm_int_series),
            Function.LE(qm_int_series, qm_int_series),
        )


class TestDateSeries:
    def test_year(self):
        assert_produces(
            DateSeries(qm_date_series).year, Function.YearFromDate(qm_date_series)
        )
