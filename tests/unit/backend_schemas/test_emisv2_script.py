import openpyxl

from tests.backend_schemas.emisv2.script import (
    extract_sheets_from_excel_file,
    get_schema_from_csv,
)


def create_test_file(tmp_path):

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "foo_bar"
    worksheet.append(["Column", "Type", "Primary Key", "Foreign Key"])
    worksheet.append(["foo_patient_id", "VARBINARY(32)", "Yes", ""])
    workbook.save(tmp_path / "test_schema.xlsx")
    tmp_file = tmp_path / "test_schema.xlsx"

    return tmp_file


def test_get_schema_from_csv(tmp_path):

    test_excel_file = create_test_file(tmp_path)

    extract_sheets_from_excel_file(test_excel_file, file_dir=tmp_path)

    schema = get_schema_from_csv(file_dir=tmp_path)

    assert "foo_bar" in schema
    assert schema["foo_bar"][0]["Column"] == "foo_patient_id"


def test_old_schema_csv_is_deleted(tmp_path):

    old_file = tmp_path / "old_file.csv"
    old_file.touch()

    test_excel_file = create_test_file(tmp_path)
    extract_sheets_from_excel_file(test_excel_file, file_dir=tmp_path)

    assert not old_file.exists()
    assert (tmp_path / "foo_bar.csv").exists()
