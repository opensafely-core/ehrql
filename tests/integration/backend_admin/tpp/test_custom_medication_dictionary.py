import pytest
import sqlalchemy

from ehrql.backend_admin.tpp import custom_medication_dictionary
from ehrql.backends.tpp import TPPBackend
from tests.backend_schemas.tpp.schema import CustomMedicationDictionary


@pytest.fixture()
def mapping_csv_path(tmp_path, monkeypatch):
    mapping_csv_path = tmp_path / "custom_medication_dictionary.csv"
    # Nb. this is going to affect the CSV path for everything else under test
    monkeypatch.setattr(
        custom_medication_dictionary,
        "CUSTOM_MEDICATION_DICTIONARY_CSV",
        mapping_csv_path,
    )
    return mapping_csv_path


@pytest.fixture()
def write_mapping_csv(mapping_csv_path):
    def _write_mapping_csv(rows):
        mapping_csv_path.write_text("\n".join(",".join(row) for row in rows))

    return _write_mapping_csv


@pytest.fixture()
def custom_med_dict(mssql_database):
    backend = TPPBackend(environ={"TEMP_DATABASE_NAME": "temp_tables"})
    engine = backend.get_query_engine(dsn=mssql_database.host_url()).engine
    with engine.connect() as connection:
        custom_med_dict = custom_medication_dictionary.CustomMedicationDictionary(
            connection, "temp_tables"
        )
        yield custom_med_dict


@pytest.fixture()
def setup_initial_data(mssql_database):
    mssql_database.setup(
        CustomMedicationDictionary(DMD_ID="111111", MultilexDrug_ID="a"),
        CustomMedicationDictionary(DMD_ID="222222", MultilexDrug_ID="b"),
    )


def test_get_custom_medication_dictionary(custom_med_dict, setup_initial_data):
    assert custom_med_dict.get() == [
        ("111111", "a"),
        ("222222", "b"),
    ]


def test_update_custom_medication_dictionary_no_existing_table(
    custom_med_dict, write_mapping_csv
):
    with pytest.raises(sqlalchemy.exc.ProgrammingError, match="Invalid object name"):
        custom_med_dict.get()
    write_mapping_csv(
        [
            ("DMD_ID", "MultilexDrug_ID", "FullName"),
            ("111111", "a", "full name for a"),
            ("222222", "b", "full name for b"),
        ]
    )
    custom_med_dict.update()
    assert custom_med_dict.get() == [
        ("111111", "a"),
        ("222222", "b"),
    ]


def test_update_custom_medication_dictionary_table_dropped(
    custom_med_dict, write_mapping_csv, setup_initial_data
):
    assert custom_med_dict.get() == [
        ("111111", "a"),
        ("222222", "b"),
    ]
    # Overwrite the table with new contents
    write_mapping_csv(
        [
            ("DMD_ID", "MultilexDrug_ID", "FullName"),
            ("333333", "c", "full name for c"),
            ("444444", "d", "full name for d"),
        ]
    )
    custom_med_dict.update()

    assert custom_med_dict.get() == [
        ("333333", "c"),
        ("444444", "d"),
    ]


def test_update_custom_medication_dictionary_table_not_dropped(
    custom_med_dict, write_mapping_csv, setup_initial_data
):
    assert custom_med_dict.get() == [
        ("111111", "a"),
        ("222222", "b"),
    ]
    # Force the INSERT to error, by passing a DM+D ID that's too long.
    # The transaction should rollback.
    write_mapping_csv(
        [
            ("DMD_ID", "MultilexDrug_ID", "FullName"),
            (f"{'5' * 60}", "e", "full name for e"),
        ],
    )
    with pytest.raises(sqlalchemy.exc.OperationalError):
        custom_med_dict.update()

    # Table still contains the original data
    get_data = custom_med_dict.get()
    assert get_data == [
        ("111111", "a"),
        ("222222", "b"),
    ], get_data


def test_custom_medication_dictionary_run_get(
    mssql_database, setup_initial_data, capsys
):
    custom_medication_dictionary.run(
        backend_class=TPPBackend,
        dsn=mssql_database.host_url(),
        action="get",
        environ={"TEMP_DATABASE_NAME": "temp_tables"},
        user_args=[],
    )

    assert capsys.readouterr().out.strip() == str([("111111", "a"), ("222222", "b")])


def test_custom_medication_dictionary_run_update(
    mssql_database, write_mapping_csv, capsys
):
    write_mapping_csv(
        [
            ("DMD_ID", "MultilexDrug_ID", "FullName"),
            ("333333", "c", "full name for c"),
            ("444444", "d", "full name for d"),
        ]
    )
    custom_medication_dictionary.run(
        backend_class=TPPBackend,
        dsn=mssql_database.host_url(),
        action="update",
        environ={"TEMP_DATABASE_NAME": "temp_tables"},
        user_args=[],
    )

    assert capsys.readouterr().out.strip() == "OK"
