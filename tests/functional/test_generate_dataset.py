import csv
from datetime import date, datetime

import pytest

from ehrql.file_formats import FILE_FORMATS
from ehrql.tables import EventFrame, core, table
from tests.lib.file_utils import read_file_as_dicts
from tests.lib.inspect_utils import function_body_as_string
from tests.lib.tpp_schema import Patient


@function_body_as_string
def trivial_dataset_definition():
    from ehrql import create_dataset
    from ehrql.tables.tpp import patients

    dataset = create_dataset()
    year = patients.date_of_birth.year
    dataset.define_population(year >= 1940)
    dataset.year = year

    dataset.configure_dummy_data(
        population_size=10,
        additional_population_constraint=patients.date_of_death.is_null(),
    )


@function_body_as_string
def trivial_dataset_definition_legacy_dummy_data():
    from ehrql import create_dataset
    from ehrql.tables.tpp import patients

    dataset = create_dataset()
    year = patients.date_of_birth.year
    dataset.define_population(year >= 1940)
    dataset.year = year

    dataset.configure_dummy_data(population_size=10, legacy=True)


@function_body_as_string
def parameterised_dataset_definition():
    from ehrql import create_dataset, get_parameter
    from ehrql.tables.tpp import patients

    year = get_parameter("year", type=int)

    dataset = create_dataset()
    birth_year = patients.date_of_birth.year
    dataset.define_population(birth_year >= year)
    dataset.year = birth_year


@pytest.mark.parametrize("extension", list(FILE_FORMATS.keys()))
def test_generate_dataset_with_tpp_backend(
    call_cli, tmp_path, mssql_database, extension, monkeypatch
):
    mssql_database.setup(
        Patient(Patient_ID=1, DateOfBirth=datetime(1934, 5, 5)),
        Patient(Patient_ID=2, DateOfBirth=datetime(1943, 5, 5)),
        Patient(Patient_ID=3, DateOfBirth=datetime(1999, 5, 5)),
    )

    output_path = tmp_path / f"results.{extension}"
    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(trivial_dataset_definition)

    call_cli(
        "generate-dataset",
        dataset_definition_path,
        "--output",
        output_path,
        "--backend",
        "tpp",
        "--dsn",
        mssql_database.host_url(),
    )
    results = read_file_as_dicts(output_path)

    expected = [1943, 1999]
    if extension in (".csv", ".csv.gz"):
        expected = [str(v) for v in expected]

    assert len(results) == len(expected)
    assert {r["year"] for r in results} == set(expected)


def test_parameterised_dataset_definition(call_cli, tmp_path, mssql_database):
    mssql_database.setup(
        Patient(Patient_ID=1, DateOfBirth=datetime(1934, 5, 5)),
        Patient(Patient_ID=2, DateOfBirth=datetime(1943, 5, 5)),
        Patient(Patient_ID=3, DateOfBirth=datetime(1999, 5, 5)),
    )

    output_path = tmp_path / "results.csv"
    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(parameterised_dataset_definition)

    call_cli(
        "generate-dataset",
        dataset_definition_path,
        "--output",
        output_path,
        "--backend",
        "tpp",
        "--dsn",
        mssql_database.host_url(),
        "--",
        "--year",
        "1940",
    )
    results = read_file_as_dicts(output_path)

    expected = ["1943", "1999"]

    assert len(results) == len(expected)
    assert {r["year"] for r in results} == set(expected)


def test_parameterised_dataset_definition_with_bad_param(tmp_path, call_cli):
    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(parameterised_dataset_definition)

    with pytest.raises(SystemExit):
        call_cli(
            "generate-dataset",
            dataset_definition_path,
            "--",
            "--ear",
            "1940",
        )
    assert (
        "dataset_definition.py error: parameter `year` defined but no values found"
        in call_cli.readouterr().err
    )


def test_parameterised_dataset_definition_with_bad_param_syntax(tmp_path, call_cli):
    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(parameterised_dataset_definition)

    # Call the cli with user args, but without the required -- separator
    with pytest.raises(SystemExit):
        call_cli(
            "generate-dataset",
            dataset_definition_path,
            "--year",
            "1940",
        )

    error = call_cli.readouterr().err
    assert "unknown arguments: --year 1940" in error
    assert "If you are trying to provide custom parameters" in error


