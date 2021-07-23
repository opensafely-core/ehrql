import re
from pathlib import Path

import pytest
from lib.mock_backend import Events, MockBackend, RegistrationHistory
from lib.util import extract

from cohortextractor import (
    codelist,
    codelist_from_csv,
    combine_codelists,
    filter_codes_by_category,
    table,
)


@pytest.fixture
def codelist_csv():
    def csv_path(codelist_name):
        return (
            Path(__file__).parent.absolute()
            / "fixtures"
            / "codelist_csvs"
            / f"{codelist_name}.csv"
        )

    return csv_path


@pytest.mark.integration
def test_codelist_query(database, setup_test_database):
    input_data = [
        # Patient 1
        RegistrationHistory(PatientId=1),
        Events(PatientId=1, EventCode="abc", Date="2021-1-1"),
        Events(PatientId=1, EventCode="xyz", Date="2021-2-1"),
        Events(PatientId=1, EventCode="foo", Date="2021-3-1"),
        # Patient 2
        RegistrationHistory(PatientId=2),
        Events(PatientId=2, EventCode="bar", Date="2021-1-1"),
        # Patient 3
        RegistrationHistory(PatientId=3),
        Events(PatientId=3, EventCode="ijk", Date="2021-1-1"),
    ]
    setup_test_database(input_data)

    # Insert a load of extra codes as padding to force this test to exercise
    # the "insert in multiple batches" codepath
    extra_codes = [f"Code{n}" for n in range(1100)]
    test_codelist = codelist(["abc", "xyz", *extra_codes, "ijk"], system="ctv3")

    class Cohort:
        code = (
            table("clinical_events")
            .filter("code", is_in=test_codelist)
            .latest()
            .get("code")
        )

    result = extract(Cohort, MockBackend, database)
    assert result == [
        {"patient_id": 1, "code": "xyz"},
        {"patient_id": 2, "code": None},
        {"patient_id": 3, "code": "ijk"},
    ]


@pytest.mark.parametrize(
    "filename,code_column,expected",
    [
        ("default_col", None, ["123A", "123B", "234C", "345D"]),
        ("default_col", "code", ["123A", "123B", "234C", "345D"]),
        ("custom_col", "123Codes", ["123-A", "123-B", "123-C", "123-D"]),
        ("extra_whitespace", "code", ["W123", "W234", "W345", "W456"]),
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
    expected = codelist(
        [
            ("123A", "respiratory"),
            ("123B", "respiratory"),
            ("234C", "other"),
            ("345D", "other"),
        ],
        system="ctv3",
    )
    actual = codelist_from_csv(csv_path, system="ctv3", category_column="category")
    assert actual.codes == expected.codes
    assert actual.system == expected.system
    assert actual.has_categories


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


@pytest.mark.integration
def test_codelist_query_with_codelist_from_csv(
    database, setup_test_database, codelist_csv
):
    input_data = [
        # Patient 1
        RegistrationHistory(PatientId=1),
        Events(PatientId=1, EventCode="abc", Date="2021-1-1"),
        # Patient 2
        RegistrationHistory(PatientId=2),
        Events(PatientId=2, EventCode="bar", Date="2021-1-1"),
        # Patient 3
        RegistrationHistory(PatientId=3),
        Events(PatientId=3, EventCode="ijk", Date="2021-1-1"),
    ]
    setup_test_database(input_data)

    codelist_csv_path = codelist_csv("long_csv")

    class Cohort:
        _codelist = codelist_from_csv(codelist_csv_path, system="ctv3")
        code = (
            table("clinical_events")
            .filter("code", is_in=_codelist)
            .latest()
            .get("code")
        )

    result = extract(Cohort, MockBackend, database)
    assert result == [
        {"patient_id": 1, "code": "abc"},
        {"patient_id": 2, "code": None},
        {"patient_id": 3, "code": None},
    ]


def test_filter_codes_by_category():
    codes = codelist([("1", "A"), ("2", "B"), ("3", "A"), ("4", "C")], "ctv3")
    filtered = filter_codes_by_category(codes, include=["B", "C"])
    assert filtered.system == codes.system
    assert filtered.codes == [("2", "B"), ("4", "C")]


def test_combine_codelists_with_categories():
    list_1 = codelist([("A", "foo"), ("B", "bar")], system="icd10")
    list_2 = codelist([("X", "foo"), ("Y", "bar")], system="icd10")
    combined = combine_codelists(list_1, list_2)
    expected = codelist(
        [("A", "foo"), ("B", "bar"), ("X", "foo"), ("Y", "bar")], system="icd10"
    )
    assert combined.codes == expected.codes
    assert combined.system == expected.system


def test_combine_codelists_mixed_categorisation():
    list_1 = codelist([("A", "foo"), ("B", "bar")], system="icd10")
    list_2 = codelist(["X", "Y", "Z"], system="icd10")
    with pytest.raises(
        ValueError, match="Cannot combine categorised and uncategorised codelists"
    ):
        combine_codelists(list_1, list_2)


def test_combine_codelists_inconsistent_categories():
    list_1 = codelist([("A", "foo"), ("B", "bar")], system="icd10")
    list_2 = codelist([("X", "foo"), ("B", "foo")], system="icd10")
    with pytest.raises(
        ValueError,
        match=re.escape("Inconsistent categorisation: ('B', 'foo') and ('B', 'bar')"),
    ):
        combine_codelists(list_1, list_2)


@pytest.mark.integration
def test_codelist_query_with_categorised_codelist(database, setup_test_database):
    input_data = [
        # Patient 1
        RegistrationHistory(PatientId=1),
        Events(PatientId=1, EventCode="abc", Date="2021-1-1"),
        Events(PatientId=1, EventCode="xyz", Date="2021-2-1"),
        Events(PatientId=1, EventCode="foo", Date="2021-3-1"),
        # Patient 2
        RegistrationHistory(PatientId=2),
        Events(PatientId=2, EventCode="bar", Date="2021-1-1"),
        # Patient 3
        RegistrationHistory(PatientId=3),
        Events(PatientId=3, EventCode="ijk", Date="2021-1-1"),
    ]
    setup_test_database(input_data)

    test_codelist = codelist(
        [("abc", "cat1"), ("xyz", "cat1"), ("foo", "cat2"), ("bar", "cat1")],
        system="ctv3",
    )

    class Cohort:
        category = (
            table("clinical_events")
            .filter("code", is_in=test_codelist)
            .latest()
            .get("category")
        )

    result = extract(Cohort, MockBackend, database)
    assert result == [
        {"patient_id": 1, "category": "cat2"},
        {"patient_id": 2, "category": "cat1"},
        {"patient_id": 3, "category": None},
    ]
