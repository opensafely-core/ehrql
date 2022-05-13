import pytest

from databuilder.codes import CodelistError, CTV3Code, codelist_from_csv


def test_codelist_from_csv(tmp_path):
    csv_file = tmp_path / "codes.csv"
    csv_file.write_text("CodeID,foo\nabc,123\ndef,456\n ghi ,789\n,")
    codes = codelist_from_csv(csv_file, "CodeID", "ctv3")
    assert codes == {CTV3Code("abc"), CTV3Code("def"), CTV3Code("ghi")}


def test_codelist_from_csv_missing_column(tmp_path):
    csv_file = tmp_path / "codes.csv"
    csv_file.write_text("CodeID,foo\nabc,123\n,def,456\n ghi ,789")
    with pytest.raises(CodelistError, match="no_col_here"):
        codelist_from_csv(csv_file, "no_col_here", "ctv3")


def test_codelist_from_csv_missing_file(tmp_path):
    with pytest.raises(CodelistError, match="no_file_here.csv"):
        codelist_from_csv(tmp_path / "no_file_here.csv", "CodeID", "ctv3")


def test_codelist_from_csv_unknown_system():
    with pytest.raises(CodelistError, match="not_a_real_system"):
        codelist_from_csv("somefile.csv", "CodeID", "not_a_real_system")
