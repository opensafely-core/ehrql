"""
To use this script:

Commands:
    fetch <path-to-excel-file>
        Extract each worksheet from the excel file into a csv file. Run this when the EMIS schema spreadsheet is updated)

        python tests/backend_schemas/emisv2/script.py fetch <path-to-excel-file>

    build
        Build a Python schema object from existing csv files
        NOTE: You must run 'fetch' at least once before runnng this command

        python tests/backend_schemas/emisv2/script.py build
"""

import csv
import sys
from pathlib import Path
from pprint import pprint

from openpyxl import load_workbook


RAW_FILES_DIR = Path(__file__).parent / "raw_emis_csv"


def extract_sheets_from_excel_file(excel_file, file_dir=RAW_FILES_DIR):
    workbook = load_workbook(excel_file)
    file_dir.mkdir(parents=True, exist_ok=True)

    # Clear existing files from directory to ensure that only the current schema information exists
    for filename in file_dir.glob("*.csv"):
        filename.unlink()

    for sheet in workbook.worksheets:
        if sheet.title == "High level overview":  # pragma: no cover
            continue

        csv_name = f"{sheet.title}.csv"
        with open(file_dir / csv_name, "w", newline="") as schema_table:
            writer = csv.writer(schema_table)
            for row in sheet.rows:
                writer.writerow([cell.value for cell in row])


def get_schema_from_csv(file_dir=RAW_FILES_DIR):
    """
    Sample schema structure

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

    schema = {}

    # Iterate over csv files in 'raw_emis_csv' directory
    for file in file_dir.glob("*csv"):
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


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else None
    if command == "fetch":
        if len(sys.argv) < 3:
            raise RuntimeError(
                "Missing File: This command requires the path to an Excel file"
            )
        extract_sheets_from_excel_file(sys.argv[2])
    elif command == "build":
        get_schema_from_csv()
    else:
        raise RuntimeError(f"Unknown command: {command}; valid commands: fetch, build")
