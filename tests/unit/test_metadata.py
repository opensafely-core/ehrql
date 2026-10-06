import pytest

from ehrql.metadata import metadata_to_list, parse_metadata


def test_parse_metadata_handles_empty_value():
    assert parse_metadata({}) == {}
    assert parse_metadata({"EHRQL_METADATA": ""}) == {}


def test_parse_metadata():
    assert parse_metadata({"EHRQL_METADATA": '{"user": "testuser", "foo": "1"}'}) == {
        "user": "testuser",
        "foo": "1",
    }


def test_parse_metadata_only_allows_strings():
    with pytest.raises(AssertionError, match="metadata values must be strings"):
        parse_metadata({"EHRQL_METADATA": '{"foo": 1}'})


def test_metadata_as_strings():
    metadata_dict = {"user": "testuser", "project": "myproject"}
    assert metadata_to_list(metadata_dict) == ["user=testuser", "project=myproject"]
