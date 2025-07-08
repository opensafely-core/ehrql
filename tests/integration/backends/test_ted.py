from datetime import date

import sqlalchemy

from ehrql.backends.ted import TEDBackend
from ehrql.query_engines.mssql_dialect import SelectStarInto
from ehrql.tables import ted
from tests.lib.ted_schema import (
    Assessments,
    AttainmentResults,
    Classes,
    Students,
    TeacherClassAllocation,
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
    for table, columns in get_all_backend_columns(TEDBackend()):
        table_names.add(table)
        column_types.update({(table, c.key): c.type for c in columns})
        # Construct a query which selects every column in the table
        select_query = sqlalchemy.select(*[c.label(c.key) for c in columns])
        # Write the results of that query into a temporary table (it will be empty but
        # that's fine, we just want the types)
        temp_table = sqlalchemy.table(f"#{table}")
        queries.append(SelectStarInto(temp_table, select_query.alias()))
    # Create all the underlying tables in the database without populating them
    mssql_database.setup(metadata=Students.metadata)
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


@register_test_for(ted.students)
def test_students(select_all_ted):
    results = select_all_ted(
        Students(
            Student_ID=1,
            MAT_ID="MAT001",
            School_ID="SCH001",
            Cohort="Y7",
            Gender="M",
            KS2_maths=85.5,
            KS2_reading=78.0,
            CAT_test=110.0,
            Reading_Age=12.5,
            PP_status=True,
            EAL=True,
            SEN=False,
            SEN_E=False,
            LAC=False,
            Attendance=95,
        ),
        Students(
            Student_ID=2,
            MAT_ID="MAT002",
            School_ID="SCH002",
            Cohort="Y8",
            Gender="F",
            KS2_maths=92.0,
            KS2_reading=88.5,
            CAT_test=None,
            Reading_Age=None,
            PP_status=False,
            EAL=False,
            SEN=True,
            SEN_E=True,
            LAC=False,
            Attendance=87,
        ),
        Students(
            Student_ID=3,
            MAT_ID="MAT001",
            School_ID="SCH001",
            Cohort=None,
            Gender=None,
            KS2_maths=None,
            KS2_reading=None,
            CAT_test=None,
            Reading_Age=None,
            PP_status=None,
            EAL=None,
            SEN=None,
            SEN_E=None,
            LAC=None,
            Attendance=None,
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "mat_id": "MAT001",
            "school_id": "SCH001",
            "cohort": "Y7",
            "gender": "M",
            "ks2_maths_score": 85.5,
            "ks2_reading_score": 78.0,
            "cat_test_score": 110.0,
            "reading_age": 12.5,
            "pp": True,
            "eal": True,
            "send": False,
            "ehcp": False,
            "lac": False,
            "attendance": 95,
        },
        {
            "patient_id": 2,
            "mat_id": "MAT002",
            "school_id": "SCH002",
            "cohort": "Y8",
            "gender": "F",
            "ks2_maths_score": 92.0,
            "ks2_reading_score": 88.5,
            "cat_test_score": None,
            "reading_age": None,
            "pp": False,
            "eal": False,
            "send": True,
            "ehcp": True,
            "lac": False,
            "attendance": 87,
        },
        {
            "patient_id": 3,
            "mat_id": "MAT001",
            "school_id": "SCH001",
            "cohort": None,
            "gender": None,
            "ks2_maths_score": None,
            "ks2_reading_score": None,
            "cat_test_score": None,
            "reading_age": None,
            "pp": None,
            "eal": None,
            "send": None,
            "ehcp": None,
            "lac": None,
            "attendance": None,
        },
    ]


@register_test_for(ted.results)
def test_results(select_all_ted):
    results = select_all_ted(
        Students(
            Student_ID=1,
            MAT_ID="MAT001",
            School_ID="SCH001",
            Cohort="Y7",
            Gender="M",
        ),
        Students(
            Student_ID=2,
            MAT_ID="MAT002",
            School_ID="SCH002",
            Cohort="Y8",
            Gender="F",
        ),
        # Assessments
        Assessments(
            Assessment_ID=1,
            Subject="Mathematics",
            No_qns=20,
            Assessment_type="class test",
        ),
        Assessments(
            Assessment_ID=2,
            Subject="English",
            No_qns=15,
            Assessment_type="end of term",
        ),
        Assessments(
            Assessment_ID=3,
            Subject="Science",
            No_qns=None,
            Assessment_type="GCSE",
        ),
        # Classes
        Classes(
            Class_ID="CLS001",
            School_ID="SCH001",
            Year_group="Y7",
            Academic_year="2023/24",
        ),
        Classes(
            Class_ID="CLS002",
            School_ID="SCH001",
            Year_group="Y7",
            Academic_year="2023/24",
        ),
        Classes(
            Class_ID="CLS003",
            School_ID="SCH002",
            Year_group="Y8",
            Academic_year="2023/24",
        ),
        # TeacherClassAllocation - CLS001 has one teacher, CLS002 has multiple, CLS003 has none
        TeacherClassAllocation(
            Tch_Class_ID="T001-SCH001-CLS001",
            Teacher_ID="T001",
            Class_ID="CLS001",
            Subject="Mathematics",
            Academic_year="2023/24",
            Percentage=100.0,
        ),
        TeacherClassAllocation(
            Tch_Class_ID="T002-SCH001-CLS002",
            Teacher_ID="T002",
            Class_ID="CLS002",
            Subject="English",
            Academic_year="2023/24",
            Percentage=50.0,
        ),
        TeacherClassAllocation(
            Tch_Class_ID="T003-SCH001-CLS002",
            Teacher_ID="T003",
            Class_ID="CLS002",
            Subject="English",
            Academic_year="2023/24",
            Percentage=50.0,
        ),
        # AttainmentResults
        AttainmentResults(
            Student_ID=1,
            Assessment_ID=1,
            Class_ID="CLS001",
            Date=date(2023, 6, 15),
            Score=85.5,
            Predicted_Grade="7",
        ),
        AttainmentResults(
            Student_ID=1,
            Assessment_ID=2,
            Class_ID="CLS002",
            Date=date(2023, 7, 10),
            Score=92.0,
            Predicted_Grade="8",
        ),
        AttainmentResults(
            Student_ID=2,
            Assessment_ID=1,
            Class_ID="CLS001",
            Date=date(2023, 6, 15),
            Score=78.5,
            Predicted_Grade="6",
        ),
        AttainmentResults(
            Student_ID=2,
            Assessment_ID=3,
            Class_ID="CLS003",
            Date=date(2023, 8, 5),
            Score=None,
            Predicted_Grade=None,
        ),
    )
    assert results == [
        {
            "patient_id": 1,
            "class_id": "CLS001",
            "academic_year": "2023/24",
            "year_group": "Y7",
            "assessment_type": "class test",
            "subject": "Mathematics",
            "num_questions": 20,
            "date": date(2023, 6, 15),
            "score": 85.5,
            "predicted_grade": "7",
            "teacher_id": "T001",
        },
        {
            "patient_id": 1,
            "class_id": "CLS002",
            "academic_year": "2023/24",
            "year_group": "Y7",
            "assessment_type": "end of term",
            "subject": "English",
            "num_questions": 15,
            "date": date(2023, 7, 10),
            "score": 92.0,
            "predicted_grade": "8",
            "teacher_id": None,
        },
        {
            "patient_id": 2,
            "class_id": "CLS001",
            "academic_year": "2023/24",
            "year_group": "Y7",
            "assessment_type": "class test",
            "subject": "Mathematics",
            "num_questions": 20,
            "date": date(2023, 6, 15),
            "score": 78.5,
            "predicted_grade": "6",
            "teacher_id": "T001",
        },
        {
            "patient_id": 2,
            "class_id": "CLS003",
            "academic_year": "2023/24",
            "year_group": "Y8",
            "assessment_type": "GCSE",
            "subject": "Science",
            "num_questions": None,
            "date": date(2023, 8, 5),
            "score": None,
            "predicted_grade": None,
            "teacher_id": None,
        },
    ]


def test_registered_tests_are_exhaustive():
    assert_tests_exhaustive(TEDBackend())
