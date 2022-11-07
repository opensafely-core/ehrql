from abc import ABC
from collections.abc import Mapping, MutableMapping, MutableSet


class IdentitySet(MutableSet):
    """
    This set considers objects equal if and only if they are identical, even if they
    have overridden __eq__() and __hash__().

    Adapted with gratitude from https://stackoverflow.com/a/17039643/400467.
    """

    def __init__(self, seq=()):
        self._set = set()
        for value in seq:
            self.add(value)

    def add(self, value):
        self._set.add(Ref(value))

    def discard(self, value):
        self._set.discard(Ref(value))

    def __contains__(self, value):
        return Ref(value) in self._set

    def __len__(self):
        return len(self._set)

    def __iter__(self):
        return (ref.referent for ref in self._set)

    def __repr__(self):  # pragma: no cover
        return f"{type(self).__name__}({list(self)})"


class IdentityDict(MutableMapping):
    """
    This map considers keys equal if and only if they are identical, even if they
    have overridden __eq__() and __hash__().
    """

    def __init__(self, seq=(), **kwargs):
        self._dict = {}
        for k, v in seq:
            self[k] = v
        for k, v in kwargs.items():
            self[k] = v

    def __setitem__(self, key, value):
        self._dict[Ref(key)] = value

    def __delitem__(self, key):
        del self._dict[Ref(key)]

    def __getitem__(self, key):
        return self._dict[Ref(key)]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return (ref.referent for ref in self._dict)

    def __repr__(self):  # pragma: no cover
        return f"{type(self).__name__}({list(self.items())})"


class DefaultDict(Mapping, ABC):
    """
    Mixin to provide defaultdict-like behaviour for custom Mapping classes.

    Must be the first base class of a derived class. Must be mixed in with
    another base class that provides Mapping methods.
    """

    def __init__(self, default_factory=None, **kwargs):
        super().__init__(**kwargs)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        value = self.default_factory()
        self[key] = value
        return value


class DefaultIdentityDict(DefaultDict, IdentityDict):
    pass


class Ref:
    def __init__(self, referent):
        self.referent = referent

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.referent is other.referent

    def __hash__(self):
        return id(self.referent)
