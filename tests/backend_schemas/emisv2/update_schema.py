import os
from pathlib import Path

import urllib3
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker


urllib3.disable_warnings()

# TODO: improve just file update-emis-v2-schema recipe. set up dotenv sample (with env variables: staging url, username and token placeholders)


environment = "staging"
username = os.environ.get("EXA_USERNAME")
token = os.environ.get("EXA_TOKEN")

SCHEMA_DIR = Path(__file__).parent
SCHEMA_CSV = SCHEMA_DIR / "schema.csv"


class TrinoSqlAlchemy:
    environments = {
        "staging": "explorerplus.stagingemisinsights.co.uk",
    }

    def __init__(self, token, username, environment=environment) -> None:
        self.user = username
        self.token = token
        self.host = self.environments[environment]
        self.port = 443
        self.catalog = "hive"
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = self.get_session()
        return self._session

    def get_session(self):
        conf = (
            f"trino://{self.user}:{self.token}@{self.host}:{self.port}/{self.catalog}"
        )
        args = {"http_scheme": "https", "verify": False, "request_timeout": 90}
        engine = create_engine(conf, connect_args=args)
        session_cls = sessionmaker(bind=engine)
        return session_cls()

    @property
    def engine(self):
        return self.session.get_bind()


def get_table_columns(inspector, schema, tables):
    for table in tables:
        table_schema = inspector.get_columns(table_name=table, schema=schema)
        yield table, table_schema


def get_column_metadata(column):
    type_name = type(column).__name__
    precision = getattr(column, "precision", None)
    length = getattr(column, "length", None)
    return type_name, precision, length


def fetch_schema_rows(inspector, schema, tables):
    schema_columns = []
    for table, columns in get_table_columns(inspector, schema, tables):
        for col in columns:
            col_type, col_precision, col_length = get_column_metadata(col["type"])
            if not col["nullable"]:  # TODO: tmp delete if condition is never met
                print(f"Table: {table} \n {col}")
                assert False

            # TODO: figure out if timezone is needed
            schema_columns.append(
                {
                    "TableName": table,
                    "ColumnName": col["name"],
                    "ColumnType": col_type,
                    "Precision": col_precision,
                    # "Scale": scale, #TODO : tbc
                    "MaxLength": col_length,
                }
            )

    result = print(schema_columns)
    return result


# TODO column headers: TableName,ColumnName,ColumnType,Precision,Scale,MaxLength,IsNullable,CollationName
def fetch_schema():
    schema = "explorer_open_safely"
    trino = TrinoSqlAlchemy(username=username, token=token, environment=environment)
    inspector = inspect(trino.engine)
    tables = inspector.get_view_names(schema=schema)
    fetch_schema_rows(inspector, schema, tables)


if __name__ == "__main__":
    # TODO: This is a stub
    if username and token:
        fetch_schema()
