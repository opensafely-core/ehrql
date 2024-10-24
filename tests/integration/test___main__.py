import contextlib
import json
import os
import shutil
import sys
import textwrap
from pathlib import Path
from unittest.mock import patch

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
from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.query_engines.sandbox import SandboxQueryEngine
from ehrql.utils.module_utils import get_sibling_subclasses


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
    "command_line_arguments,dummy_tables_path",
    [
        (["sandbox"], "example-data"),
        (["sandbox", "some-tables"], "some-tables"),
    ],
)
def test_sandbox_dummy_tables_path_exists(
    command_line_arguments, dummy_tables_path, tmpdir
):
    with contextlib.chdir(tmpdir), patch("ehrql.sandbox.run") as run:
        os.mkdir(dummy_tables_path)
        main(command_line_arguments)
        run.assert_called_once_with(Path(dummy_tables_path))


def test_sandbox_dummy_tables_path_specified_but_does_not_exist(tmpdir):
    with contextlib.chdir(tmpdir):
        with pytest.raises(SystemExit):
            main(["sandbox", "some-tables"])


def test_sandbox_dump_example_data(tmpdir):
    with (
        contextlib.chdir(tmpdir),
        patch("ehrql.sandbox.run") as run,
        patch("builtins.input", return_value="y") as mock_input,
    ):
        assert not os.path.exists("example-data")
        main(["sandbox"])
        mock_input.assert_called_once()
        assert os.path.exists("example-data")
        run.assert_called_once_with(Path("example-data"))


def test_sandbox_dump_example_data_rejected():
    with patch("builtins.input", return_value="n") as mock_input:
        assert not os.path.exists("example-data")
        with pytest.raises(SystemExit):
            main(["sandbox"])
        mock_input.assert_called_once()
        assert not os.path.exists("example-data")


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

    code = textwrap.dedent(
        f"""\
        from ehrql import create_dataset
        from ehrql.tables import table_from_file, PatientFrame, Series

        @table_from_file({str(csv_file)!r})
        class test_table(PatientFrame):
            i = Series(int)

        dataset = create_dataset()
        dataset.define_population(test_table.exists_for_patient())
        dataset.configure_dummy_data(population_size=2)
        dataset.i = test_table.i
        """
    )
    dataset_file = tmp_path / "sub_dir" / "dataset_definition.py"
    dataset_file.parent.mkdir(parents=True, exist_ok=True)
    dataset_file.write_text(code)

    monkeypatch.chdir(dataset_file.parent)
    with pytest.raises(Exception) as e:
        main(["generate-dataset", str(dataset_file)])
    assert "is not contained within the directory" in str(e.value)


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
            SandboxQueryEngine,
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
