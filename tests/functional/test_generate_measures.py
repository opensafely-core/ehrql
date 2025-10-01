import csv
import textwrap
from datetime import date

import pytest

from ehrql.tables import EventFrame, table
from ehrql.tables.core import patients
from tests.lib.file_utils import read_file_as_dicts
from tests.lib.inspect_utils import function_body_as_string
from tests.lib.orm_utils import make_orm_models


@function_body_as_string
def MEASURE_DEFINITIONS():
    from ehrql import INTERVAL, Measures, years
    from ehrql.tables.core import patients

    measures = Measures()

    measures.define_measure(
        "births",
        numerator=patients.date_of_birth.is_during(INTERVAL),
        denominator=patients.exists_for_patient(),
        group_by={"sex": patients.sex},
        intervals=years(2).starting_on("2020-01-01"),
    )


DISABLE_DISCLOSURE_CONTROL = "\n\nmeasures.configure_disclosure_control(enabled=False)"


@pytest.mark.parametrize("disclosure_control_enabled", [False, True])
def test_generate_measures(
    in_memory_sqlite_database, tmp_path, disclosure_control_enabled, call_cli
):
    in_memory_sqlite_database.setup(
        make_orm_models(
            {
                patients: [
                    dict(patient_id=1, date_of_birth=date(2020, 6, 1), sex="male"),
                    dict(patient_id=2, date_of_birth=date(2021, 6, 1), sex="female"),
                    dict(patient_id=3, date_of_birth=date(2021, 6, 1), sex="female"),
                    dict(patient_id=4, date_of_birth=date(2021, 6, 1), sex="female"),
                    dict(patient_id=5, date_of_birth=date(2021, 6, 1), sex="female"),
                    dict(patient_id=6, date_of_birth=date(2021, 6, 1), sex="female"),
                    dict(patient_id=7, date_of_birth=date(2021, 6, 1), sex="female"),
                    dict(patient_id=8, date_of_birth=date(2021, 6, 1), sex="female"),
                    dict(patient_id=9, date_of_birth=date(2021, 6, 1), sex="female"),
                ]
            }
        )
    )

    measure_definitions = tmp_path / "measures.py"
    if disclosure_control_enabled:
        measure_definitions.write_text(MEASURE_DEFINITIONS)
    else:
        measure_definitions.write_text(MEASURE_DEFINITIONS + DISABLE_DISCLOSURE_CONTROL)
    output_file = tmp_path / "output.csv"

    call_cli(
        "generate-measures",
        measure_definitions,
        "--output",
        output_file,
        "--dsn",
        in_memory_sqlite_database.host_url(),
        "--query-engine",
        "sqlite",
    )
    if disclosure_control_enabled:
        assert output_file.read_text() == textwrap.dedent(
            """\
            measure,interval_start,interval_end,ratio,numerator,denominator,sex
            births,2020-01-01,2020-12-31,0.0,0,10,female
            births,2020-01-01,2020-12-31,,0,0,male
            births,2021-01-01,2021-12-31,1.0,10,10,female
            births,2021-01-01,2021-12-31,,0,0,male
            """
        )
    else:
        assert output_file.read_text() == textwrap.dedent(
            """\
            measure,interval_start,interval_end,ratio,numerator,denominator,sex
            births,2020-01-01,2020-12-31,0.0,0,8,female
            births,2020-01-01,2020-12-31,1.0,1,1,male
            births,2021-01-01,2021-12-31,1.0,8,8,female
            births,2021-01-01,2021-12-31,0.0,0,1,male
            """
        )


@pytest.mark.parametrize("disclosure_control_enabled", [False, True])
def test_generate_measures_dummy_data_generated(
    tmp_path, disclosure_control_enabled, call_cli
):
    measure_definitions = tmp_path / "measures.py"
    measure_definitions.write_text(MEASURE_DEFINITIONS)
    output_file = tmp_path / "output.csv"

    call_cli(
        "generate-measures",
        measure_definitions,
        "--output",
        output_file,
    )
    assert output_file.read_text().startswith(
        "measure,interval_start,interval_end,ratio,numerator,denominator,sex"
    )


