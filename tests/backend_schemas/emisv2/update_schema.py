import json
import keyword
import os
import subprocess
import sys
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
SCHEMA_JSON = SCHEMA_DIR / "schema.json"
SCHEMA_CSV = SCHEMA_DIR / "schema.csv"
SCHEMA_PYTHON = SCHEMA_DIR / "schema.py"

HEADER = """
from sqlalchemy import types as t
from sqlalchemy.orm import DeclarativeBase, mapped_column
from trino.sqlalchemy import datatype as trdt


class Base(DeclarativeBase):
    "Common base class to signal that models below belong to the same database"
"""

# Filter to these tables and columns
TABLE_NAMES = {"patient", "medication_issue_record", "observation"}
COLUMN_NAMES = {
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


#################################################################
# FETCH (TODO: remove me)
#################################################################


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
    type_repr = f"{column.__class__.__module__}.{repr(column)}"
    return type_name, precision, length, type_repr


def fetch_schema_rows(inspector, schema, tables):
    schema_columns = []
    for table, columns in get_table_columns(inspector, schema, tables):
        for col in columns:
            col_type, col_precision, col_length, col_type_repr = get_column_metadata(
                col["type"]
            )
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
                    "ColumnTypeRepr": col_type_repr,
                }
            )

    print(schema_columns)
    return schema_columns


def write_schema_columns_to_json(schema_rows):
    with open(SCHEMA_JSON, "w") as f:
        json.dump(schema_rows, f)


# TODO column headers: TableName,ColumnName,ColumnType,Precision,Scale,MaxLength,IsNullable,CollationName
def fetch_schema():
    schema = "explorer_open_safely"
    trino = TrinoSqlAlchemy(username=username, token=token, environment=environment)
    inspector = inspect(trino.engine)
    tables = inspector.get_view_names(schema=schema)
    schema_columns = fetch_schema_rows(inspector, schema, tables)
    # TODO: Write to csv instead of as JSON
    write_schema_columns_to_json(schema_columns)


#################################################################
# BUILD (TODO: remove me)
#################################################################


def sort_columns(columns):
    # Assert column names are unique
    assert len({c["ColumnName"] for c in columns}) == len(columns)
    # Sort columns lexically except keep `Patient_ID` first
    return sorted(
        columns, key=lambda c: (c["ColumnName"] != "patient_id", c["ColumnName"])
    )


def read_schema():
    # TODO: This should presumably read from csv, not json
    with open(SCHEMA_JSON) as f:
        schema = json.load(f)
    by_table = {}
    for item in schema:
        by_table.setdefault(item["TableName"], []).append(item)
    return {name: sort_columns(columns) for name, columns in sorted(by_table.items())}


def is_valid(name):
    return name.isidentifier() and not keyword.iskeyword(name)


def class_name_for_table(name):
    assert is_valid(name), name
    return name.replace("_", " ").title().replace(" ", "")


def _add_precision(type_name, precision):
    if precision:
        return f"{type_name}(precision={precision})"
    return type_name


def format_timestamp(type_name, column):
    return _add_precision(type_name, column["Precision"])


def format_decimal_type(type_name, column):
    return _add_precision(type_name, column["Precision"])


def format_string_type(type_name, column):
    length = column["MaxLength"]
    if length:
        return f"{type_name}(length={length})"
    return type_name


# TODO: Not used; needs reviewing and then combining with definition_for_column
def get_column_type(column):
    # TODO: Move this to the top of the script
    TYPE_MAP = {
        "timestamp": lambda col: format_timestamp("trdt.TIMESTAMP", col),
        "bigint": lambda _: "t.BIGINT",
        "varchar": lambda col: format_string_type("t.VARCHAR", col),
        "varbinary": lambda _: "t.VARBINARY",
        "decimal": lambda col: format_decimal_type("t.DECIMAL", col),
    }
    type_formatter = TYPE_MAP[column["ColumnType"].lower()]
    return type_formatter(column)


def definition_for_column(column):
    type_ = (
        column["ColumnTypeRepr"]
        .replace("trino.sqlalchemy.datatype.", "trdt.")
        .replace("sqlalchemy.sql.sqltypes.", "t.")
        .replace("()", "")  # Remove empty parentheses from types that don't need them
    )
    return f"mapped_column({type_})"


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
    for table, columns in read_schema().items():
        if table not in TABLE_NAMES:
            continue
        lines.extend(["", ""])
        lines.append(f"class {class_name_for_table(table)}(Base):")
        lines.append(f"    __tablename__ = {table!r}")
        lines.append("    _pk = mapped_column(t.Integer, primary_key=True)")
        lines.append("")
        for column in columns:
            attr_name = column["ColumnName"]
            if attr_name not in COLUMN_NAMES[table]:
                continue
            lines.append(f"    {attr_name} = {definition_for_column(column)}")
    write_schema(lines)


if __name__ == "__main__":
    # TODO: This is a stub
    if username and token:
        fetch_schema()
    else:
        build_schema()