def test_generate_dataset_with_database_error(tmp_path, call_cli, mssql_database):
    mssql_database.setup(
        Patient(Patient_ID=1, DateOfBirth=datetime(1934, 5, 5)),
    )

    @function_body_as_string
    def database_operational_error_dataset_definition():
        from ehrql import create_dataset, years
        from ehrql.tables.core import patients

        dataset = create_dataset()
        dataset.define_population(patients.date_of_birth.year >= 1900)
        dataset.extended_dob = patients.date_of_birth + years(9999)

        dataset.configure_dummy_data(population_size=10)

    # This dataset definition triggers an OperationalError by implementing date
    # arithmetic that results in an out of bounds date (after 9999-12-31)
    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(database_operational_error_dataset_definition)

    with pytest.raises(SystemExit) as err:
        call_cli(
            "generate-dataset",
            dataset_definition_path,
            "--backend",
            "tpp",
            "--dsn",
            mssql_database.host_url(),
        )
    assert err.value.code == 5


@pytest.mark.dummy_data
def test_validate_dummy_data_happy_path(tmp_path, call_cli):
    dummy_data_file = tmp_path / "dummy.csv"
    dummy_data = "patient_id,year\n1,1971\n2,1992"
    dummy_data_file.write_text(dummy_data)

    output_path = tmp_path / "results.csv"
    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(trivial_dataset_definition)

    call_cli(
        "generate-dataset",
        dataset_definition_path,
        "--output",
        output_path,
        "--dummy-data-file",
        dummy_data_file,
    )
    results = read_file_as_dicts(output_path)

    assert results == [
        {"patient_id": "1", "year": "1971"},
        {"patient_id": "2", "year": "1992"},
    ]


@pytest.mark.dummy_data
def test_validate_dummy_data_error_path(tmp_path, call_cli):
    dummy_data_file = tmp_path / "dummy.csv"
    dummy_data = "patient_id,year\n1,1971\n2,foo"
    dummy_data_file.write_text(dummy_data)

    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(trivial_dataset_definition)

    with pytest.raises(SystemExit):
        call_cli(
            "generate-dataset",
            dataset_definition_path,
            "--dummy-data-file",
            dummy_data_file,
        )
    assert "invalid literal for int" in call_cli.readouterr().err


@pytest.mark.dummy_data
@pytest.mark.parametrize(
    "dataset_definition_fixture",
    (
        trivial_dataset_definition,
        trivial_dataset_definition_legacy_dummy_data,
    ),
)
def test_generate_dummy_data(tmp_path, call_cli, dataset_definition_fixture):
    output_path = tmp_path / "results.csv"
    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition_fixture)

    call_cli(
        "generate-dataset",
        dataset_definition_path,
        "--output",
        output_path,
    )
    lines = output_path.read_text().splitlines()

    assert lines[0] == "patient_id,year"
    assert len(lines) == 11  # 1 header, 10 rows


@pytest.mark.dummy_data
def test_generate_dummy_data_with_dummy_tables(tmp_path, call_cli):
    dummy_tables_path = tmp_path / "dummy_tables"
    dummy_tables_path.mkdir()
    dummy_tables_path.joinpath("patients.csv").write_text(
        "patient_id,date_of_birth\n8,1985-10-20\n9,1995-05-10"
    )

    output_path = tmp_path / "results.csv"

    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(trivial_dataset_definition)

    call_cli(
        "generate-dataset",
        dataset_definition_path,
        "--output",
        output_path,
        "--dummy-tables",
        dummy_tables_path,
    )
    results = read_file_as_dicts(output_path)

    assert results == [
        {"patient_id": "8", "year": "1985"},
        {"patient_id": "9", "year": "1995"},
    ]


