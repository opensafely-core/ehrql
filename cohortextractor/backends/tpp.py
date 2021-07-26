from cohortextractor.backends.base import BaseBackend, Column, MappedTable, QueryTable
from cohortextractor.query_engines.mssql import MssqlQueryEngine


def rtrim(ref, char):
    """
    MSSQL's {L,R}TRIM() functions (unlike TRIM()) don't allow trimming of arbitrary characters, only spaces. So we've
    implemented it here. Note that this won't work as-is for '^' or ']', but they could be supported with a bit of
    escaping.
        * Since we're using PATINDEX(), which only works from the front of the string, we REVERSE() the
          string every time we refer to it and then re-REVERSE() the result once we're done.
        * We search through the string to find the index of the first character that isn't the thing we're stripping.
        * Then we work out the length of the string remaining from that point to the end.
        * Finally we take a substring from the index to the end of the string.

    (LTRIM() could be implemented in the same way, but without all the reversing.)
    """
    assert len(char) == 1
    assert char not in ["^", "]"]
    return f"""
        REVERSE(
            SUBSTRING(
                REVERSE({ref}),
                PATINDEX(
                    '%[^{char}]%',
                    REVERSE({ref})
                ),
                LEN({ref}) - PATINDEX('%[^{char}]%', REVERSE({ref})) + 1
            )
        )
    """


class TPPBackend(BaseBackend):
    backend_id = "tpp"
    query_engine_class = MssqlQueryEngine
    patient_join_column = "Patient_ID"

    patients = MappedTable(
        source="Patient",
        columns=dict(
            sex=Column("varchar", source="Sex"),
            date_of_birth=Column("date", source="DateOfBirth"),
        ),
    )

    clinical_events = MappedTable(
        source="CodedEvent",
        columns=dict(
            code=Column("varchar", source="CTV3Code"),
            date=Column("datetime", source="ConsultationDate"),
        ),
    )

    practice_registrations = MappedTable(
        source="RegistrationHistory",
        columns=dict(
            date_start=Column("datetime", source="StartDate"),
            date_end=Column("datetime", source="EndDate"),
        ),
    )

    sgss_sars_cov_2 = QueryTable(
        columns=dict(
            date=Column("date"),
            positive_result=Column("boolean"),
        ),
        query="""
            SELECT Patient_ID as patient_id, Specimen_Date AS date, 1 AS positive_result FROM SGSS_AllTests_Positive
            UNION ALL
            SELECT Patient_ID as patient_id, Specimen_Date AS date, 0 AS positive_result FROM SGSS_AllTests_Negative
        """,
    )

    hospitalizations = QueryTable(
        columns=dict(
            date=Column("date"),
            code=Column("varchar"),
        ),
        query=f"""
            SELECT Patient_ID as patient_id, Admission_Date as date, {rtrim("fully_split.Value", "X")} as code
            FROM APCS
            -- STRING_SPLIT() only accepts a single-character delimiter, so collapse multi-character delimiters before
            -- splitting. This only works because we know the codes themselves don't container commas and pipes.
            CROSS APPLY STRING_SPLIT(REPLACE(Der_Diagnosis_All, ' ||', '|'), '|') pipe_split
            CROSS APPLY STRING_SPLIT(REPLACE(pipe_split.Value, ' ,', ','), ',') fully_split
        """,
    )
