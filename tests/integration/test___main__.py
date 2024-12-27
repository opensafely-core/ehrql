import contextlib
import json
import shutil
import sys
from pathlib import Path

import pytest

from ehrql.__main__ import (
    BACKEND_ALIASES,
    QUERY_ENGINE_ALIASES,
    backend_from_id,
    main,
    query_engine_from_id,
)
from ehrql.backends.base import SQLBackend
from ehrql.query_engines.base import BaseQueryEngine
from ehrql.query_engines.base_sql import BaseSQLQueryEngine
from ehrql.query_engines.debug import DebugQueryEngine
from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.utils.module_utils import get_sibling_subclasses
from tests.lib.inspect_utils import function_body_as_string


FIXTURES_PATH = Path(__file__).parents[1] / "fixtures" / "good_definition_files"


def test_assure(capsys):
    main(["assure", str(FIXTURES_PATH / "assurance.py")])
    out, _ = capsys.readouterr()
    assert "All OK" in out


def test_test_connection(mssql_database, capsys):
    env = {
        "BACKEND": "ehrql.backends.tpp.TPPBackend",
        "DATABASE_URL": mssql_database.host_url(),
    }
    argv = ["test-connection"]
    main(argv, env)
    out, _ = capsys.readouterr()
    assert "SUCCESS" in out


def test_dump_example_data(tmpdir):
    with contextlib.chdir(tmpdir):
        main(["dump-example-data"])
    filenames = [path.basename for path in (tmpdir / "example-data").listdir()]
    assert "patients.csv" in filenames


@pytest.mark.parametrize(
    "definition_type,definition_file",
    [
        ("dataset", FIXTURES_PATH / "dataset_definition.py"),
        ("measures", FIXTURES_PATH / "measure_definitions.py"),
        ("test", FIXTURES_PATH / "assurance.py"),
    ],
)
def test_serialize_definition(definition_type, definition_file, capsys):
    main(
        [
            "serialize-definition",
            "--definition-type",
            definition_type,
            str(definition_file),
        ]
    )
    stdout, stderr = capsys.readouterr()
    # We rely on tests elsewhere to ensure that the serialization is working correctly;
    # here we just want to check that we return valid JSON
    assert json.loads(stdout)
    # We shouldn't be producing any warnings or any other output
    assert stderr == ""


def test_generate_dataset_disallows_reading_file_outside_working_directory(
    tmp_path, monkeypatch, capsys
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
        main(["generate-dataset", str(dataset_file)])
    assert "is not contained within the directory" in str(e.value)


@pytest.mark.parametrize("legacy", [True, False])
def test_generate_dataset_passes_dummy_data_config(tmp_path, caplog, legacy):
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

    main(
        [
            "generate-dataset",
            str(dataset_file),
            "--output",
            str(tmp_path / "output.csv"),
        ]
    )

    logs = caplog.text
    assert "Attempting to generate 2 matching patients" in logs
    assert "timeout: 3s" in logs
    if legacy:
        assert "Using legacy dummy data generation" in logs
    else:
        assert "Using next generation dummy data generation" in logs


@pytest.mark.skipif(
    not sys.platform.startswith("linux"),
    reason="Subprocess isolation only works on Linux",
)
def test_isolation_report(capsys):
    main(["isolation-report"])
    assert json.loads(capsys.readouterr().out)


@pytest.mark.skipif(
    shutil.which("dot") is None,
    reason="Graphing requires Graphviz library",
)
def test_graph_query(tmpdir):  # pragma: no cover
    output_file = tmpdir / "query.svg"
    main(
        [
            "graph-query",
            str(FIXTURES_PATH / "dataset_definition.py"),
            "--output",
            str(output_file),
        ]
    )
    assert output_file.exists()


def test_all_query_engine_aliases_are_importable():
    for alias in QUERY_ENGINE_ALIASES.keys():
        assert query_engine_from_id(alias)


def test_all_backend_aliases_are_importable():
    for alias in BACKEND_ALIASES.keys():
        assert backend_from_id(alias)


def test_all_query_engines_have_an_alias():
    for cls in get_sibling_subclasses(BaseQueryEngine):
        if cls in [
            BaseSQLQueryEngine,
            InMemoryQueryEngine,
            DebugQueryEngine,
        ]:
            continue
        name = f"{cls.__module__}.{cls.__name__}"
        assert name in QUERY_ENGINE_ALIASES.values(), f"No alias defined for '{name}'"


def test_all_backends_have_an_alias():
    for cls in get_sibling_subclasses(SQLBackend):
        name = f"{cls.__module__}.{cls.__name__}"
        assert name in BACKEND_ALIASES.values(), f"No alias defined for '{name}'"


def test_all_backend_aliases_match_display_names():
    for alias in BACKEND_ALIASES.keys():
        assert backend_from_id(alias).display_name.lower() == alias
