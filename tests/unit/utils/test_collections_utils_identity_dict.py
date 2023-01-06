from pytest import raises

from databuilder.utils.collections_utils import DefaultIdentityDict, IdentityDict


def test_repr():
    s = IdentityDict(a=1, b=2, c=3)
    assert eval(repr(s)) == s


def test_empty_means_empty():
    assert len(IdentityDict()) == 0


def test_can_be_initialized_with_contents():
    d = IdentityDict(a=1)
    assert len(d) == 1
    assert "a" in d
    assert d["a"] == 1


def test_setting():
    d = IdentityDict()
    d["a"] = 1
    assert len(d) == 1
    assert "a" in d
    assert d["a"] == 1


def test_overriding_a_value():
    d = IdentityDict(a=1)
    d["a"] = 2
    assert d["a"] == 2


def test_removing():
    d = IdentityDict(a=1)
    del d["a"]
    assert len(d) == 0
    assert "a" not in d


def test_can_iterate_over_contents():
    d = IdentityDict(a=1, b=2)
    assert list(d.items()) == [("a", 1), ("b", 2)]


def test_construction_distinguishes_between_equal_but_non_identical_objects():
    k1 = AlwaysEqual()
    k2 = AlwaysEqual()
    s = IdentityDict([(k1, 1), (k2, 2)])
    assert len(s) == 2
    assert s[k1] == 1
    assert s[k2] == 2


def test_adding_distinguishes_between_equal_but_non_identical_objects():
    k1 = AlwaysEqual()
    k2 = AlwaysEqual()
    s = IdentityDict()
    s[k1] = 1
    s[k2] = 2
    assert len(s) == 2
    assert s[k1] == 1
    assert s[k2] == 2


def test_deleting_distinguishes_between_equal_but_non_identical_objects():
    s = IdentityDict([(AlwaysEqual(), 1)])
    with raises(KeyError):
        del s[AlwaysEqual()]
    assert len(s) == 1


def test_contains_distinguishes_between_equal_but_non_identical_objects():
    assert AlwaysEqual() not in IdentityDict([(AlwaysEqual(), 1)])


def test_default_identity_dict_provides_default():
    assert DefaultIdentityDict(default_factory=lambda: "fish")["a"] == "fish"


def test_default_identity_dict_persists_retrieved_defaults():
    d = DefaultIdentityDict(default_factory=lambda: "fish")
    assert len(d) == 0
    _ = d["a"]
    assert len(d) == 1


def test_default_identity_dict_admits_setting_values():
    def f():
        return None  # pragma: no cover

    assert DefaultIdentityDict(f, a=1)["a"] == 1


def test_default_identity_dict_raises_without_factory():
    with raises(KeyError):
        _ = DefaultIdentityDict(default_factory=None)["a"]


class AlwaysEqual:
    def __eq__(self, other):
        return True  # pragma: no cover

    def __hash__(self):
        return 1  # pragma: no cover
