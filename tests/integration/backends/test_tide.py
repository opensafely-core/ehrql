from datetime import date

import sqlalchemy

from ehrql.backends.tide import TIDEBackend
from ehrql.query_engines.mssql_dialect import SelectStarInto
from ehrql.tables import tide
from tests.lib.tide_schema import (
    Assessments,
    Pupils,
)

from .helpers import (
    assert_tests_exhaustive,
    assert_types_correct,
    get_all_backend_columns,
    register_test_for,
)


def test_backend_columns_have_correct_types(mssql_database):
    columns_with_types = get_all_backend_columns_with_types(mssql_database)
    assert_types_correct(columns_with_types, mssql_database)


def get_all_backend_columns_with_types(mssql_database):
    """
    For every column on every table we expose in the backend, yield the SQLAlchemy type
    instance we expect to use for that column together with the type information that
    database has for that column so we can check they're compatible
    """
    table_names = set()
    column_types = {}
    queries = []
    for table, columns in get_all_backend_columns(TIDEBackend()):
        table_names.add(table)
        column_types.update({(table, c.key): c.type for c in columns})
        # Construct a query which selects every column in the table
        select_query = sqlalchemy.select(*[c.label(c.key) for c in columns])
        # Write the results of that query into a temporary table (it will be empty but
        # that's fine, we just want the types)
        temp_table = sqlalchemy.table(f"#{table}")
        queries.append(SelectStarInto(temp_table, select_query.alias()))
    # Create all the underlying tables in the database without populating them
    mssql_database.setup(metadata=Pupils.metadata)
    with mssql_database.engine().connect() as connection:
        # Create our temporary tables
        for query in queries:
            connection.execute(query)
        # Get the column names, types and collations for all columns in those tables
        query = sqlalchemy.text(
            """
            SELECT
                -- MSSQL does some nasty name mangling involving underscores to make
                -- local temporary table names globally unique. We undo that here.
                SUBSTRING(t.name, 2, CHARINDEX('__________', t.name) - 2) AS [table],
                c.name AS [column],
                y.name AS [type_name],
                c.collation_name AS [collation]
            FROM
                tempdb.sys.columns c
            JOIN
                tempdb.sys.objects t ON t.object_id = c.object_id
            JOIN
                tempdb.sys.types y ON y.user_type_id = c.user_type_id
            WHERE
                t.type_desc = 'USER_TABLE'
                AND CHARINDEX('__________', t.name) > 0
            """
        )
        results = list(connection.execute(query))
    for table, column, type_name, collation in results:
        # Ignore any leftover cruft in the database
        if table not in table_names:  # pragma: no cover
            continue
        column_type = column_types[table, column]
        column_args = {"type": type_name, "collation": collation}
        yield table, column, column_type, column_args


@register_test_for(tide.pupils)
def test_pupils(select_all_tide):
    results = select_all_tide(
        Pupils(
            pupil_id=1,
            mat_id="MAT001",
            gender="female",
            date_of_birth=date(2010, 1, 1),
            eal=True,
            send=False,
            pupil_premium=True,
            attendance=95,
        ),
        Pupils(
            pupil_id=2,
            mat_id="MAT002",
            gender="male",
            date_of_birth=date(2011, 3, 1),
            eal=False,
            send=True,
            pupil_premium=False,
            attendance=87,
        ),
        Pupils(
            pupil_id=3,
            mat_id="MAT001",
            gender="unknown",
            date_of_birth=date(2009, 12, 1),
            eal=None,
            send=None,
            pupil_premium=None,
            attendance=None,
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "mat_id": "MAT001",
            "gender": "female",
            "date_of_birth": date(2010, 1, 1),
            "eal": True,
            "send": False,
            "pupil_premium": True,
            "attendance": 95,
        },
        {
            "patient_id": 2,
            "mat_id": "MAT002",
            "gender": "male",
            "date_of_birth": date(2011, 3, 1),
            "eal": False,
            "send": True,
            "pupil_premium": False,
            "attendance": 87,
        },
        {
            "patient_id": 3,
            "mat_id": "MAT001",
            "gender": "unknown",
            "date_of_birth": date(2009, 12, 1),
            "eal": None,
            "send": None,
            "pupil_premium": None,
            "attendance": None,
        },
    ]


@register_test_for(tide.assessments)
def test_assessments(select_all_tide):
    results = select_all_tide(
        Pupils(
            pupil_id=1,
            mat_id="MAT001",
            gender="female",
            date_of_birth=date(2010, 1, 1),
        ),
        Pupils(
            pupil_id=2,
            mat_id="MAT002",
            gender="male",
            date_of_birth=date(2011, 3, 1),
        ),
        Assessments(
            pupil_id=1,
            date=date(2023, 6, 15),
            teacher_id="T001",
            subject="Mathematics",
            result=85.5,
        ),
        Assessments(
            pupil_id=1,
            date=date(2023, 7, 10),
            teacher_id="T002",
            subject="English",
            result=92.0,
        ),
        Assessments(
            pupil_id=2,
            date=date(2023, 6, 15),
            teacher_id="T001",
            subject="Mathematics",
            result=78.5,
        ),
        Assessments(
            pupil_id=2,
            date=date(2023, 8, 5),
            teacher_id="T003",
            subject="Science",
            result=None,
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "date": date(2023, 6, 15),
            "teacher_id": "T001",
            "subject": "Mathematics",
            "result": 85.5,
        },
        {
            "patient_id": 1,
            "date": date(2023, 7, 10),
            "teacher_id": "T002",
            "subject": "English",
            "result": 92.0,
        },
        {
            "patient_id": 2,
            "date": date(2023, 6, 15),
            "teacher_id": "T001",
            "subject": "Mathematics",
            "result": 78.5,
        },
        {
            "patient_id": 2,
            "date": date(2023, 8, 5),
            "teacher_id": "T003",
            "subject": "Science",
            "result": None,
        },
    ]


def test_registered_tests_are_exhaustive():
    assert_tests_exhaustive(TIDEBackend())
