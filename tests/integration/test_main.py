import textwrap
from datetime import date

import pytest

from ehrql.main import debug_dataset_definition, generate_measures
from ehrql.query_engines.sqlite import SQLiteQueryEngine
from ehrql.tables.core import patients
from tests.lib.orm_utils import make_orm_models


MEASURE_DEFINITIONS = """
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
"""

DISABLE_DISCLOSURE_CONTROL = "\n\nmeasures.configure_disclosure_control(enabled=False)"


@pytest.mark.parametrize("disclosure_control_enabled", [False, True])
def test_generate_measures(
    in_memory_sqlite_database, tmp_path, disclosure_control_enabled
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

    generate_measures(
        measure_definitions,
        output_file,
        dsn=in_memory_sqlite_database.host_url(),
        query_engine_class=SQLiteQueryEngine,
        # Defaults
        backend_class=None,
        dummy_tables_path=None,
        dummy_data_file=None,
        environ={},
        user_args=(),
    )
    if disclosure_control_enabled:
        assert output_file.read_text() == textwrap.dedent(
            """\
            measure,interval_start,interval_end,ratio,numerator,denominator,sex
            births,2020-01-01,2020-12-31,,0,0,male
            births,2020-01-01,2020-12-31,0.0,0,10,female
            births,2021-01-01,2021-12-31,,0,0,male
            births,2021-01-01,2021-12-31,1.0,10,10,female
            """
        )
    else:
        assert output_file.read_text() == textwrap.dedent(
            """\
            measure,interval_start,interval_end,ratio,numerator,denominator,sex
            births,2020-01-01,2020-12-31,1.0,1,1,male
            births,2020-01-01,2020-12-31,0.0,0,8,female
            births,2021-01-01,2021-12-31,0.0,0,1,male
            births,2021-01-01,2021-12-31,1.0,8,8,female
            """
        )


@pytest.mark.parametrize("disclosure_control_enabled", [False, True])
def test_generate_measures_dummy_data_generated(tmp_path, disclosure_control_enabled):
    measure_definitions = tmp_path / "measures.py"
    measure_definitions.write_text(MEASURE_DEFINITIONS)
    output_file = tmp_path / "output.csv"

    generate_measures(
        measure_definitions,
        output_file,
        # Defaults
        dsn=None,
        backend_class=None,
        query_engine_class=None,
        dummy_tables_path=None,
        dummy_data_file=None,
        environ={},
        user_args=(),
    )
    assert output_file.read_text().startswith(
        "measure,interval_start,interval_end,ratio,numerator,denominator,sex"
    )


@pytest.mark.parametrize("disclosure_control_enabled", [False, True])
def test_generate_measures_legacy_dummy_data_generated(
    tmp_path, disclosure_control_enabled
):
    measure_definitions = tmp_path / "measures.py"
    measure_definitions.write_text(
        MEASURE_DEFINITIONS
        + "\nmeasures.configure_dummy_data(population_size=10, legacy=True)"
    )
    output_file = tmp_path / "output.csv"

    generate_measures(
        measure_definitions,
        output_file,
        # Defaults
        dsn=None,
        backend_class=None,
        query_engine_class=None,
        dummy_tables_path=None,
        dummy_data_file=None,
        environ={},
        user_args=(),
    )
    assert output_file.read_text().startswith(
        "measure,interval_start,interval_end,ratio,numerator,denominator,sex"
    )


@pytest.mark.parametrize("disclosure_control_enabled", [False, True])
def test_generate_measures_dummy_data_supplied(tmp_path, disclosure_control_enabled):
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

    generate_measures(
        measure_definitions,
        output_file,
        dummy_data_file=dummy_data_file,
        # Defaults
        dsn=None,
        backend_class=None,
        query_engine_class=None,
        dummy_tables_path=None,
        environ={},
        user_args=(),
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
def test_generate_measures_dummy_tables(tmp_path, disclosure_control_enabled):
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

    generate_measures(
        measure_definitions,
        output_file,
        dummy_tables_path=dummy_tables_path,
        # Defaults
        dsn=None,
        backend_class=None,
        query_engine_class=None,
        dummy_data_file=None,
        environ={},
        user_args=(),
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


def test_debug_show(tmp_path, capsys):
    definition = textwrap.dedent(
        """\
        from ehrql import create_dataset, show
        from ehrql.tables.core import patients

        dataset = create_dataset()
        year = patients.date_of_birth.year
        show(dataset, label="Number")
        dataset.define_population(year>1980)
        """
    )

    definition_path = tmp_path / "show.py"
    definition_path.write_text(definition)
    DUMMY_DATA = textwrap.dedent(
        """\
        patient_id,date_of_birth
        1,1980-06-01
        2,1985-06-01
        """
    )
    dummy_tables_path = tmp_path / "dummy_tables"
    dummy_tables_path.mkdir()
    dummy_tables_path.joinpath("patients.csv").write_text(DUMMY_DATA)

    debug_dataset_definition(
        definition_path,
        dummy_tables_path=dummy_tables_path,
        environ={},
        user_args=(),
    )

    expected = textwrap.dedent(
        """\
        Show line 6: Number
        patient_id
        -----------------
        """
    ).strip()
    assert capsys.readouterr().err.strip() == expected
