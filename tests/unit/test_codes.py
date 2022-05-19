import textwrap

import pytest

from databuilder.codes import CodelistError, CTV3Code, codelist_from_csv


def test_codelist_from_csv(tmp_path):
    csv_file = tmp_path / "codes.csv"
    csv_text = """
        CodeID,foo
        abc,123
        def,456
        ghi ,789
        ,
        """
    csv_file.write_text(textwrap.dedent(csv_text.strip()))
    codelist = codelist_from_csv(csv_file, "CodeID", "ctv3")
    assert codelist.codes == {CTV3Code("abc"), CTV3Code("def"), CTV3Code("ghi")}


def test_codelist_from_csv_missing_column(tmp_path):
    csv_file = tmp_path / "codes.csv"
    csv_file.write_text("CodeID,foo\nabc,123\n,def,456\n ghi ,789")
    with pytest.raises(CodelistError, match="no_col_here"):
        codelist_from_csv(csv_file, "no_col_here", "ctv3")


def test_codelist_from_csv_missing_file(tmp_path):
    with pytest.raises(CodelistError, match="no_file_here.csv"):
        codelist_from_csv(tmp_path / "no_file_here.csv", "CodeID", "ctv3")


def test_codelist_from_csv_unknown_system(tmp_path):
    csv_file = tmp_path / "codes.csv"
    csv_file.touch()
    with pytest.raises(CodelistError, match="not_a_real_system"):
        codelist_from_csv(csv_file, "CodeID", "not_a_real_system")


def test_codelist_from_csv_with_categories(tmp_path):
    csv_file = tmp_path / "codes.csv"
    csv_text = """
        CodeID,cat1,__str__
        abc,123,foo
        def,456,bar,
        ghi ,789
        ,
        """
    csv_file.write_text(textwrap.dedent(csv_text.strip()))
    codelist = codelist_from_csv(csv_file, "CodeID", "ctv3")
    # Sensibly named category is accessible as an attribute
    assert codelist.cat1 == {
        CTV3Code("abc"): "123",
        CTV3Code("def"): "456",
        CTV3Code("ghi"): "789",
    }
    # Poorly named category is still accessible via the dictionary
    assert codelist.category_maps["__str__"] == {
        CTV3Code("abc"): "foo",
        CTV3Code("def"): "bar",
        CTV3Code("ghi"): "",
    }
