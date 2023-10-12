import textwrap
from datetime import date

from ehrql.main import generate_measures
from ehrql.query_engines.sqlite import SQLiteQueryEngine
from ehrql.tables.beta.core import patients
from ehrql.utils.orm_utils import make_orm_models


MEASURE_DEFINITIONS = """
from ehrql import INTERVAL, Measures, years
from ehrql.tables.beta.core import patients


measures = Measures()

measures.define_measure(
    "births",
    numerator=patients.date_of_birth.is_during(INTERVAL),
    denominator=patients.exists_for_patient(),
    group_by={"sex": patients.sex},
    intervals=years(2).starting_on("2020-01-01"),
)
"""


def test_generate_measures(in_memory_sqlite_database, tmp_path):
    in_memory_sqlite_database.setup(
        make_orm_models(
            {
                patients: [
                    dict(patient_id=1, date_of_birth=date(2020, 6, 1), sex="male"),
                    dict(patient_id=2, date_of_birth=date(2021, 6, 1), sex="female"),
                ]
            }
        )
    )

    measure_definitions = tmp_path / "measures.py"
    measure_definitions.write_text(MEASURE_DEFINITIONS)
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
    assert output_file.read_text() == textwrap.dedent(
        """\
        measure,interval_start,interval_end,ratio,numerator,denominator,sex
        births,2020-01-01,2020-12-31,1.0,1,1,male
        births,2020-01-01,2020-12-31,0.0,0,1,female
        births,2021-01-01,2021-12-31,0.0,0,1,male
        births,2021-01-01,2021-12-31,1.0,1,1,female
        """
    )


def test_generate_measures_dummy_data_generated(tmp_path):
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


def test_generate_measures_dummy_data_supplied(tmp_path):
    measure_definitions = tmp_path / "measures.py"
    measure_definitions.write_text(MEASURE_DEFINITIONS)
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
    assert output_file.read_text() == DUMMY_DATA


def test_generate_measures_dummy_tables(tmp_path):
    measure_definitions = tmp_path / "measures.py"
    measure_definitions.write_text(MEASURE_DEFINITIONS)
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
    assert output_file.read_text() == textwrap.dedent(
        """\
        measure,interval_start,interval_end,ratio,numerator,denominator,sex
        births,2020-01-01,2020-12-31,1.0,1,1,male
        births,2020-01-01,2020-12-31,0.0,0,1,female
        births,2021-01-01,2021-12-31,0.0,0,1,male
        births,2021-01-01,2021-12-31,1.0,1,1,female
        """
    )
