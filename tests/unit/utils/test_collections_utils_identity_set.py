from databuilder.utils.collections_utils import IdentitySet


def test_repr():
    s = IdentitySet([1, 2, 3])
    assert eval(repr(s)) == s


def test_empty_means_empty():
    assert len(IdentitySet()) == 0


def test_can_be_initialized_with_contents():
    s = IdentitySet([1, 2, 3])
    assert len(s) == 3
    assert 1 in s


def test_adding():
    s = IdentitySet()
    s.add(1)
    assert len(s) == 1
    assert 1 in s


def test_duplicates_are_ignored():
    s = IdentitySet([1])
    s.add(1)
    assert len(s) == 1


def test_can_iterate_over_contents():
    s = IdentitySet([1, 2])
    assert list(s) == [1, 2]


def test_removing():
    s = IdentitySet([1])
    s.remove(1)
    assert len(s) == 0
    assert 1 not in s


def test_discard_is_idempotent():
    IdentitySet().discard(1)  # no error


def test_construction_distinguishes_between_equal_but_non_identical_objects():
    s = IdentitySet([AlwaysEqual(), AlwaysEqual()])
    assert len(s) == 2


def test_adding_distinguishes_between_equal_but_non_identical_objects():
    s = IdentitySet()
    s.add(AlwaysEqual())
    s.add(AlwaysEqual())
    assert len(s) == 2


def test_discarding_distinguishes_between_equal_but_non_identical_objects():
    s = IdentitySet([AlwaysEqual()])
    s.discard(AlwaysEqual())
    assert len(s) == 1


def test_contains_distinguishes_between_equal_but_non_identical_objects():
    assert AlwaysEqual() not in IdentitySet([AlwaysEqual()])


class AlwaysEqual:
    def __eq__(self, other):
        return True  # pragma: no cover

    def __hash__(self):
        return 1  # pragma: no cover
