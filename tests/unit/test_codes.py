import textwrap
from pathlib import Path

import pytest

from ehrql.codes import (
    BNFCode,
    CodelistError,
    CTV3Code,
    DMDCode,
    ICD10Code,
    ICD10MultiCodeString,
    OPCS4Code,
    OPCS4MultiCodeString,
    SNOMEDCTCode,
    codelist_from_csv,
    codelist_from_csv_lines,
)


# `codelist_from_csv` can take either a string or `pathlib.Path` and we want to check
# that we handle both correctly
@pytest.fixture(params=[str, Path])
def path_type(request):
    return request.param


def test_codelist_from_csv(path_type, tmp_path):
    csv_file = tmp_path / "codes.csv"
    csv_text = """
        CodeID,foo
        abc00,
        def00,
        """
    csv_file.write_text(textwrap.dedent(csv_text.strip()))
    codelist = codelist_from_csv(path_type(csv_file), column="CodeID")
    assert codelist == ["abc00", "def00"]


def test_codelist_from_csv_missing_file(path_type):
    missing_file = Path(__file__) / "no_file_here.csv"
    with pytest.raises(CodelistError, match="no_file_here.csv"):
        codelist_from_csv(path_type(missing_file), column="CodeID")


def test_codelist_from_csv_missing_file_hint(path_type):
    bad_path = Path(__file__) / "bad\file.csv"
    with pytest.raises(CodelistError, match="backslash"):
        codelist_from_csv(path_type(bad_path), column="CodeID")


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
    codelist = codelist_from_csv_lines(csv_lines, column="CodeID")
    assert codelist == ["abc00", "def00", "ghi00"]


def test_codelist_from_csv_lines_missing_column():
    csv_lines = [
        "CodeID",
        "abc00",
    ]
    with pytest.raises(CodelistError, match="no_col_here"):
        codelist_from_csv_lines(csv_lines, column="no_col_here")


def test_codelist_from_csv_lines_with_category_column():
    csv_lines = [
        "CodeID,Cat1",
        "abc00,foo",
        "def00,bar",
        "ghi00,",
    ]
    codelist = codelist_from_csv_lines(
        csv_lines,
        column="CodeID",
        category_column="Cat1",
    )
    assert codelist == {
        "abc00": "foo",
        "def00": "bar",
        "ghi00": "",
    }


def test_codelist_from_csv_lines_with_missing_category_column():
    csv_lines = [
        "CodeID,Cat1",
        "abc00,foo",
    ]
    with pytest.raises(CodelistError, match="no_col_here"):
        codelist_from_csv_lines(
            csv_lines,
            column="CodeID",
            category_column="no_col_here",
        )


@pytest.mark.parametrize(
    "cls,value",
    [
        (BNFCode, "0101010I0AAAEAE"),
        (BNFCode, "23965909711"),
        (CTV3Code, "ABC01"),
        (CTV3Code, "De4.."),
        (SNOMEDCTCode, "1234567890"),
    ],
)
def test_valid_single_codes(cls, value):
    assert cls(value).value == value


@pytest.mark.parametrize(
    "singlecode_cls,multicode_cls,value",
    [
        (ICD10Code, ICD10MultiCodeString, "A01"),
        (ICD10Code, ICD10MultiCodeString, "A012"),
        (ICD10Code, ICD10MultiCodeString, "A01X"),
        (OPCS4Code, OPCS4MultiCodeString, "B23"),
        (OPCS4Code, OPCS4MultiCodeString, "B234"),
    ],
)
def test_valid_single_codes_match_multi_codes(singlecode_cls, multicode_cls, value):
    # tests that the same exact codes are valid on single and multiclass versions.
    # they use different regex because multiclass allows prefix matching but
    # single class does not, so this test ensures same behaviour across both regexen.
    assert singlecode_cls(value).value == value
    assert multicode_cls.is_valid(value)


@pytest.mark.parametrize(
    "cls,value",
    [
        (ICD10MultiCodeString, "A"),
        (ICD10MultiCodeString, "A0"),
        (OPCS4MultiCodeString, "B"),
        (OPCS4MultiCodeString, "B2"),
    ],
)
def test_valid_multi_codes_prefix_matching(cls, value):
    assert cls.is_valid(value)


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
        # Too short
        (SNOMEDCTCode, "123"),
        # Too long
        (SNOMEDCTCode, "12345678901234567890"),
        # Leading zero
        (SNOMEDCTCode, "0123456789"),
    ],
)
def test_invalid_single_codes(cls, value):
    with pytest.raises(ValueError):
        cls(value)


@pytest.mark.parametrize(
    "singlecode_cls,multicode_cls,value",
    [
        # Letter other than at the start
        (ICD10Code, ICD10MultiCodeString, "AA1"),
        # Wrong length
        (ICD10Code, ICD10MultiCodeString, "A0124"),
        # Letter other than X as 4th character
        (ICD10Code, ICD10MultiCodeString, "A01Y"),
        # X as 3rd character
        (ICD10Code, ICD10MultiCodeString, "A1X"),
        # empty
        (ICD10Code, ICD10MultiCodeString, ""),
        # I is not an allowed first character
        (OPCS4Code, OPCS4MultiCodeString, "I00"),
        # empty
        (OPCS4Code, OPCS4MultiCodeString, ""),
        # too long
        (OPCS4Code, OPCS4MultiCodeString, "B1234"),
    ],
)
def test_invalid_single_codes_match_multicodes(singlecode_cls, multicode_cls, value):
    with pytest.raises(ValueError):
        singlecode_cls(value)
    assert not multicode_cls.is_valid(value)


def test_syntactically_equivalent_codes():
    # No point duplicating the tests here, but we'll need to test them if we ever stop
    # sharing the regex
    assert DMDCode.regex == SNOMEDCTCode.regex
