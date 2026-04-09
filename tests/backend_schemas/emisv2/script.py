"""
Before running this script, save the EMIS v2 schema excel file in:

    tests/backend_schemas/emisv2/raw_emis_csv/raw_emisv2_schema/

This directory is listed in .gitignore and will not be committed.

To run this script:
    python3 tests/backend_schemas/emisv2/script.py "excel_schema_file.xlsx"
"""

import argparse
import csv
from pathlib import Path
from pprint import pprint

from openpyxl import load_workbook


RAW_FILES_DIR = Path(__file__).parent / "raw_emis_csv"
EXCEL_INPUT_DIR = RAW_FILES_DIR / "raw_emisv2_schema"

EXCEL_INPUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_sheets_from_excel_file(excel_file, file_dir):
    workbook = load_workbook(EXCEL_INPUT_DIR / excel_file)
    file_dir.mkdir(exist_ok=True)

    for sheet in workbook.worksheets:
        if sheet.title == "High level overview":  # pragma: no cover
            continue

        csv_name = f"{sheet.title}.csv"
        with open(file_dir / csv_name, "w", newline="") as schema_table:
            writer = csv.writer(schema_table)
            for row in sheet.rows:
                writer.writerow([cell.value for cell in row])


def get_schema_from_csv(excel_file, file_dir=None):
    """
    Example generated schema

    schema = {
            "patient": [
                {
                    "Column": "patient_id",
                    "Type": "VARBINARY(16)",
                    "Primary Key": "Yes",
                    "Foreign Key": "",
                },
                {
                    "Column": "date_of_birth",
                    "Type": "timestamp(6)",
                    "Primary Key": "",
                    "Foreign Key": "",
                },
            ],
            "medication": [
                ...
            ],
        }

    """

    if file_dir is None:  # pragma: no cover
        file_dir = RAW_FILES_DIR

    extract_sheets_from_excel_file(excel_file, file_dir)

    schema = {}

    # Iterate over sub directories in 'raw_emis_csv' directory
    for file in file_dir.iterdir():
        # Confirm that it's a csv file
        if file.suffix == ".csv":
            table_name = file.stem
            with open(file) as csv_file:
                reader = csv.DictReader(csv_file)

                schema[table_name] = []

                for row in reader:
                    schema[table_name].append(
                        {
                            "Column": row["Column"],
                            "Type": row["Type"],
                            "Primary Key": row["Primary Key"],
                            "Foreign Key": row["Foreign Key"],
                        }
                    )

    pprint(schema)
    return schema


def run():  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file", type=str, help="Raw file as received from EMIS for v2 backend"
    )
    args = parser.parse_args()

    get_schema_from_csv(args.input_file)


if __name__ == "__main__":  # pragma: no cover
    run()
