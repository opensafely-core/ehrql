from urllib.parse import unquote

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


def test_metadata_to_list_with_normal_values():
    # Keys/values we expect to actually use (project, job id, user name/id etc) will
    # normally just be alphanumeric/hyphen/underscore and url-encoding won't change
    # them
    metadata_dict = {"job-id": "job_1234", "user.name": "a-user"}
    assert metadata_to_list(metadata_dict) == ["job-id=job_1234", "user.name=a-user"]


def test_metadata_to_list_urlencodes_special_characters():
    # Arbitrary characters that would break the "key=value" formatting or the SQL
    # comment/HTTP header they get embedded in are safe since they're urlencoded
    metadata_dict = {"a key": "a value\nwith a newline", "a=key": "a&value"}
    assert metadata_to_list(metadata_dict) == [
        "a%20key=a%20value%0Awith%20a%20newline",
        "a%3Dkey=a%26value",
    ]


def test_metadata_to_list_round_trip():
    # Make sure we can parse and unparse as expected
    metadata_dict = {"a=key with spaces": "a value with=an equals sign"}
    tags = metadata_to_list(metadata_dict)
    comment = " ".join(tags)

    parsed = {}
    for tag in comment.split(" "):
        key, value = tag.split("=", 1)
        parsed[unquote(key)] = unquote(value)

    assert parsed == metadata_dict