@pytest.mark.dummy_data
def test_generate_dataset_disallows_reading_file_outside_working_directory(
    tmp_path, monkeypatch, call_cli
):
    csv_file = tmp_path / "file.csv"
    csv_file.write_text("patient_id,i\n1,10\n2,20")

    @function_body_as_string
    def code():
        from ehrql import create_dataset
        from ehrql.tables import PatientFrame, Series, table_from_file

        @table_from_file("<CSV_FILE>")
        class test_table(PatientFrame):
            i = Series(int)

        dataset = create_dataset()
        dataset.define_population(test_table.exists_for_patient())
        dataset.configure_dummy_data(population_size=2)
        dataset.i = test_table.i

    code = code.replace('"<CSV_FILE>"', repr(str(csv_file)))

    dataset_file = tmp_path / "sub_dir" / "dataset_definition.py"
    dataset_file.parent.mkdir(parents=True, exist_ok=True)
    dataset_file.write_text(code)

    monkeypatch.chdir(dataset_file.parent)
    with pytest.raises(Exception) as e:
        call_cli("generate-dataset", dataset_file)
    assert "is not contained within the directory" in str(e.value)


@pytest.mark.dummy_data
@pytest.mark.parametrize("legacy", [True, False])
def test_generate_dataset_passes_dummy_data_config(call_cli, tmp_path, caplog, legacy):
    @function_body_as_string
    def code():
        from ehrql import create_dataset
        from ehrql.tables.core import patients

        dataset = create_dataset()
        dataset.define_population(patients.exists_for_patient())
        dataset.sex = patients.sex

        dataset.configure_dummy_data(population_size=2, timeout=3, **{})

    code = code.replace("**{}", "legacy=True" if legacy else "")
    dataset_file = tmp_path / "dataset_definition.py"
    dataset_file.write_text(code)

    call_cli(
        "generate-dataset",
        dataset_file,
        "--output",
        tmp_path / "output.csv",
    )

    logs = caplog.text
    assert "Attempting to generate 2 matching patients" in logs
    assert "timeout: 3s" in logs
    if legacy:
        assert "Using legacy dummy data generation" in logs
    else:
        assert "Using next generation dummy data generation" in logs


def test_generate_dataset_with_test_data_file(call_cli, tmp_path):
    @function_body_as_string
    def dataset_definition_with_tests():
        from ehrql import create_dataset
        from ehrql.tables.core import patients

        dataset = create_dataset()
        dataset.define_population(patients.sex == "female")

        test_data = {  # noqa: F841
            1: {
                "patients": {"sex": "male"},
                "expected_in_population": False,
            },
            2: {
                "patients": {"sex": "female"},
                "expected_in_population": True,
                "expected_columns": {},
            },
        }

    test_data_file = tmp_path / "dataset_definition.py"
    test_data_file.write_text(dataset_definition_with_tests)
    output_file = tmp_path / "output.csv"

    captured = call_cli(
        "generate-dataset",
        test_data_file,
        "--output",
        output_file,
        "--test-data-file",
        test_data_file,
    )

    # Check that the assurance tests were invoked
    assert "All OK!" in captured.out
    # Check we also generated some output
    assert len(output_file.read_text()) > 0


