from datetime import date

import pytest
import sqlalchemy

from databuilder.backends.tpp import TPPBackend
from databuilder.query_model import TableSchema
from tests.lib.tpp_schema import apcs, patient


def run_query(database, query):
    with database.engine().connect() as cursor:
        yield from cursor.execute(query)


@pytest.mark.parametrize(
    "raw, codes",
    [
        ("flim", ["flim"]),
        ("flim ,flam ,flum", ["flim", "flam", "flum"]),
        ("flim ||flam ||flum", ["flim", "flam", "flum"]),
        ("abc ,def ||ghi ,jkl", ["abc", "def", "ghi", "jkl"]),
        ("ABCX ,XYZ ,OXO", ["ABC", "XYZ", "OXO"]),
    ],
    ids=[
        "returns a single code",
        "returns multiple space comma separated codes",
        "returns multiple space double pipe separated codes",
        "copes with comma pipe combinations",
        "strips just trailing xs",
    ],
)
def test_hospitalization_table_code_conversion(mssql_database, raw, codes):
    mssql_database.setup(
        patient(
            related=[apcs(codes=raw)],
        )
    )

    table = TPPBackend.hospitalizations.get_expression(
        "hospitalizations", TableSchema(code=str)
    )
    query = sqlalchemy.select(table.c.code)

    results = list(run_query(mssql_database, query))

    # Because of the way that we split the raw codes, the order in which they are returned is not the same as the order
    # they appear in the table.
    assert len(results) == len(codes)
    assert {r[0] for r in results} == set(codes)


def test_patients_contract_table(mssql_database):
    mssql_database.setup(
        patient(1, "M", "1990-01-01", date_of_death="2021-01-04"),
        patient(2, "F", "1990-01-01", date_of_death="2020-02-04"),
        patient(3, "I", "1990-01-01", date_of_death="9999-12-31"),
        patient(4, None, "1990-01-01"),
        patient(5, "X", "1990-01-01"),
    )

    table = TPPBackend.patients.get_expression(
        "patients", TableSchema(date_of_birth=date, date_of_death=date, sex=str)
    )
    query = sqlalchemy.select(
        table.c.patient_id, table.c.date_of_birth, table.c.date_of_death, table.c.sex
    )

    results = list(run_query(mssql_database, query))
    assert results == [
        (1, date(1990, 1, 1), date(2021, 1, 1), "male"),
        (2, date(1990, 1, 1), date(2020, 2, 1), "female"),
        (3, date(1990, 1, 1), None, "intersex"),
        (4, date(1990, 1, 1), None, "unknown"),
        (5, date(1990, 1, 1), None, "unknown"),
    ]
