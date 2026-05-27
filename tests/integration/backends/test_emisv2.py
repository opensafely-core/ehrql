from datetime import UTC, date, datetime

import pytest
import sqlalchemy

from ehrql import create_dataset
from ehrql.backends.emisv2 import EMISV2Backend
from ehrql.tables import emisv2
from ehrql.utils.sqlalchemy_query_utils import CreateTableAs, GeneratedTable
from tests.backend_schemas.emisv2.schema import (
    MedicationIssueRecord,
    Observation,
    Patient,
)

from .helpers import (
    assert_tests_exhaustive,
    assert_types_correct,
    get_all_backend_columns,
    register_test_for,
)


def test_extract_smoketest_dataset_definition(trino_engine):
    trino_engine.setup(
        # Trino DBAPI's Binary() implementation takes a string and encodes it as UTF-8
        Patient(
            _pk=1,
            patient_id=bytes(range(16)).decode("utf-8"),
            date_of_birth=datetime(2000, 1, 1, 0, 0, 0, 0),
        ),
        Patient(
            _pk=2,
            patient_id=bytes(range(1, 17)).decode("utf-8"),
            date_of_birth=datetime(1900, 1, 1, 0, 0, 0, 0),
        ),
    )

    # This query is a copy of the smoketest dataset definition query in
    # tests/acceptance/external_studies/test-age-distribution/analysis/dataset_definition.py
    from ehrql.tables.smoketest import patients

    index_year = 2022
    min_age = 18
    max_age = 80

    year_of_birth = patients.date_of_birth.year
    age = index_year - year_of_birth

    dataset = create_dataset()
    dataset.define_population((age >= min_age) & (age <= max_age))
    dataset.age = age

    results = trino_engine.extract(dataset, backend=EMISV2Backend())

    assert results == [{"patient_id": bytes(range(16)), "age": 22}]


def test_backend_columns_have_correct_types(trino_database):
    columns_with_types = get_all_backend_columns_with_types(trino_database)
    assert_types_correct(columns_with_types, trino_database)