@pytest.mark.parametrize("disclosure_control_enabled", [False, True])
def test_generate_measures_legacy_dummy_data_generated(
    tmp_path, disclosure_control_enabled, call_cli
):
    measure_definitions = tmp_path / "measures.py"
    measure_definitions.write_text(
        MEASURE_DEFINITIONS
        + "\nmeasures.configure_dummy_data(population_size=10, legacy=True)"
    )
    output_file = tmp_path / "output.csv"

    call_cli(
        "generate-measures",
        measure_definitions,
        "--output",
        output_file,
    )
    assert output_file.read_text().startswith(
        "measure,interval_start,interval_end,ratio,numerator,denominator,sex"
    )


@pytest.mark.parametrize("disclosure_control_enabled", [False, True])
def test_generate_measures_dummy_data_supplied(
    tmp_path, disclosure_control_enabled, call_cli
):
    measure_definitions = tmp_path / "measures.py"
    if disclosure_control_enabled:
        measure_definitions.write_text(MEASURE_DEFINITIONS)
    else:
        measure_definitions.write_text(MEASURE_DEFINITIONS + DISABLE_DISCLOSURE_CONTROL)
    output_file = tmp_path / "output.csv"
    DUMMY_DATA = textwrap.dedent(
        """\
        measure,interval_start,interval_end,ratio,numerator,denominator,sex
        births,2020-01-01,2020-12-31,0.4,4,10,male
        births,2020-01-01,2020-12-31,0.3,6,20,female
        births,2021-01-01,2021-12-31,0.6,6,10,male
        births,2021-01-01,2021-12-31,0.7,14,20,female
        """
    )
    dummy_data_file = tmp_path / "dummy.csv"
    dummy_data_file.write_text(DUMMY_DATA)

    call_cli(
        "generate-measures",
        measure_definitions,
        "--output",
        output_file,
        "--dummy-data",
        dummy_data_file,
    )
    if disclosure_control_enabled:
        assert output_file.read_text() == textwrap.dedent(
            """\
            measure,interval_start,interval_end,ratio,numerator,denominator,sex
            births,2020-01-01,2020-12-31,0.0,0,10,male
            births,2020-01-01,2020-12-31,0.0,0,20,female
            births,2021-01-01,2021-12-31,0.0,0,10,male
            births,2021-01-01,2021-12-31,0.75,15,20,female
            """
        )
    else:
        assert output_file.read_text() == DUMMY_DATA


@pytest.mark.parametrize("disclosure_control_enabled", [False, True])
def test_generate_measures_dummy_tables(tmp_path, disclosure_control_enabled, call_cli):
    measure_definitions = tmp_path / "measures.py"
    if disclosure_control_enabled:
        measure_definitions.write_text(MEASURE_DEFINITIONS)
    else:
        measure_definitions.write_text(MEASURE_DEFINITIONS + DISABLE_DISCLOSURE_CONTROL)
    output_file = tmp_path / "output.csv"
    DUMMY_DATA = textwrap.dedent(
        """\
        patient_id,date_of_birth,sex
        1,2020-06-01,male
        2,2021-06-01,female
        """
    )
    dummy_tables_path = tmp_path / "dummy_tables"
    dummy_tables_path.mkdir()
    dummy_tables_path.joinpath("patients.csv").write_text(DUMMY_DATA)

    call_cli(
        "generate-measures",
        measure_definitions,
        "--output",
        output_file,
        "--dummy-tables",
        dummy_tables_path,
    )
    if disclosure_control_enabled:
        assert output_file.read_text() == textwrap.dedent(
            """\
            measure,interval_start,interval_end,ratio,numerator,denominator,sex
            births,2020-01-01,2020-12-31,,0,0,male
            births,2020-01-01,2020-12-31,,0,0,female
            births,2021-01-01,2021-12-31,,0,0,male
            births,2021-01-01,2021-12-31,,0,0,female
            """
        )
    else:
        assert output_file.read_text() == textwrap.dedent(
            """\
            measure,interval_start,interval_end,ratio,numerator,denominator,sex
            births,2020-01-01,2020-12-31,1.0,1,1,male
            births,2020-01-01,2020-12-31,0.0,0,1,female
            births,2021-01-01,2021-12-31,0.0,0,1,male
            births,2021-01-01,2021-12-31,1.0,1,1,female
            """
        )