def test_generate_dataset_with_event_level_data(sqlite_engine, call_cli, tmp_path):
    engine = sqlite_engine
    extension = "csv"

    engine.populate(
        {
            core.patients: [
                {"patient_id": 1, "date_of_birth": date(1980, 1, 1)},
                {"patient_id": 2, "date_of_birth": date(1990, 1, 1)},
                {"patient_id": 3, "date_of_birth": date(2000, 1, 1)},
            ],
            core.clinical_events: [
                {"patient_id": 1, "date": date(2020, 1, 1), "snomedct_code": "123456"},
                {"patient_id": 1, "date": date(2020, 2, 1), "snomedct_code": "123456"},
                {"patient_id": 1, "date": date(2020, 2, 1), "snomedct_code": "923456"},
                {"patient_id": 2, "date": date(2020, 3, 1), "snomedct_code": "123456"},
                {"patient_id": 2, "date": date(2020, 4, 1), "snomedct_code": "123457"},
                {"patient_id": 3, "date": date(2020, 5, 1), "snomedct_code": "123456"},
                {"patient_id": 3, "date": date(2020, 6, 1), "snomedct_code": "123457"},
                {"patient_id": 3, "date": date(2020, 7, 1), "snomedct_code": "123456"},
            ],
        }
    )

    @function_body_as_string
    def dataset_definition():
        from ehrql import create_dataset
        from ehrql.tables.core import clinical_events, patients

        dataset = create_dataset()
        dataset.define_population(patients.date_of_birth.year != 1990)
        dataset.dob = patients.date_of_birth
        events_1 = clinical_events.where(
            clinical_events.snomedct_code.is_in(["123456", "123457"])
        )
        events_2 = clinical_events.where(
            clinical_events.snomedct_code.is_in(["923456"])
        )
        dataset.add_event_table(
            "events_1", date=events_1.date, code=events_1.snomedct_code
        )
        dataset.add_event_table(
            "events_2", date=events_2.date, code=events_2.snomedct_code
        )

    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition)
    output_path = tmp_path / "results"

    call_cli(
        "generate-dataset",
        dataset_definition_path,
        "--output",
        f"{output_path}:{extension}",
        "--dsn",
        engine.database.host_url(),
        "--query-engine",
        engine.name,
        environ={
            "EHRQL_PERMISSIONS": '["event_level_data"]',
        },
    )

    assert read_file_as_dicts(output_path / f"dataset.{extension}") == [
        {"patient_id": "1", "dob": "1980-01-01"},
        {"patient_id": "3", "dob": "2000-01-01"},
    ]
    assert read_file_as_dicts(output_path / f"events_1.{extension}") == [
        {"patient_id": "1", "date": "2020-01-01", "code": "123456"},
        {"patient_id": "1", "date": "2020-02-01", "code": "123456"},
        {"patient_id": "3", "date": "2020-05-01", "code": "123456"},
        {"patient_id": "3", "date": "2020-06-01", "code": "123457"},
        {"patient_id": "3", "date": "2020-07-01", "code": "123456"},
    ]
    assert read_file_as_dicts(output_path / f"events_2.{extension}") == [
        {"patient_id": "1", "date": "2020-02-01", "code": "923456"},
    ]


@pytest.mark.dummy_data
def test_generate_dataset_with_dummy_event_level_data(call_cli, tmp_path):
    @function_body_as_string
    def dataset_definition():
        from ehrql import claim_permissions, create_dataset
        from ehrql.tables.core import clinical_events, patients

        claim_permissions("event_level_data")

        dataset = create_dataset()
        dataset.define_population(patients.date_of_birth.year != 1990)
        dataset.dob = patients.date_of_birth
        events_1 = clinical_events.where(
            clinical_events.snomedct_code.is_in(["123456", "123457"])
        )
        events_2 = clinical_events.where(
            clinical_events.snomedct_code.is_in(["923456"])
        )
        dataset.add_event_table(
            "events_1", date=events_1.date, code=events_1.snomedct_code
        )
        dataset.add_event_table(
            "events_2", date=events_2.date, code=events_2.snomedct_code
        )

    d = date.fromisoformat
    dummy_data = {
        "dataset": [
            {"patient_id": 1, "dob": d("1980-01-01")},
            {"patient_id": 3, "dob": d("2000-01-01")},
        ],
        "events_1": [
            {"patient_id": 1, "date": d("2020-01-01"), "code": "123456"},
            {"patient_id": 1, "date": d("2020-02-01"), "code": "123456"},
            {"patient_id": 3, "date": d("2020-05-01"), "code": "123456"},
            {"patient_id": 3, "date": d("2020-06-01"), "code": "123457"},
            {"patient_id": 3, "date": d("2020-07-01"), "code": "123456"},
        ],
        "events_2": [
            {"patient_id": 1, "date": d("2020-02-01"), "code": "923456"},
        ],
    }

    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition)

    dummy_data_path = tmp_path / "dummy_data"
    dummy_data_path.mkdir()
    for name, file_data in dummy_data.items():
        with dummy_data_path.joinpath(f"{name}.csv").open("w") as f:
            writer = csv.DictWriter(f, file_data[0].keys())
            writer.writeheader()
            writer.writerows(file_data)

    output_ext = "arrow"
    output_path = tmp_path / "results"

    call_cli(
        "generate-dataset",
        dataset_definition_path,
        "--output",
        f"{output_path}:{output_ext}",
        "--dummy-data-file",
        dummy_data_path,
    )

    for name, file_data in dummy_data.items():
        path = output_path / f"{name}.{output_ext}"
        assert read_file_as_dicts(path) == file_data


