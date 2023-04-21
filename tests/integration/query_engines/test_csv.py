from ehrql.ehrql import Dataset
from ehrql.query_engines.csv import CSVQueryEngine
from ehrql.query_language import compile
from ehrql.tables import EventFrame, PatientFrame, Series, table


def test_csv_query_engine(tmp_path):
    tmp_path.joinpath("patients.csv").write_text(
        "\n".join(
            [
                # Columns like `extra_column` which aren't in the schema should just be
                # ignored
                "patient_id,sex,extra_column",
                "1,M,a",
                "2,F,b",
                "3,,",
            ]
        ),
    )
    tmp_path.joinpath("events.csv").write_text(
        "\n".join(
            [
                "patient_id,score",
                "1,2",
                "1,3",
                "1,4",
                "2,5",
                "2,10",
            ]
        ),
    )

    @table
    class patients(PatientFrame):
        sex = Series(str)

    @table
    class events(EventFrame):
        score = Series(int)
        # Columns in the schema which aren't in the CSV should just end up NULL
        expected_missing = Series(bool)

    dataset = Dataset()
    dataset.sex = patients.sex
    dataset.total_score = events.score.sum_for_patient()
    # Check that missing columns end up NULL
    dataset.missing = events.where(
        events.expected_missing.is_null()
    ).count_for_patient()

    dataset.define_population(patients.exists_for_patient())
    variable_definitions = compile(dataset)

    query_engine = CSVQueryEngine(tmp_path)
    results = query_engine.get_results(variable_definitions)

    assert list(results) == [
        (1, "M", 9, 3),
        (2, "F", 15, 2),
        (3, None, None, 0),
    ]
