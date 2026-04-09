import openpyxl

from tests.backend_schemas.emisv2.script import get_schema_from_csv


def test_get_schema_from_csv(tmp_path):

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "foo_bar"
    worksheet.append(["Column", "Type", "Primary Key", "Foreign Key"])
    worksheet.append(["foo_patient_id", "VARBINARY(32)", "Yes", ""])
    workbook.save(tmp_path / "test_schema.xlsx")

    schema = get_schema_from_csv(tmp_path / "test_schema.xlsx", file_dir=tmp_path)

    assert "foo_bar" in schema
    assert schema["foo_bar"][0]["Column"] == "foo_patient_id"
