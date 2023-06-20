import csv
import keyword
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import black
import requests


SERVER_URL = "https://jobs.opensafely.org"
WORKSPACE_NAME = "tpp-database-schema"
OUTPUTS_INDEX_URL = (
    f"{SERVER_URL}/datalab/opensafely-internal/{WORKSPACE_NAME}/outputs/"
)

SCHEMA_DIR = Path(__file__).parent
SCHEMA_CSV = SCHEMA_DIR / "tpp_schema.csv"
SCHEMA_PYTHON = SCHEMA_DIR / "tpp_schema.py"

TYPE_MAP = {
    "bit": lambda _: "t.Boolean",
    "tinyint": lambda _: "t.SMALLINT",
    "int": lambda _: "t.Integer",
    "bigint": lambda _: "t.BIGINT",
    "numeric": lambda _: "t.Numeric",
    "float": lambda _: "t.Float",
    "real": lambda _: "t.REAL",
    "date": lambda _: "t.Date",
    "time": lambda _: "t.Time",
    "datetime": lambda _: "t.DateTime",
    "char": lambda col: format_string_type("t.CHAR", col),
    "varchar": lambda col: format_string_type("t.VARCHAR", col),
    "varbinary": lambda col: format_string_type("t.VARBINARY", col),
}

HEADER = """
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
"""


def fetch_schema():
    # There's currently no API to get the latest output from a workspace so we use a
    # regex to extract output IDs from the workspace's outputs page.
    index_page = requests.get(OUTPUTS_INDEX_URL)
    escaped_path = re.escape(urlparse(OUTPUTS_INDEX_URL).path)
    url_re = re.compile(rf"{escaped_path}(\d+)/")
    ids = url_re.findall(index_page.text)
    max_id = max(map(int, ids))
    # Once we have the ID we can fetch the output manifest using the API
    outputs_api = f"{SERVER_URL}/api/v2/workspaces/{WORKSPACE_NAME}/snapshots/{max_id}"
    outputs = requests.get(outputs_api, headers={"Accept": "application/json"}).json()
    # And that gives us the URL for the file
    file_urls = [f["url"] for f in outputs["files"] if f["name"] == "output/rows.csv"]
    assert len(file_urls) == 1
    file_url = urljoin(SERVER_URL, file_urls[0])
    response = requests.get(file_url)
    SCHEMA_CSV.write_text(response.text)


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
    # Apply some custom modifications to the schema. Ideally we wouldn't have to do this
    # at all as it undermines (to some extent) the point of automating the schema build,
    # but sadly it's necessary.
    apply_schema_modifications(by_table)
    # Sort tables and columns into consistent order
    return {name: sort_columns(columns) for name, columns in sorted(by_table.items())}


def apply_schema_modifications(by_table):
    # We don't include the schema information table in the schema information because
    #  a) where would this madness end?
    #  b) it contains some weird types like `sysname` that we don't want to have to
    #     worry about.
    del by_table["OpenSAFELYSchemaInformation"]

    # For some reason, the `CodedEvent_SNOMED` table isn't included in the schema so we
    # have to add it here. See:
    # https://github.com/opensafely/tpp-database-schema/issues/49
    #
    # The columns and types are taken from the old Cohort Extractor
    # test setup code:
    # https://github.com/opensafely-core/cohort-extractor/blob/bdf82919/tests/tpp_backend_setup.py#L150-L161
    assert "CodedEvent_SNOMED" not in by_table
    by_table["CodedEvent_SNOMED"] = [
        {"ColumnName": "Patient_ID", "ColumnType": "bigint"},
        {"ColumnName": "CodedEvent_ID", "ColumnType": "bigint"},
        {"ColumnName": "NumericValue", "ColumnType": "real"},
        {"ColumnName": "ConsultationDate", "ColumnType": "datetime"},
        {"ColumnName": "ConceptID", "ColumnType": "varchar", "MaxLength": "18"},
        {"ColumnName": "CodingSystem", "ColumnType": "int"},
    ]

    assert "CustomMedicationDictionary" not in by_table
    by_table["CustomMedicationDictionary"] = [
        {"ColumnName": "DMD_ID", "ColumnType": "varchar", "MaxLength": "50"},
        {"ColumnName": "MultilexDrug_ID", "ColumnType": "varchar", "MaxLength": "767"},
    ]

    # We don't get column collation information but we know this matters in some cases
    # because you can't compare columns across tables unless the collations are
    # compatible. We add collations here for the two critical columns whose collations
    # we're aware of (because they caused us problems in the distant past).
    # https://github.com/opensafely/tpp-database-schema/issues/50
    add_to_column(
        by_table["CodedEvent"],
        "CTV3Code",
        collation="Latin1_General_BIN",
    )
    add_to_column(
        by_table["MedicationDictionary"],
        "DMD_ID",
        collation="Latin1_General_CI_AS",
    )
    add_to_column(
        by_table["CustomMedicationDictionary"],
        "DMD_ID",
        collation="Latin1_General_CI_AS",
    )


def write_schema(lines):
    lines[:0] = [HEADER.strip()]
    code = "\n".join(lines)
    code = black.format_str(code, mode=black.Mode())
    SCHEMA_PYTHON.write_text(code)


def sort_columns(columns):
    # Assert column names are unique
    assert len({c["ColumnName"] for c in columns}) == len(columns)
    # Sort columns lexically except keep `Patient_ID` first
    return sorted(
        columns,
        key=lambda c: (c["ColumnName"] != "Patient_ID", c["ColumnName"]),
    )


def add_to_column(columns, name, **kwargs):
    for column in columns:
        if column["ColumnName"] == name:
            column.update(kwargs)
            return
    assert False, f"Column '{name}' not found"


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
    type_formatter = TYPE_MAP[column["ColumnType"]]
    args = [type_formatter(column)]
    # If the name isn't a valid Python attribute then we need to supply it explicitly as
    # the first argument
    name = column["ColumnName"]
    if attr_name_for_column(name) != name:
        args.insert(0, repr(name))
    return f"mapped_column({', '.join(args)})"


def format_string_type(type_name, column):
    args = column["MaxLength"]
    if collation := column.get("collation"):
        args += f", collation={collation!r}"
    return f"{type_name}({args})"


def is_valid(name):
    return name.isidentifier() and not keyword.iskeyword(name)


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else None
    if command == "fetch":
        fetch_schema()
    elif command == "build":
        build_schema()
    else:
        raise RuntimeError(f"Unknown command: {command}; valid commands: fetch, build")
