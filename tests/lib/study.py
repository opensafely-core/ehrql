import csv
import gzip
import hashlib
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import urlretrieve

from pyarrow.feather import read_table

from databuilder.__main__ import main
from databuilder.file_formats import get_file_extension


class Cache:
    _cache_expiry = timedelta(days=1)

    def get(self, url):
        path = self._cache_path(url)
        if not path.exists() or self._is_expired(
            path
        ):  # pragma: no cover (varies between runs)
            urlretrieve(url, path)
        return path

    def _cache_path(self, url):
        return self._cache_dir() / hashlib.sha1(url.encode()).hexdigest()

    @staticmethod
    def _cache_dir():
        p = Path(__file__)
        assert p.parent.match(
            "*/tests/lib"
        ), "Directory structure has changed, this code needs updating"
        cache = p.parent.parent.parent / "cache"
        cache.mkdir(exist_ok=True)
        return cache

    def _is_expired(self, p):  # pragma: no cover (not called if file missing)
        return p.stat().st_mtime < (datetime.now() - self._cache_expiry).timestamp()


def fetch_repo(repo, branch, root):
    tarball = Cache().get(f"https://github.com/{repo}/tarball/{branch}")
    shutil.unpack_archive(tarball, root, format="gztar")

    # The name of the directory inside the tarball is a bit unpredictable, like
    # opensafely-test-age-distribution-8308211. So we grab it with a glob. We then use
    # that directory as the workspace rather than moving the contents to another
    # directory with a known name.
    unpacked = list(root.glob("*"))
    assert len(unpacked) == 1, unpacked
    workspace = unpacked[0]

    return workspace


class Study:
    def __init__(self, root, containers, image):
        self._root = root
        self._containers = containers
        self._image = image

    def setup_from_repo(self, repo, branch, definition_path):
        self._workspace = fetch_repo(repo, branch, self._root)
        self._definition_path = self._workspace / definition_path

    def setup_from_string(self, definition):
        self._workspace = self._root
        self._definition_path = self._workspace / "dataset.py"
        self._definition_path.write_text(definition)

    def generate(self, database, backend, extension=".csv"):
        self._dataset_path = self._workspace / f"dataset{extension}"

        env = {
            "DATABASE_URL": database.host_url(),
            "OPENSAFELY_BACKEND": backend,
        }

        main(
            self._generate_command(self._definition_path, self._dataset_path),
            environ=env,
        )

    def generate_in_docker(self, database, backend, extension=".csv"):
        self._dataset_path = self._workspace / f"dataset{extension}"
        environment = {
            "DATABASE_URL": database.container_url(),
            "OPENSAFELY_BACKEND": backend,
        }
        self._run_in_docker(
            command=self._generate_command(
                self._docker_path(self._definition_path),
                self._docker_path(self._dataset_path),
            ),
            environment=environment,
        )

    @staticmethod
    def _generate_command(definition, dataset):
        return [
            "generate-dataset",
            str(definition),
            "--output",
            str(dataset),
        ]

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
            "databuilder.backends.tpp.TPPBackend",
            "--output",
            str(output),
            str(definition),
        ]

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
