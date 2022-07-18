import pytest

from databuilder.docs.specs import (
    build_chapter,
    build_section,
    concatenate_optional_text,
    get_series_code,
    get_title_for_test_fn,
)


def test_concatenate_optional_text_present():
    first_dict = {"a": 0, "b": 1}
    text = "test"
    combined_dict = concatenate_optional_text(first_dict, text)
    assert "text" in combined_dict, "optional text not present"
    assert combined_dict["text"] == "test", "incorrect value for optional text"


def test_concatenate_optional_text_absent():
    first_dict = {"a": 0, "b": 1}
    text = None
    combined_dict = concatenate_optional_text(first_dict, text)
    assert "text" not in combined_dict, "optional text present"


def test_build_chapter_empty_sections():
    chapter = build_chapter(1, "dummy", [])
    assert chapter["id"] == 1
    assert chapter["title"] == "Dummy chapter for testing spec generation"
    assert chapter["text"] == "This chapter should not appear in the table of contents"


def test_build_section():
    section = build_section(1, "dummy", "test_dummy")
    assert section["id"] == 1
    assert section["title"] == "Dummy section for testing spec generation"
    assert section["text"] == "This section should not appear in the table of contents"
    paragraphs = section["paragraphs"]
    assert len(paragraphs) == 2
    for paragraph in paragraphs:
        if paragraph["id"] == "1.1":
            assert (
                paragraph["text"] == "this docstring should appear in the spec"
            ), "paragraph text not found when docstring present"
            continue
        if paragraph["id"] == "1.2":
            assert (
                "text" not in paragraph
            ), "paragraph text found when no docstring present"
            continue
        assert False, "expected paragraph ids not found"


def test_take_with_expr():
    pass


test_take_with_expr.title = "Take rows that match an expression"


def test_take_with_constant_true():
    pass


@pytest.mark.parametrize(
    "test_fn,title",
    [
        (test_take_with_expr, "Take rows that match an expression"),
        (test_take_with_constant_true, "Take with constant true"),
    ],
)
def test_get_title_for_test_fn(test_fn, title):
    assert get_title_for_test_fn(test_fn) == title


@pytest.mark.parametrize(
    "source_lines,source_index,includes_population,expected",
    [
        (
            # single line
            ['p.d1.is_before("2000-01-20"),'],
            0,
            False,
            'p.d1.is_before("2000-01-20")',
        ),
        (
            # multiple lines
            [
                "case(",
                "    when(p.i1 < 8).then(p.i1),",
                "    when(p.i1 > 8).then(100),",
                "),",
            ],
            0,
            False,
            "case(\n    when(p.i1 < 8).then(p.i1),\n    when(p.i1 > 8).then(100),\n)",
        ),
        (
            # real test function; multiple lines, series starts after table_data
            [
                "    spec_test(",
                "        table_data,",
                "        case(",
                "            when(p.i1 < 8).then(p.i1),",
                "            when(p.i1 > 8).then(100),",
                "        ),",
                "        {",
                "            1: 6,",
                "            2: 7,",
                "            3: None,",
                "            4: 100,",
                "            5: None,",
                "        },",
                "    )",
            ],
            2,
            False,
            "case(\n    when(p.i1 < 8).then(p.i1),\n    when(p.i1 > 8).then(100),\n)",
        ),
        (
            # incomplete series definition; this should never happen as it should only exist if
            # there's a syntax error in a specs tests, which would raise an error earlier than
            # this code
            ["p.d1.is_before("],
            0,
            False,
            "p.d1.is_before(",
        ),
        (
            # with population definition
            ['p.d1.is_before("2000-01-20"),', "population=p.b1"],
            0,
            True,
            'p.d1.is_before("2000-01-20")\nset_population(p.b1)',
        ),
        (
            # incomplete population definition; this should also never happen
            ['p.d1.is_before("2000-01-20"),', 'population=p.d2.is_before("2000-01-'],
            0,
            True,
            'p.d1.is_before("2000-01-20")\nset_population(p.d2.is_before("2000-01-)',
        ),
    ],
)
def test_get_series_code(source_lines, source_index, includes_population, expected):
    assert (
        get_series_code(source_lines, source_index, set_population=includes_population)
        == expected
    )