def test_generate_measures_multiple_files(call_cli, tmp_path):
    @function_body_as_string
    def measure_definition():
        from ehrql import INTERVAL, create_measures, months
        from ehrql.tables.core import clinical_events, patients

        events = clinical_events.where(clinical_events.date.is_during(INTERVAL))
        age_band = (patients.age_on(INTERVAL.start_date) // 10) * 10

        measures = create_measures()
        measures.define_defaults(
            numerator=events.count_for_patient(),
            denominator=events.exists_for_patient(),
            intervals=months(2).starting_on("2020-01-01"),
        )
        measures.define_measure(
            "age_band",
            group_by={"age_band": age_band},
        )
        measures.define_measure(
            "sex",
            group_by={"sex": patients.sex},
        )
        measures.define_measure(
            "age_band_alive",
            group_by={
                "age_band": age_band,
                "is_alive": patients.is_alive_on(INTERVAL.start_date),
            },
        )

    measure_definition_path = tmp_path / "measures.py"
    measure_definition_path.write_text(measure_definition)
    output_ext = "arrow"
    output_path = tmp_path / "measure_outputs"

    call_cli(
        "generate-measures",
        measure_definition_path,
        "--output",
        f"{output_path}:{output_ext}",
    )

    # Check the expected files exist, have the expected columns and contain some data
    for name, groups in [
        ("age_band", ["age_band"]),
        ("sex", ["sex"]),
        ("age_band_alive", ["age_band", "is_alive"]),
    ]:
        file_data = read_file_as_dicts(output_path / f"{name}.{output_ext}")
        assert file_data[0].keys() == {
            "interval_start",
            "interval_end",
            "ratio",
            "numerator",
            "denominator",
            *groups,
        }
        assert len(file_data) > 1


def test_generate_measures_multiple_dummy_data_files(call_cli, tmp_path):
    @function_body_as_string
    def measure_definition():
        from ehrql import INTERVAL, create_measures, months
        from ehrql.tables.core import clinical_events, patients

        events = clinical_events.where(clinical_events.date.is_during(INTERVAL))
        age_band = (patients.age_on(INTERVAL.start_date) // 10) * 10

        measures = create_measures()
        measures.define_defaults(
            numerator=events.count_for_patient(),
            denominator=events.exists_for_patient(),
            intervals=months(2).starting_on("2020-01-01"),
        )
        measures.define_measure(
            "age_band",
            group_by={"age_band": age_band},
        )
        measures.define_measure(
            "sex",
            group_by={"sex": patients.sex},
        )
        measures.define_measure(
            "age_band_alive",
            group_by={
                "age_band": age_band,
                "is_alive": patients.is_alive_on(INTERVAL.start_date).map_values(
                    {True: "Y", False: "N"}
                ),
            },
        )
        measures.configure_disclosure_control(enabled=False)

    dummy_data = {
        "age_band": [
            {
                "interval_start": date(2020, 1, 1),
                "interval_end": date(2020, 1, 31),
                "ratio": 2.0,
                "numerator": 20,
                "denominator": 10,
                "age_band": 10,
            },
            {
                "interval_start": date(2020, 2, 1),
                "interval_end": date(2020, 2, 29),
                "ratio": 0.5,
                "numerator": 5,
                "denominator": 10,
                "age_band": 40,
            },
        ],
        "sex": [
            {
                "interval_start": date(2020, 1, 1),
                "interval_end": date(2020, 1, 31),
                "ratio": 1.0,
                "numerator": 10,
                "denominator": 10,
                "sex": "female",
            },
            {
                "interval_start": date(2020, 1, 1),
                "interval_end": date(2020, 1, 31),
                "ratio": None,
                "numerator": 0,
                "denominator": 0,
                "sex": "male",
            },
        ],
        "age_band_alive": [
            {
                "interval_start": date(2020, 1, 1),
                "interval_end": date(2020, 1, 31),
                "ratio": 1.0,
                "numerator": 10,
                "denominator": 10,
                "age_band": 10,
                "is_alive": "Y",
            },
            {
                "interval_start": date(2020, 2, 1),
                "interval_end": date(2020, 2, 29),
                "ratio": 2.5,
                "numerator": 25,
                "denominator": 10,
                "age_band": 40,
                "is_alive": "N",
            },
        ],
    }

    dummy_data_path = tmp_path / "dummy_data"
    dummy_data_path.mkdir()
    for name, file_data in dummy_data.items():
        with dummy_data_path.joinpath(f"{name}.csv").open("w") as f:
            writer = csv.DictWriter(f, file_data[0].keys())
            writer.writeheader()
            writer.writerows(file_data)

    measure_definition_path = tmp_path / "measures.py"
    measure_definition_path.write_text(measure_definition)
    output_path = tmp_path / "measures.arrow"

    call_cli(
        "generate-measures",
        measure_definition_path,
        "--dummy-data-file",
        dummy_data_path,
        "--output",
        output_path,
    )

    output_data = read_file_as_dicts(output_path)

    # Create the output we're expecting to find by combining all the input dummy data
    combined_data = []
    for name, file_data in dummy_data.items():
        combined_data.extend(
            {"measure": name, "age_band": None, "sex": None, "is_alive": None} | i
            for i in file_data
        )

    # Check the we have the expected output (modulo row order)
    assert len(output_data) == len(combined_data)
    assert {hashable(i) for i in output_data} == {hashable(i) for i in combined_data}


@table
class restricted_table(EventFrame):
    class _meta:
        required_permission = "special_perm"


@function_body_as_string
def measure_definitions_with_restricted_table():
    from ehrql import create_measures, months
    from tests.functional.test_generate_measures import restricted_table

    measures = create_measures()
    measures.define_measure(
        "some_measure",
        numerator=restricted_table.count_for_patient(),
        denominator=restricted_table.exists_for_patient(),
        intervals=months(1).starting_on("2020-01-01"),
    )


def test_generate_measures_rejects_insufficient_permissions(
    sqlite_engine, call_cli, tmp_path
):
    engine = sqlite_engine

    measure_definitions_path = tmp_path / "measure_definitions.py"
    measure_definitions_path.write_text(measure_definitions_with_restricted_table)

    with pytest.raises(SystemExit):
        call_cli(
            "generate-measures",
            measure_definitions_path,
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


def test_generate_measures_allows_sufficient_permissions(
    sqlite_engine, call_cli, tmp_path
):
    engine = sqlite_engine
    engine.populate({restricted_table: [{"patient_id": 1}]})

    measure_definitions_path = tmp_path / "measure_definitions.py"
    measure_definitions_path.write_text(measure_definitions_with_restricted_table)
    output_path = tmp_path / "results.csv"

    call_cli(
        "generate-measures",
        measure_definitions_path,
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


def test_generate_measures_warns_on_missing_permissions_for_dummy_data(
    call_cli, tmp_path, caplog
):
    measure_definitions_path = tmp_path / "measure_definitions.py"
    measure_definitions_path.write_text(measure_definitions_with_restricted_table)
    output_path = tmp_path / "results.csv"

    call_cli(
        "generate-measures",
        measure_definitions_path,
        "--output",
        output_path,
    )

    assert output_path.exists()

    output = caplog.text
    assert "restricted_table" in output
    assert 'claim_permissions("special_perm")' in output


def test_generate_measures_does_not_warn_when_permission_claimed(
    call_cli, tmp_path, caplog
):
    measure_definitions_with_claim = (
        f"from ehrql import claim_permissions\n"
        f"claim_permissions('special_perm')\n"
        f"\n"
        f"{measure_definitions_with_restricted_table}"
    )
    measure_definitions_path = tmp_path / "measure_definitions.py"
    measure_definitions_path.write_text(measure_definitions_with_claim)
    output_path = tmp_path / "results.csv"

    call_cli(
        "generate-measures",
        measure_definitions_path,
        "--output",
        output_path,
    )

    assert output_path.exists()

    output = caplog.text
    assert "restricted_table" not in output
    assert 'claim_permissions("special_perm")' not in output


def hashable(dictionary):
    # Dictionaries aren't hashable so we need to turn them into something which is in
    # order to use set comparison
    return frozenset(dictionary.items())
