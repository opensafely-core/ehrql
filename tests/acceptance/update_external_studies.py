"""
This is a utility script which it's convenient to have sitting alongside the test it
supports but which isn't actually executed by the test suite — hence the "no covers"
"""

import shutil  # pragma: no cover
import tarfile  # pragma: no cover
from fnmatch import fnmatch  # pragma: no cover
from pathlib import Path  # pragma: no cover
from urllib.request import urlopen  # pragma: no cover

from .test_external_studies import EXTERNAL_STUDIES, STUDY_DIR  # pragma: no cover


def update_external_studies():  # pragma: no cover
    if STUDY_DIR.exists():
        shutil.rmtree(STUDY_DIR)
    for name, config in EXTERNAL_STUDIES.items():
        target_dir = STUDY_DIR / name
        tarball_url = f"https://github.com/{config['repo']}/tarball/{config['branch']}"
        download_files(target_dir, tarball_url, config["file_globs"])
        create_dummy_files(target_dir, config.get("dummy_files", []))


def download_files(target_dir, tarball_url, file_globs):  # pragma: no cover
    for name, read_bytes in get_files_from_remote_tarball(tarball_url):
        # Strip the arbitrary leading directory from the tar path
        path = name.partition("/")[2]
        if any(fnmatch(path, pattern) for pattern in file_globs):
            out_path = target_dir / path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(read_bytes())


def get_files_from_remote_tarball(url):  # pragma: no cover
    with urlopen(url) as stream:
        with tarfile.open(fileobj=stream, mode="r:gz") as tarobj:
            while tar_info := tarobj.next():
                if tar_info.isfile():
                    yield tar_info.name, lambda: tarobj.extractfile(tar_info).read()


def create_dummy_files(target_dir, dummy_files):  # pragma: no cover
    """
    Ensure any necessary filepaths exist (e.g. output files that are referenced in a
    dataset definition
    """
    for dummy_file in dummy_files:
        dummy_filepath = Path(target_dir) / dummy_file
        dummy_filepath.parent.mkdir(exist_ok=True, parents=True)
        dummy_filepath.touch(exist_ok=True)


if __name__ == "__main__":
    update_external_studies()