@pytest.mark.dummy_data
def test_generate_dataset_rejects_unauthorised_event_level_data_request(
    monkeypatch, sqlite_engine, call_cli, tmp_path
):
    engine = sqlite_engine

    @function_body_as_string
    def dataset_definition():
        from ehrql import create_dataset
        from ehrql.tables.core import clinical_events

        dataset = create_dataset()
        dataset.define_population(clinical_events.exists_for_patient())
        events_1 = clinical_events.where(clinical_events.snomedct_code == "123456")
        dataset.add_event_table("events_1", date=events_1.date)

    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition)

    with pytest.raises(SystemExit):
        call_cli(
            "generate-dataset",
            dataset_definition_path,
            "--output",
            tmp_path / "results:csv",
            "--dsn",
            engine.database.host_url(),
            "--query-engine",
            engine.name,
            environ={},
        )

    output = call_cli.readouterr().err
    assert "Missing permissions" in output
    assert "event_level_data" in output


@table
class restricted_table(EventFrame):
    class _meta:
        required_permission = "special_perm"


@function_body_as_string
def dataset_definition_with_restricted_table():
    from ehrql import create_dataset
    from tests.functional.test_generate_dataset import restricted_table

    dataset = create_dataset()
    dataset.define_population(restricted_table.exists_for_patient())


def test_generate_dataset_rejects_insufficient_permissions(
    sqlite_engine, call_cli, tmp_path
):
    engine = sqlite_engine

    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition_with_restricted_table)

    with pytest.raises(SystemExit):
        call_cli(
            "generate-dataset",
            dataset_definition_path,
            "--output",
            tmp_path / "results.csv",
            "--dsn",
            engine.database.host_url(),
            "--query-engine",
            engine.name,
        )

    output = call_cli.readouterr().err
    assert "Missing permissions" in output
    assert "restricted_table" in output
    assert "special_perm" in output


def test_generate_dataset_allows_sufficient_permissions(
    sqlite_engine, call_cli, tmp_path
):
    engine = sqlite_engine
    engine.populate({restricted_table: [{"patient_id": 1}]})

    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition_with_restricted_table)
    output_path = tmp_path / "results.csv"

    call_cli(
        "generate-dataset",
        dataset_definition_path,
        "--output",
        output_path,
        "--dsn",
        engine.database.host_url(),
        "--query-engine",
        engine.name,
        environ={
            "EHRQL_PERMISSIONS": '["foo","special_perm","bar"]',
        },
    )

    assert output_path.exists()


@pytest.mark.dummy_data
def test_generate_dataset_errors_on_missing_permissions_for_dummy_data(
    call_cli, tmp_path
):
    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition_with_restricted_table)

    with pytest.raises(SystemExit):
        call_cli(
            "generate-dataset",
            dataset_definition_path,
            "--output",
            tmp_path / "results.csv",
        )

    output = call_cli.readouterr().err
    assert "restricted_table" in output
    assert 'claim_permissions("special_perm")' in output


@pytest.mark.dummy_data
def test_generate_dataset_does_not_warn_when_permission_claimed(
    call_cli, tmp_path, caplog
):
    dataset_definition_with_claim = (
        f"from ehrql import claim_permissions\n"
        f"claim_permissions('special_perm')\n"
        f"\n"
        f"{dataset_definition_with_restricted_table}"
    )
    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition_with_claim)
    output_path = tmp_path / "results.csv"

    call_cli(
        "generate-dataset",
        dataset_definition_path,
        "--output",
        output_path,
    )

    assert output_path.exists()

    output = caplog.text
    assert "restricted_table" not in output
    assert 'claim_permissions("special_perm")' not in output