def get_all_backend_columns_with_types(trino_database):
    """
    For every column on every table we expose in the backend, yield the SQLAlchemy type
    instance we expect to use for that column together with the type information that
    database has for that column so we can check they're compatible
    """
    table_names = set()
    column_types = {}
    queries = []
    for table, columns in get_all_backend_columns(EMISV2Backend(), trino_database):
        table_names.add(table)
        column_types.update({(table, c.key): c.type for c in columns})
        # Construct a query which selects every column in the table
        select_query = sqlalchemy.select(*[c.label(c.key) for c in columns])
        # Write the results of that query into a temporary table (it will be empty but
        # that's fine, we just want the types)
        # Trino doesn't support actual temporary tables, so really this temp table is
        # a real table that we drop after the test
        temp_table_name = f"temp_{table}"
        temp_table = GeneratedTable.from_query(temp_table_name, select_query)
        queries.append(
            (temp_table_name, temp_table, CreateTableAs(temp_table, select_query))
        )
    # Create all the underlying tables in the database without populating them
    trino_database.setup(metadata=Patient.metadata)
    # Note: we really ought to have something like the setup/cleanup call below to
    # handle materialized query tables (which we happen not to have any of in the EMIS
    # backend at present). But the structure of the `queries` list doesn't currently
    # allow for this and I think there's a wider refactor here which would make this
    # problem go away so I'm going to punt on it for now.
    # queries = add_setup_and_cleanup_queries(queries)
    with trino_database.engine().connect() as connection:
        # Create our "temporary" tables
        for temp_table_name, temp_table, query in queries:
            connection.execute(query)
            # Get the column names, types and collations for all columns in those tables
            query = sqlalchemy.text(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name=:t
                """
            )
            results = list(connection.execute(query, {"t": temp_table_name}))
            table_name = temp_table_name.replace("temp_", "")
            for column, type_name in results:
                column_type = column_types[table_name, column]
                column_args = {"type": type_name}
                yield table_name, column, column_type, column_args

            # Drop the temp table
            temp_table.drop(trino_database.engine())


def test_registered_tests_are_exhaustive():
    assert_tests_exhaustive(EMISV2Backend())


@register_test_for(emisv2.patients)
def test_patients(select_all_emisv2):
    results = select_all_emisv2(
        Patient(
            _pk=1,
            patient_id=bytes(range(16)).decode("utf-8"),
            date_of_birth=datetime(2000, 1, 1, 0, 0, 0, 0),
            date_of_death=datetime(2023, 5, 12, 0, 0, 0, 0),
            sex="M",
        ),
    )
    assert results == [
        {
            "patient_id": bytes(range(16)),
            "date_of_birth": date(2000, 1, 1),
            "date_of_death": date(2023, 5, 12),
            "sex": "male",
        }
    ]


@register_test_for(emisv2.clinical_events)
def test_clinical_events(select_all_emisv2):
    results = select_all_emisv2(
        Observation(
            patient_id=bytes(range(16)).decode("utf-8"),
            effective_datetime=datetime(2023, 5, 12, 14, 30, 15, 0, tzinfo=UTC),
            numeric_value=80.0,
            snomed_concept_id=123456789,
        )
    )
    assert results == [
        {
            "patient_id": bytes(range(16)),
            "date": date(2023, 5, 12),
            "snomedct_code": "123456789",
            "numeric_value": 80.0,
        }
    ]


@register_test_for(emisv2.medications)
def test_medications(select_all_emisv2):
    results = select_all_emisv2(
        MedicationIssueRecord(
            patient_id=bytes(range(16)).decode("utf-8"),
            dmd_product_code_id=12354611500001104,
            effective_datetime=datetime(2023, 5, 12, 14, 30, 15, 0, tzinfo=UTC),
        )
    )
    assert results == [
        {
            "patient_id": bytes(range(16)),
            "date": date(2023, 5, 12),
            "dmd_code": "12354611500001104",
        }
    ]


@register_test_for(emisv2.practice_registrations)
def test_practice_registrations(select_all_emisv2):
    results = select_all_emisv2(
        Patient(
            patient_id=bytes(range(16)).decode("utf-8"),
            registration_start_datetime=datetime(2000, 2, 1, 0, 0, 0, 0),
            registration_end_datetime=None,
        ),
    )
    assert results == [
        {
            "patient_id": bytes(range(16)),
            "start_date": date(2000, 2, 1),
            "end_date": None,
        }
    ]


@register_test_for(emisv2.addresses)
def test_addresses(select_all_emisv2):
    results = select_all_emisv2(
        Patient(
            patient_id=bytes(range(16)).decode("utf-8"),
            registration_start_datetime=datetime(2000, 2, 1, 0, 0, 0, 0),
            registration_end_datetime=None,
            imd_rounded=11100,
            middle_level_super_output_area="E02000001",
        ),
    )
    assert results == [
        {
            "patient_id": bytes(range(16)),
            "start_date": date(2000, 2, 1),
            "end_date": None,
            "msoa_code": "E02000001",
            "imd_rounded": 11100,
        }
    ]


@pytest.mark.parametrize(
    "environ,expected",
    [
        pytest.param(
            {"EHRQL_PERMISSIONS": '["include_t1oo"]'},
            [
                {"patient_id": bytes([1] * 16), "birth_year": 2001},
                {"patient_id": bytes([2] * 16), "birth_year": 2002},
                {"patient_id": bytes([3] * 16), "birth_year": 2003},
                {"patient_id": bytes([4] * 16), "birth_year": 2004},
            ],
            id="with_permissions",
        ),
        pytest.param(
            {},
            [
                {"patient_id": bytes([3] * 16), "birth_year": 2003},
                {"patient_id": bytes([4] * 16), "birth_year": 2004},
            ],
            id="without_T1OO_permissions",
        ),
    ],
)
def test_t1oo_patients_excluded_as_specified(trino_engine, environ, expected):
    trino_engine.setup(
        Patient(
            _pk=1,
            patient_id=bytes([1] * 16).decode("utf-8"),
            date_of_birth=datetime(2001, 1, 1, 0, 0, 0, 0),
            is_consent_93c1=False,
        ),
        Patient(
            _pk=2,
            patient_id=bytes([2] * 16).decode("utf-8"),
            date_of_birth=datetime(2002, 1, 1, 0, 0, 0, 0),
            is_consent_93c1=False,
        ),
        Patient(
            _pk=3,
            patient_id=bytes([3] * 16).decode("utf-8"),
            date_of_birth=datetime(2003, 1, 1, 0, 0, 0, 0),
            is_consent_93c1=True,
        ),
        Patient(
            _pk=4,
            patient_id=bytes([4] * 16).decode("utf-8"),
            date_of_birth=datetime(2004, 1, 1, 0, 0, 0, 0),
        ),
    )

    from ehrql.tables import emisv2

    dataset = create_dataset()
    dataset.birth_year = emisv2.patients.date_of_birth.year
    dataset.define_population(dataset.birth_year >= 2000)

    results = trino_engine.extract(
        dataset,
        backend=EMISV2Backend(environ=environ),
    )

    assert list(results) == expected


@pytest.mark.parametrize(
    "environ,expected",
    [
        pytest.param(
            {"EHRQL_PERMISSIONS": '["include_t1oo"]'},
            [
                {"patient_id": bytes([1] * 16), "registration_start_year": 2001},
                {"patient_id": bytes([2] * 16), "registration_start_year": 2002},
                {"patient_id": bytes([3] * 16), "registration_start_year": 2003},
                {"patient_id": bytes([4] * 16), "registration_start_year": 2004},
            ],
            id="with_permissions",
        ),
        pytest.param(
            {},
            [
                {"patient_id": bytes([3] * 16), "registration_start_year": 2003},
                {"patient_id": bytes([4] * 16), "registration_start_year": 2004},
            ],
            id="without_T1OO_permissions",
        ),
    ],
)
def test_t1oo_patients_excluded_as_specified_when_population_definition_does_not_use_patients_table(
    trino_engine, environ, expected
):
    trino_engine.setup(
        Patient(
            _pk=1,
            patient_id=bytes([1] * 16).decode("utf-8"),
            registration_start_datetime=datetime(2001, 1, 1, 0, 0, 0, 0),
            is_consent_93c1=False,
        ),
        Patient(
            _pk=2,
            patient_id=bytes([2] * 16).decode("utf-8"),
            registration_start_datetime=datetime(2002, 1, 1, 0, 0, 0, 0),
            is_consent_93c1=False,
        ),
        Patient(
            _pk=3,
            patient_id=bytes([3] * 16).decode("utf-8"),
            registration_start_datetime=datetime(2003, 1, 1, 0, 0, 0, 0),
            is_consent_93c1=True,
        ),
        Patient(
            _pk=4,
            patient_id=bytes([4] * 16).decode("utf-8"),
            registration_start_datetime=datetime(2004, 1, 1, 0, 0, 0, 0),
        ),
    )

    from ehrql.tables import emisv2

    dataset = create_dataset()
    dataset.registration_start_year = (
        emisv2.practice_registrations.sort_by(emisv2.practice_registrations.start_date)
        .last_for_patient()
        .start_date.year
    )
    dataset.define_population(dataset.registration_start_year >= 2000)

    results = trino_engine.extract(
        dataset,
        backend=EMISV2Backend(environ=environ),
    )

    assert list(results) == expected
