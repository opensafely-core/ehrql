from pathlib import Path

import pytest

from databuilder import codelist, codelist_from_csv, combine_codelists, table

from .lib.mock_backend import ctv3_event, patient
from .lib.util import OldCohortWithPopulation


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


def test_codelist_query(engine):
    input_data = [
        patient(
            1,
            ctv3_event(code="abc", date="2021-01-01"),
            ctv3_event(code="xyz", date="2021-02-01"),
            ctv3_event(code="foo", date="2021-03-01"),
        ),
        patient(2, ctv3_event(code="bar", date="2021-01-01")),
        patient(3, ctv3_event(code="ijk", date="2021-01-01")),
    ]
    engine.setup(input_data)

    # Insert a load of extra codes as padding to force this test to exercise
    # the "insert in multiple batches" codepath
    extra_codes = [f"Code{n}" for n in range(1100)]
    test_codelist = codelist(["abc", "xyz", *extra_codes, "ijk"], system="ctv3")

    class Cohort(OldCohortWithPopulation):
        code = (
            table("clinical_events")
            .filter("code", is_in=test_codelist)
            .latest()
            .get("code")
        )

    result = engine.extract(Cohort)
    assert result == [
        {"patient_id": 1, "code": "xyz"},
        {"patient_id": 2, "code": None},
        {"patient_id": 3, "code": "ijk"},
    ]


def test_codelist_equals_query(engine):
    input_data = [
        patient(1, ctv3_event(code="abc", date="2021-01-01")),
        patient(2, ctv3_event(code="bar", date="2021-01-01")),
        patient(3, ctv3_event(code="ijk", date="2021-01-01")),
    ]
    engine.setup(input_data)

    # A single code codelist can be expressed as an equals query
    test_codelist = codelist(["abc"], system="ctv3")

    class Cohort(OldCohortWithPopulation):
        code = (
            table("clinical_events")
            .filter("code", is_in=test_codelist)
            .latest()
            .get("code")
        )

    result = engine.extract(Cohort)
    assert result == [
        {"patient_id": 1, "code": "abc"},
        {"patient_id": 2, "code": None},
        {"patient_id": 3, "code": None},
    ]


def test_codelist_query_selects_correct_system(engine):
    input_data = [
        patient(
            1,
            ctv3_event(code="abc", date="2021-01-01"),
            ctv3_event(code="sabc", date="2021-01-01", system="snomed"),
        ),
        patient(2, ctv3_event(code="sabc", date="2021-01-01")),
        patient(3, ctv3_event(code="ijk", date="2021-01-01", system="snomed")),
    ]
    engine.setup(input_data)

    test_codelist = codelist(["sabc", "sxyz", "ijk"], system="snomed")

    class Cohort(OldCohortWithPopulation):
        code = (
            table("clinical_events")
            .filter("code", is_in=test_codelist)
            .latest()
            .get("code")
        )

    result = engine.extract(Cohort)
    # extracts only the snomed events, even though there are matching codes in ctv3 events
    assert result == [
        {"patient_id": 1, "code": "sabc"},
        {"patient_id": 2, "code": None},
        {"patient_id": 3, "code": "ijk"},
    ]


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


def test_codelist_query_with_codelist_from_csv(engine, codelist_csv):
    input_data = [
        patient(1, ctv3_event(code="abc", date="2021-01-01")),
        patient(2, ctv3_event(code="bar", date="2021-01-01")),
        patient(3, ctv3_event(code="ijk", date="2021-01-01")),
    ]
    engine.setup(input_data)

    codelist_csv_path = codelist_csv("long_csv")

    class Cohort(OldCohortWithPopulation):
        _codelist = codelist_from_csv(codelist_csv_path, system="ctv3")
        code = (
            table("clinical_events")
            .filter("code", is_in=_codelist)
            .latest()
            .get("code")
        )

    result = engine.extract(Cohort)
    assert result == [
        {"patient_id": 1, "code": "abc"},
        {"patient_id": 2, "code": None},
        {"patient_id": 3, "code": None},
    ]
