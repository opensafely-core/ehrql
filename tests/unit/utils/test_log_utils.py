from ehrql.utils import log_utils


def test_kv():
    assert log_utils.kv({}) == ""
    assert (
        log_utils.kv({"foo": "foo", "bar": 1, "baz": [1, 2, 3]})
        == "foo=foo bar=1 baz=[1, 2, 3]"
    )


def test_indent():
    lines = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing\n"
        "elit, sed do eiusmod tempor incididunt ut labore et\n"
        "dolore magna aliqua."
    )
    expected = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing\n"
        "    elit, sed do eiusmod tempor incididunt ut labore et\n"
        "    dolore magna aliqua."
    )

    assert log_utils.indent(lines, prefix="    ") == expected
