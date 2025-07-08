import sqlalchemy

import ehrql.tables.ted
from ehrql.backends.base import MappedTable, QueryTable, SQLBackend
from ehrql.query_engines.mssql import MSSQLQueryEngine


class TEDBackend(SQLBackend):
    """
    The ehrQL TED backend provides access to education data from the TED
    dataset, including student demographics and assessment results.
    """

    display_name = "TED"
    query_engine_class = MSSQLQueryEngine
    patient_join_column = "student_id"
    implements = [
        ehrql.tables.ted,
    ]

    def column_kwargs_for_type(self, type_):
        """Override to set collation for string types to match SQL Server defaults"""
        if type_ is str:
            return {
                "type_": sqlalchemy.String(collation="SQL_Latin1_General_CP1_CS_AS")
            }
        return super().column_kwargs_for_type(type_)

    students = MappedTable(
        source="Students",
        columns={
            "patient_id": "Student_ID",
            "mat_id": "MAT_ID",
            "school_id": "School_ID",
            "cohort": "Cohort",
            "gender": "Gender",
            "ks2_maths_score": "KS2_maths",
            "ks2_reading_score": "KS2_reading",
            "cat_test_score": "CAT test",
            "reading_age": "Reading Age",
            "pp": "PP_status",
            "eal": "EAL",
            "send": "SEN",
            "ehcp": "SEN E",
            "lac": "LAC",
            "attendance": "Attendance",
        },
    )

    results = QueryTable(
        """
            SELECT
                ar.Student_ID AS patient_id,
                ar.Class_ID AS class_id,
                c.Academic_year AS academic_year,
                c.Year_group AS year_group,
                a.Assessment_type AS assessment_type,
                a.Subject AS subject,
                a.No_qns AS num_questions,
                ar.Date AS date,
                ar.Score AS score,
                ar.Predicted_Grade AS predicted_grade,
                CASE
                    WHEN teacher_counts.teacher_count = 1 THEN teacher_counts.Teacher_ID
                    ELSE NULL
                END AS teacher_id
            FROM AttainmentResults ar
            LEFT JOIN Assessments a ON ar.Assessment_ID = a.Assessment_ID
            LEFT JOIN Classes c ON ar.Class_ID = c.Class_ID
            LEFT JOIN (
                SELECT
                    Class_ID,
                    COUNT(DISTINCT Teacher_ID) AS teacher_count,
                    MAX(Teacher_ID) AS Teacher_ID
                FROM TeacherClassAllocation
                GROUP BY Class_ID
            ) teacher_counts ON ar.Class_ID = teacher_counts.Class_ID
        """
    )
