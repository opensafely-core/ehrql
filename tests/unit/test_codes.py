import textwrap

import pytest

from databuilder.codes import (
    BNFCode,
    CodelistError,
    CTV3Code,
    DMDCode,
    ICD10Code,
    OPCS4Code,
    SNOMEDCTCode,
    codelist_from_csv,
    codelist_from_csv_lines,
)


def test_codelist_from_csv(tmp_path):
    csv_file = tmp_path / "codes.csv"
    csv_text = """
        CodeID,foo
        abc00,
        def00,
        """
    csv_file.write_text(textwrap.dedent(csv_text.strip()))
    codelist = codelist_from_csv(csv_file, column="CodeID", system="ctv3")
    assert codelist.codes == {CTV3Code("abc00"), CTV3Code("def00")}


def test_codelist_from_csv_missing_file(tmp_path):
    with pytest.raises(CodelistError, match="no_file_here.csv"):
        codelist_from_csv(
            tmp_path / "no_file_here.csv",
            column="CodeID",
            system="ctv3",
        )


def test_codelist_from_csv_lines():
    csv_lines = [
        "CodeID,foo",
        "abc00,",
        "def00,",
        # Check codes are trimmed
        "ghi00 ,",
        # Check blanks are ignored
        "  ,"
        # Check duplicates are ignored
        " def00,",
    ]
    codelist = codelist_from_csv_lines(
        csv_lines,
        column="CodeID",
        system="ctv3",
    )
    assert codelist.codes == {CTV3Code("abc00"), CTV3Code("def00"), CTV3Code("ghi00")}


def test_codelist_from_csv_lines_missing_column():
    csv_lines = [
        "CodeID",
        "abc00",
    ]
    with pytest.raises(CodelistError, match="no_col_here"):
        codelist_from_csv_lines(
            csv_lines,
            column="no_col_here",
            system="ctv3",
        )


def test_codelist_from_csv_lines_unknown_system():
    csv_lines = [
        "CodeID",
        "abc00",
    ]
    with pytest.raises(CodelistError, match="not_a_real_system"):
        codelist_from_csv_lines(
            csv_lines,
            column="CodeID",
            system="not_a_real_system",
        )


def test_codelist_from_csv_lines_with_categories():
    csv_lines = [
        "CodeID,cat1,__str__",
        "abc00,123,foo",
        "def00,456,bar,",
        "ghi00 ,789",
        ",",
    ]
    codelist = codelist_from_csv_lines(
        csv_lines,
        column="CodeID",
        system="ctv3",
    )
    # Sensibly named category is accessible as an attribute
    assert codelist.cat1 == {
        CTV3Code("abc00"): "123",
        CTV3Code("def00"): "456",
        CTV3Code("ghi00"): "789",
    }
    # Poorly named category is still accessible via the dictionary
    assert codelist.category_maps["__str__"] == {
        CTV3Code("abc00"): "foo",
        CTV3Code("def00"): "bar",
        CTV3Code("ghi00"): "",
    }


@pytest.mark.parametrize(
    "cls,value",
    [
        (BNFCode, "0101010I0AAAEAE"),
        (BNFCode, "23965909711"),
        (CTV3Code, "ABC01"),
        (CTV3Code, "De4.."),
        (ICD10Code, "A01"),
        (ICD10Code, "A012"),
        (OPCS4Code, "B23"),
        (OPCS4Code, "B234"),
        (SNOMEDCTCode, "1234567890"),
    ],
)
def test_valid_codes(cls, value):
    assert cls(value).value == value


@pytest.mark.parametrize(
    "cls,value",
    [
        # Digit (5) instead of letter as first character of Product
        (BNFCode, "0101010I05AAEAE"),
        # Appliance but too many digits
        (BNFCode, "239659097111"),
        # Wrong length
        (CTV3Code, "ABC0"),
        # Dot other than at the end
        (CTV3Code, "ABC.0"),
        # Letter other than at the start
        (ICD10Code, "AA1"),
        # Wrong length
        (ICD10Code, "A0124"),
        # I is not an allowed first character
        (OPCS4Code, "I00"),
        # Too short
        (SNOMEDCTCode, "123"),
        # Too long
        (SNOMEDCTCode, "12345678901234567890"),
        # Leading zero
        (SNOMEDCTCode, "0123456789"),
    ],
)
def test_invalid_codes(cls, value):
    with pytest.raises(ValueError):
        cls(value)


def test_syntactically_equivalent_codes():
    # No point duplicating the tests here, but we'll need to test them if we ever stop
    # sharing the regex
    assert DMDCode.regex == SNOMEDCTCode.regex
