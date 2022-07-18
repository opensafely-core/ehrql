#!/usr/bin/env python
"""
Create any tables referenced by `dataset_definition` in `sqlite_file`
"""
import sys
from argparse import ArgumentParser
from pathlib import Path
from urllib.parse import quote

import sqlalchemy

# Hack to work around the fact that these scripts aren't in the top level directory
sys.path.insert(0, str(Path(__file__).parents[1].resolve()))

from databuilder.main import get_query_engine, load_definition
from databuilder.query_language import compile
from databuilder.query_model import SelectPatientTable, SelectTable, all_nodes
from tests.lib.util import orm_class_from_schema


def main(args):
    parser = ArgumentParser(description=__doc__.partition("\n\n")[0])
    parser.add_argument("sqlite_file", type=Path)
    parser.add_argument("dataset_definition", type=Path)
    options = parser.parse_args(args)
    create_schema(**vars(options))


def create_schema(sqlite_file, dataset_definition):
    definition = load_definition(dataset_definition)
    variables = compile(definition)
    table_nodes = get_table_nodes(variables)
    metadata = create_orm_metadata_from_table_nodes(table_nodes)
    engine = get_sqlalchemy_engine(sqlite_file)
    metadata.create_all(engine)


def get_table_nodes(variables):
    table_nodes = set()
    for variable in variables.values():
        for node in all_nodes(variable):
            if isinstance(node, (SelectTable, SelectPatientTable)):
                table_nodes.add(node)
    return table_nodes


def create_orm_metadata_from_table_nodes(table_nodes):
    Base = sqlalchemy.orm.declarative_base()
    for node in table_nodes:
        orm_class_from_schema(Base, node.name, node.schema)
    return Base.metadata


def get_sqlalchemy_engine(sqlite_file):
    database_url = f"file:///{quote(str(sqlite_file.resolve()))}"
    query_engine = get_query_engine(
        dsn=database_url,
        backend_id=None,
        query_engine_id="databuilder.query_engines.sqlite.SQLiteQueryEngine",
        environ={},
    )
    return query_engine.engine


if __name__ == "__main__":
    main(sys.argv[1:])
