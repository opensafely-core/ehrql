import csv
import gzip
import os
from pathlib import Path

from pyarrow.feather import read_table

from ehrql.__main__ import main
from ehrql.file_formats import get_file_extension


class Study:
    def __init__(self, root, containers, image):
        self._root = root
        self._containers = containers
        self._image = image

    def setup_from_string(self, definition):
        self._workspace = self._root
        self._definition_path = self._workspace / "dataset.py"
        self._definition_path.write_text(definition)

    def generate(self, database, backend, extension=".csv", **kwargs):
        self._dataset_path = self._workspace / f"dataset{extension}"

        env = {
            "DATABASE_URL": database.host_url() if database else "",
            "OPENSAFELY_BACKEND": backend,
        }
        # Needed for running tests locally on non-Linux
        pass_through_vars = ["EHRQL_ISOLATE_USER_CODE"]
        for name in pass_through_vars:
            if name in os.environ:  # pragma: no cover
                env[name] = os.environ[name]

        main(
            self._generate_command(
                self._definition_path,
                self._dataset_path,
                **kwargs,
            ),
            environ=env,
        )

    def generate_in_docker(self, database, backend, extension=".csv", **kwargs):
        self._dataset_path = self._workspace / f"dataset{extension}"
        environment = {
            "DATABASE_URL": database.container_url() if database else "",
            "OPENSAFELY_BACKEND": backend,
        }
        self._run_in_docker(
            command=self._generate_command(
                self._docker_path(self._definition_path),
                self._docker_path(self._dataset_path),
                **kwargs,
            ),
            environment=environment,
        )

    @staticmethod
    def _generate_command(definition, dataset, **kwargs):
        args = [
            "generate-dataset",
            str(definition),
            "--output",
            str(dataset),
        ]
        user_args = kwargs.pop("user_args", None)
        for key, value in kwargs.items():
            args.extend([f"--{key.replace('_' , '-')}", value])
        if user_args is not None:
            args.append("--")
            for key, value in user_args.items():
                args.extend([f"--{key.replace('_' , '-')}", value])
        return args

    def dump_dataset_sql(self):
        self._output_path = self._workspace / "queries.sql"
        main(self._dump_dataset_sql_command(self._definition_path, self._output_path))

    def dump_dataset_sql_in_docker(self):
        self._output_path = self._workspace / "queries.sql"
        self._run_in_docker(
            command=self._dump_dataset_sql_command(
                self._docker_path(self._definition_path),
                self._docker_path(self._output_path),
            )
        )

    @staticmethod
    def _dump_dataset_sql_command(definition, output):
        return [
            "dump-dataset-sql",
            "--backend",
            "ehrql.backends.tpp.TPPBackend",
            "--output",
            str(output),
            str(definition),
        ]

    def create_dummy_tables(self, dummy_tables_path):
        main(
            ["create-dummy-tables", str(self._definition_path), str(dummy_tables_path)]
        )

    def _docker_path(self, path):
        return Path("/workspace") / path.relative_to(self._workspace)

    def _run_in_docker(self, command, environment=None):
        environment = environment or {}
        self._containers.run_fg(
            image=self._image,
            command=command,
            environment=environment,
            volumes={self._workspace: {"bind": "/workspace", "mode": "rw"}},
        )

    def results(self):
        extension = get_file_extension(self._dataset_path)
        if extension == ".csv":
            with open(self._dataset_path) as f:
                return list(csv.DictReader(f))
        elif extension == ".csv.gz":
            with gzip.open(self._dataset_path, "rt") as f:
                return list(csv.DictReader(f))
        elif extension == ".arrow":
            return read_table(str(self._dataset_path)).to_pylist()
        else:
            assert False
