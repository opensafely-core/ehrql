# pragma: no cover file
import csv
import keyword
import os
import subprocess
import sys
from pathlib import Path

import urllib3
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker


urllib3.disable_warnings()

STAGING_URL = "explorerplus.stagingemisinsights.co.uk"
SCHEMA = "explorer_open_safely"

SCHEMA_DIR = Path(__file__).parent
SCHEMA_CSV = SCHEMA_DIR / "schema.csv"
SCHEMA_PYTHON = SCHEMA_DIR / "schema.py"

HEADER = """
from sqlalchemy import types as t
from sqlalchemy.orm import DeclarativeBase, mapped_column
from trino.sqlalchemy import datatype as trdt


class Base(DeclarativeBase):
    "Common base class to signal that models below belong to the same database"
"""
TYPE_MAP = {
    "bigint": lambda _: "t.BIGINT",
    "boolean": lambda _: "t.BOOLEAN",
    "date": lambda _: "t.DATE",
    "decimal": lambda col: format_decimal_type("t.DECIMAL", col),
    "double": lambda _: "t.DOUBLE",
    "integer": lambda _: "t.Integer",
    "real": lambda _: "t.REAL",
    "varbinary": lambda _: "t.VARBINARY",
    "varchar": lambda col: format_string_type("t.VARCHAR", col),
    "timestamp": lambda col: format_timestamp_type("trdt.TIMESTAMP", col),
}

# Only build these tables and columns
INCLUDED_TABLES_AND_COLUMNS = {
    "patient": {
        "patient_id",
        "date_of_birth",
        "date_of_death",
        "sex",
    },
    "medication_issue_record": {
        "patient_id",
        "dmd_product_code_id",
        "effective_datetime",
    },
    "observation": {
        "patient_id",
        "effective_datetime",
        "snomed_concept_id",
        "numeric_value",
    },
}


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


def read_schema_rows_from_csv():
    with open(SCHEMA_CSV) as f:
        schema = list(csv.DictReader(f))
    by_table = {}
    for item in schema:
        by_table.setdefault(item["TableName"], []).append(item)
    return {name: sort_columns(columns) for name, columns in sorted(by_table.items())}


def sort_columns(columns):
    # Assert column names are unique
    assert len({c["ColumnName"] for c in columns}) == len(columns)
    # Sort columns lexically except keep `patient_id` first
    return sorted(
        columns, key=lambda c: (c["ColumnName"] != "patient_id", c["ColumnName"])
    )


def is_valid(name):
    return name.isidentifier() and not keyword.iskeyword(name)


def class_name_for_table(name):
    assert is_valid(name), name
    return name.replace("_", " ").title().replace(" ", "")


def format_decimal_type(type_name, column):
    return f"{type_name}(precision={column['Precision']}, scale={column['Scale']})"


def format_string_type(type_name, column):
    if length := column["MaxLength"]:
        return f"{type_name}(length={length})"
    return type_name


def format_timestamp_type(type_name, column):
    args = [f"precision={column['Precision']}"]
    if timezone := column["Timezone"]:
        args.append(f"timezone={timezone}")
    return f"{type_name}({', '.join(args)})"


def definition_for_column(column):
    type_formatter = TYPE_MAP[column["ColumnType"].lower()]
    return f"mapped_column({type_formatter(column)})"


def ruff_format(code):
    process = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "-"],
        check=True,
        text=True,
        capture_output=True,
        input=code,
    )
    return process.stdout


def write_schema(lines):
    code = "\n".join([HEADER] + lines)
    code = ruff_format(code)
    SCHEMA_PYTHON.write_text(code)


def build_schema():
    lines = []
    schema = read_schema_rows_from_csv()
    for table, columns in schema.items():
        if table not in INCLUDED_TABLES_AND_COLUMNS:
            continue
        lines.extend(["", ""])
        lines.append(f"class {class_name_for_table(table)}(Base):")
        lines.append(f"    __tablename__ = {table!r}")
        lines.append("    _pk = mapped_column(t.Integer, primary_key=True)")
        lines.append("")
        included_columns = INCLUDED_TABLES_AND_COLUMNS[table]
        for column in columns:
            attr_name = column["ColumnName"]
            if attr_name not in included_columns:
                continue
            lines.append(f"    {attr_name} = {definition_for_column(column)}")
    write_schema(lines)


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else None
    if command == "fetch":
        fetch_schema()
    elif command == "build":
        build_schema()
    else:
        raise RuntimeError(f"Unknown command: {command}; valid commands: fetch, build")
