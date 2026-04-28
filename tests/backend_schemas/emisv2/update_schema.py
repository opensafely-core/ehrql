# pragma: no cover file
import csv
import os
from pathlib import Path

import urllib3
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker


urllib3.disable_warnings()

STAGING_URL = "explorerplus.stagingemisinsights.co.uk"
SCHEMA = "explorer_open_safely"

SCHEMA_DIR = Path(__file__).parent
SCHEMA_CSV = SCHEMA_DIR / "schema.csv"


class TrinoSqlAlchemy:
    def __init__(self, username, token, host) -> None:
        self.user = username
        self.token = token
        self.host = host
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


def get_table_columns(inspector):
    tables = inspector.get_view_names(schema=SCHEMA)
    for table in tables:
        table_schema = inspector.get_columns(table_name=table, schema=SCHEMA)
        yield table, table_schema


def get_column_metadata(column):
    type_name = type(column).__name__
    precision = getattr(column, "precision", None)
    length = getattr(column, "length", None)
    scale = getattr(column, "scale", None)
    timezone = getattr(column, "timezone", None)
    return {
        "type_name": type_name,
        "precision": precision,
        "scale": scale,
        "length": length,
        "timezone": timezone,
    }


def fetch_schema_rows(inspector):
    schema_rows = []

    for table, columns in get_table_columns(inspector):
        for col in columns:
            metadata = get_column_metadata(col["type"])
            assert col["nullable"] is True
            schema_rows.append(
                {
                    "TableName": table,
                    "ColumnName": col["name"],
                    "ColumnType": metadata["type_name"],
                    "Precision": metadata["precision"],
                    "Scale": metadata["scale"],
                    "MaxLength": metadata["length"],
                    "Timezone": metadata["timezone"],
                }
            )
    return schema_rows


def write_schema_rows_to_csv(schema_rows):
    with open(SCHEMA_CSV, "w") as f:
        headers = schema_rows[0].keys()
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(schema_rows)


def fetch_schema():
    # The username and token must be obtained from the EMIS staging environment
    username = os.environ.get("EXA_USERNAME")
    token = os.environ.get("EXA_TOKEN")

    trino = TrinoSqlAlchemy(username, token, STAGING_URL)
    inspector = inspect(trino.engine)
    schema_rows = fetch_schema_rows(inspector)
    write_schema_rows_to_csv(schema_rows)


if __name__ == "__main__":
    fetch_schema()
