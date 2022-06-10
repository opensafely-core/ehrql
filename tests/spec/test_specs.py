from databuilder.docs.specs import (
    build_chapter,
    build_section,
    concatenate_optional_text,
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
