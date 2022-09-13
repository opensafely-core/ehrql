import datetime

from databuilder.ehrql import Dataset
from databuilder.query_engines.csv import CSVQueryEngine
from databuilder.query_language import compile
from databuilder.tables import EventFrame, PatientFrame, Series, table


def test_csv_query_engine(tmp_path):
    tmp_path.joinpath("patients.csv").write_text(
        "\n".join(
            [
                # Columns like `extra_column` which aren't in the schema should just be
                # ignored
                "patient_id,sex,top_score,sharpe_ratio,is_ok,extra_column",
                "1,M,100,0.5,0,a",
                "2,F,200,1.5,1,b",
                "3,,,,,",
            ]
        ),
    )
    tmp_path.joinpath("events.csv").write_text(
        "\n".join(
            [
                "patient_id,date,code",
                "1,2000-01-01,abc",
                "1,2000-02-01,def",
                "1,2000-03-01,def",
                "2,2001-01-01,abc",
                "2,2001-02-01,def",
            ]
        ),
    )

    @table
    class patients(PatientFrame):
        sex = Series(str)
        top_score = Series(int)
        sharpe_ratio = Series(float)
        is_ok = Series(bool)

    @table
    class events(EventFrame):
        date = Series(datetime.date)
        code = Series(str)
        # Columns in the schema which aren't in the CSV should just end up NULL
        expected_missing = Series(bool)

    dataset = Dataset()
    dataset.sex = patients.sex
    dataset.top_score = patients.top_score
    dataset.sharpe_ratio = patients.sharpe_ratio
    dataset.is_ok = patients.is_ok

    dataset.latest_abc = (
        events.take(events.code == "def").sort_by(events.date).first_for_patient().date
    )
    # Check that missing columns end up NULL
    dataset.missing = events.take(events.expected_missing.is_null()).count_for_patient()

    dataset.set_population(patients.exists_for_patient())
    variable_definitions = compile(dataset)

    query_engine = CSVQueryEngine(tmp_path)
    results = query_engine.get_results(variable_definitions)

    assert list(results) == [
        (1, "M", 100, 0.5, False, datetime.date(2000, 2, 1), 3),
        (2, "F", 200, 1.5, True, datetime.date(2001, 2, 1), 2),
        (3, None, None, None, None, None, 0),
    ]


def test_csv_query_engine_create_missing(tmp_path):
    @table
    class patients(PatientFrame):
        sex = Series(str)

    @table
    class events(EventFrame):
        date = Series(datetime.date)
        code = Series(str)

    dataset = Dataset()
    dataset.sex = patients.sex
    dataset.set_population(events.exists_for_patient())
    variable_definitions = compile(dataset)

    query_engine = CSVQueryEngine(
        tmp_path, config={"DATABUILDER_CREATE_MISSING_CSV": "True"}
    )
    results = query_engine.get_results(variable_definitions)

    assert list(results) == []

    assert tmp_path.joinpath("patients.csv").read_text() == "patient_id,sex\n"
    assert tmp_path.joinpath("events.csv").read_text() == "patient_id,date,code\n"
