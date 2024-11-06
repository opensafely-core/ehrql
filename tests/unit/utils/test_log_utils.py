from ehrql.utils import log_utils


def test_kv():
    assert log_utils.kv({}) == ""
    assert (
        log_utils.kv({"foo": "foo", "bar": 1, "baz": [1, 2, 3]})
        == "foo=foo bar=1 baz=[1, 2, 3]"
    )
