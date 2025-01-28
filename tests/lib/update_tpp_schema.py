import csv
import keyword
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests


SERVER_URL = "https://jobs.opensafely.org"
WORKSPACE_NAME = "tpp-database-schema"
OUTPUTS_INDEX_URL = f"{SERVER_URL}/opensafely-internal/{WORKSPACE_NAME}/outputs/"

SCHEMA_DIR = Path(__file__).parent
SCHEMA_CSV = SCHEMA_DIR / "tpp_schema.csv"
SCHEMA_PYTHON = SCHEMA_DIR / "tpp_schema.py"
DATA_DICTIONARY_CSV = SCHEMA_DIR / "tpp_data_dictionary.csv"
DECISION_SUPPORT_REF_CSV = SCHEMA_DIR / "tpp_decision_support_reference.csv"

TYPE_MAP = {
    "bit": (0, lambda _: "t.Boolean"),
    "tinyint": (0, lambda _: "t.SMALLINT"),
    "int": (0, lambda _: "t.Integer"),
    "bigint": (0, lambda _: "t.BIGINT"),
    "numeric": (0, lambda _: "t.Numeric"),
    "float": (0.0, lambda _: "t.Float"),
    "real": (0.0, lambda _: "t.REAL"),
    "date": ("9999-12-31", lambda _: "t.Date"),
    "time": ("00:00:00", lambda _: "t.Time"),
    "datetime": ("9999-12-31T00:00:00", lambda _: "t.DateTime"),
    "char": ("", lambda col: format_string_type("t.CHAR", col)),
    "varchar": ("", lambda col: format_string_type("t.VARCHAR", col)),
    "varbinary": (b"", lambda col: format_binary_type("t.VARBINARY", col)),
}


HEADER = """\
# This file is auto-generated: DO NOT EDIT IT
#
# To rebuild run:
#
#   python tests/lib/update_tpp_schema.py build
#

from sqlalchemy import types as t
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    "Common base class to signal that models below belong to the same database"


# This table isn't included in the schema definition TPP provide for us because it isn't
# created or managed by TPP. Instead we create and populate this table ourselves,
# currently via a command in Cohort Extractor though this may eventually be moved to a
# new repo:
# [1]: https://github.com/opensafely-core/cohort-extractor/blob/dd681275/cohortextractor/update_custom_medication_dictionary.py
class CustomMedicationDictionary(Base):
    __tablename__ = "CustomMedicationDictionary"
    # Because we don't have write privileges on the main TPP database schema this table
    # lives in our "temporary tables" database. To mimic this as closely as possible in
    # testing we create it in a separate schema from the other tables.
    __table_args__ = {"schema": "temp_tables.dbo"}

    _pk = mapped_column(t.Integer, primary_key=True)

    DMD_ID = mapped_column(t.VARCHAR(50, collation="Latin1_General_CI_AS"))
    MultilexDrug_ID = mapped_column(t.VARCHAR(767, collation="Latin1_General_CI_AS"))
"""


def fetch_schema_and_data_dictionary():
    # There's currently no API to get the latest output from a workspace so we use a
    # regex to extract output IDs from the workspace's outputs page.
    index_page = requests.get(OUTPUTS_INDEX_URL)
    url_path = urlparse(index_page.url).path.rstrip("/")
    escaped_path = re.escape(url_path)
    url_re = re.compile(rf"{escaped_path}/(\d+)/")
    ids = url_re.findall(index_page.text)
    max_id = max(map(int, ids))
    # Once we have the ID we can fetch the output manifest using the API
    outputs_api = f"{SERVER_URL}/api/v2/workspaces/{WORKSPACE_NAME}/snapshots/{max_id}"
    outputs = requests.get(outputs_api, headers={"Accept": "application/json"}).json()
    # And that gives us the URLs for the files
    file_urls = {f["name"]: f["url"] for f in outputs["files"]}
    rows_url = urljoin(SERVER_URL, file_urls["output/rows.csv"])
    SCHEMA_CSV.write_text(requests.get(rows_url).text)
    data_dictionary_url = urljoin(SERVER_URL, file_urls["output/data_dictionary.csv"])
    DATA_DICTIONARY_CSV.write_text(requests.get(data_dictionary_url).text)
    decision_support_ref_url = urljoin(
        SERVER_URL, file_urls["output/decision_support_value_reference.csv"]
    )
    DECISION_SUPPORT_REF_CSV.write_text(requests.get(decision_support_ref_url).text)


def build_schema():
    lines = []
    for table, columns in read_schema().items():
        lines.extend(["", ""])
        lines.append(f"class {class_name_for_table(table)}(Base):")
        lines.append(f"    __tablename__ = {table!r}")
        lines.append("    _pk = mapped_column(t.Integer, primary_key=True)")
        lines.append("")
        for column in columns:
            attr_name = attr_name_for_column(column["ColumnName"])
            lines.append(f"    {attr_name} = {definition_for_column(column)}")
    write_schema(lines)


def read_schema():
    with SCHEMA_CSV.open(newline="") as f:
        schema = list(csv.DictReader(f))
    by_table = {}
    for item in schema:
        by_table.setdefault(item["TableName"], []).append(item)
    # We don't include the schema information table in the schema information because
    #  a) where would this madness end?
    #  b) it contains some weird types like `sysname` that we don't want to have to
    #     worry about.
    del by_table["OpenSAFELYSchemaInformation"]
    # Sort tables and columns into consistent order
    return {name: sort_columns(columns) for name, columns in sorted(by_table.items())}


def write_schema(lines):
    code = "\n".join([HEADER] + lines)
    code = ruff_format(code)
    SCHEMA_PYTHON.write_text(code)


def ruff_format(code):
    process = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "-"],
        check=True,
        text=True,
        capture_output=True,
        input=code,
    )
    return process.stdout


def sort_columns(columns):
    # Assert column names are unique
    assert len({c["ColumnName"] for c in columns}) == len(columns)
    # Sort columns lexically except keep `Patient_ID` first
    return sorted(
        columns,
        key=lambda c: (c["ColumnName"] != "Patient_ID", c["ColumnName"]),
    )


def class_name_for_table(name):
    assert is_valid(name), name
    return name


def attr_name_for_column(name):
    name = name.replace(".", "_")
    if name == "class":
        name = "class_"
    assert is_valid(name), name
    return name


def definition_for_column(column):
    default_value, type_formatter = TYPE_MAP[column["ColumnType"]]
    args = [type_formatter(column)]
    if column["IsNullable"] == "False":
        args.append(f"nullable=False, default={default_value!r}")
    else:
        assert column["IsNullable"] == "True", f"Bad `IsNullable` value in {column!r}"
    # If the name isn't a valid Python attribute then we need to supply it explicitly as
    # the first argument
    name = column["ColumnName"]
    if attr_name_for_column(name) != name:
        args.insert(0, repr(name))
    return f"mapped_column({', '.join(args)})"


def format_string_type(type_name, column):
    length = column["MaxLength"]
    collation = column["CollationName"]
    return f"{type_name}({length}, collation={collation!r})"


def format_binary_type(type_name, column):
    length = column["MaxLength"]
    return f"{type_name}({length})"


def is_valid(name):
    return name.isidentifier() and not keyword.iskeyword(name)


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else None
    if command == "fetch":
        fetch_schema_and_data_dictionary()
    elif command == "build":
        build_schema()
    else:
        raise RuntimeError(f"Unknown command: {command}; valid commands: fetch, build")
