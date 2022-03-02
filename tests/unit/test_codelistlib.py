from pathlib import Path

import pytest

from databuilder import codelist, codelist_from_csv, combine_codelists


@pytest.fixture
def codelist_csv():
    def csv_path(codelist_name):
        return (
            Path(__file__).parent.parent.absolute()
            / "fixtures"
            / "codelist_csvs"
            / f"{codelist_name}.csv"
        )

    return csv_path


@pytest.mark.parametrize(
    "filename,code_column,expected",
    [
        ("default_col", None, ("123A", "123B", "234C", "345D")),
        ("default_col", "code", ("123A", "123B", "234C", "345D")),
        ("custom_col", "123Codes", ("123-A", "123-B", "123-C", "123-D")),
        ("extra_whitespace", "code", ("W123", "W234", "W345", "W456")),
    ],
)
def test_codelist_from_csv(codelist_csv, filename, code_column, expected):
    csv_path = codelist_csv(filename)
    kwargs = {"system": "ctv3"}
    if code_column is not None:
        kwargs["column"] = code_column
    test_codelist = codelist_from_csv(csv_path, **kwargs)
    assert test_codelist.codes == expected


def test_codelist_from_csv_unknown_column(codelist_csv):
    csv_path = codelist_csv("custom_col")
    with pytest.raises(
        ValueError,
        match=r"Codelist csv file at .+custom_col.csv does not contain column 'code'",
    ):
        codelist_from_csv(csv_path, system="ctv3")


def test_codelist_from_csv_with_categories(codelist_csv):
    csv_path = codelist_csv("categories")
    with pytest.raises(
        NotImplementedError, match="Categorised codelists are currently unsupported"
    ):
        codelist_from_csv(csv_path, system="ctv3", category_column="category")


def test_codelist_from_csv_file_not_found(codelist_csv):
    csv_path = codelist_csv("unknown")
    kwargs = {"system": "ctv3", "column": "code"}
    with pytest.raises(
        ValueError, match=r"Codelist csv file at .+unknown.csv could not be found"
    ):
        codelist_from_csv(csv_path, **kwargs)


@pytest.mark.parametrize(
    "codes,expected_codes",
    [
        ((["abc", "def"], ["ghi", "jkl"]), ["abc", "def", "ghi", "jkl"]),
        (
            (["abc", "def", "ghi"], ["ghi", "jkl", "mno"]),
            ["abc", "def", "ghi", "jkl", "mno"],
        ),
        (
            (["1", "6", "7", "9"], ["2", "1"], ["9", "5", "1"]),
            ["1", "6", "7", "9", "2", "5"],
        ),
    ],
    ids=[
        "combine 2 codelists",
        "combine 2 codelists with duplicates",
        "combine 3 codelists with duplicates",
    ],
)
def test_combine_codelists(codes, expected_codes):
    codelists_to_combine = [
        codelist(codes_to_combine, system="ctv3") for codes_to_combine in codes
    ]
    combined = combine_codelists(*codelists_to_combine)
    expected = codelist(expected_codes, system="ctv3")
    assert combined.system == expected.system
    assert combined.codes == expected.codes


def test_combine_codelists_different_systems():
    codelist1 = codelist(["abc", "def", "ghi"], system="ctv3")
    codelist2 = codelist(["ghi", "jkl", "mno"], system="ctv2")
    with pytest.raises(
        ValueError,
        match="Cannot combine codelists from different systems: 'ctv3' and 'ctv2'",
    ):
        combine_codelists(codelist1, codelist2)


def test_codelist_repr():
    codes = [ch for ch in "abcdefghijklmnopqrstuvwxyz"]
    codelist1 = codelist(codes[:5], system="ctv3")
    assert repr(codelist1) == "Codelist(system=ctv3, codes=('a', 'b', 'c', 'd', 'e'))"

    codelist2 = codelist(codes[:6], system="ctv3")
    codelist3 = codelist(codes, system="ctv3")
    for cl in [codelist2, codelist3]:
        assert (
            repr(cl) == "Codelist(system=ctv3, codes=('a', 'b', 'c', 'd', 'e', '...'))"
        )
