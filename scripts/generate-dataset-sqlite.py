#!/usr/bin/env python
"""
Wrapper around `generate-dataset` to run it against a SQLite file and write CSV to stdout
"""
import os
import sys
from argparse import ArgumentParser
from pathlib import Path
from urllib.parse import quote

# Hack to work around the fact that these scripts aren't in the top level directory
sys.path.insert(0, str(Path(__file__).parents[1].resolve()))

from databuilder.__main__ import main as databuilder_main


def main(args, environ):
    parser = ArgumentParser(description=__doc__.partition("\n\n")[0])
    parser.add_argument("sqlite_file", type=Path)
    parser.add_argument("dataset_definition", type=Path)
    options = parser.parse_args(args)
    generate_dataset_sqlite(**vars(options))


def generate_dataset_sqlite(sqlite_file, dataset_definition):
    databuilder_main(
        [
            "generate-dataset",
            "--dataset-definition",
            str(dataset_definition),
            "--output",
            "/dev/stdout",
        ],
        {"DATABASE_URL": f"file:///{quote(str(sqlite_file.resolve()))}"},
    )


if __name__ == "__main__":
    main(sys.argv[1:], environ=os.environ)
