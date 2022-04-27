from typing import Any, TypeVar, Union

import pytest

from databuilder.typing_utils import get_typespec, get_typevars, type_matches


def test_get_typevars():
    T = TypeVar("T")
    V = TypeVar("V")
    assert get_typevars(T) == {T}
    assert get_typevars(dict[T, list[set[V]]]) == {T, V}
    assert get_typevars(dict[tuple[T], set[T]]) == {T}


def test_get_typespec():
    assert get_typespec("hello") == str
    assert get_typespec({"hello", "there"}) == set[str]
    assert get_typespec({1: "one", 2: "two"}) == dict[int, str]
    assert get_typespec({1: {0.1, 0.2}, 2: {0.3, 0.4}}) == dict[int, set[float]]
    assert get_typespec({}) == dict[Any, Any]
    assert get_typespec(frozenset()) == frozenset[Any]


def test_get_typespec_errors():
    with pytest.raises(TypeError, match="homogeneous"):
        get_typespec({1, "two"})
    with pytest.raises(TypeError, match="homogeneous"):
        get_typespec({1: "one", "two": "two"})
    with pytest.raises(TypeError, match="homogeneous"):
        get_typespec({1: "one", 2: 2.0})


def test_get_typespec_errors_on_unhandled_container_type():
    with pytest.raises(AssertionError):
        # We haven't taught it how to destructure lists so this should error
        get_typespec([1, 2, 3])


def test_type_matches():
    assert type_matches(list[str], list[Union[int, str]], {})
    assert type_matches(dict[str, FileNotFoundError], dict[Any, OSError], {})


def test_type_matches_and_sets_typevar():
    T = TypeVar("T")
    Numeric = TypeVar("Numeric", int, float)
    ctx = {}
    assert type_matches(dict[str, str], dict[T, T], ctx)
    assert type_matches(dict[int, int], dict[Numeric, Numeric], ctx)
    assert ctx[T] == str
    assert ctx[Numeric] == int


def test_type_matches_and_sets_typevar_with_any():
    T = TypeVar("T")
    ctx = {}
    assert type_matches(list[Any], list[T], ctx)
    assert ctx[T] == Any


def test_type_matches_and_sets_typevar_with_any_and_concrete_type():
    T = TypeVar("T")
    ctx = {}
    assert type_matches(dict[Any, int], dict[T, T], ctx)
    assert ctx[T] == int


def test_any_matches_bound_type_var():
    T = TypeVar("T")
    ctx = {T: bool}
    assert type_matches(Any, T, ctx)


def test_type_matches_rejects_mismatch():
    Numeric = TypeVar("Numeric", int, float)
    assert not type_matches(list[str], list[int], {})
    assert not type_matches(tuple[int], list[int], {})
    assert not type_matches(list[str], list[Numeric], {})
    assert not type_matches(list[float], list[Union[int, str]], {})
    assert not type_matches(list, list[int], {})
    assert not type_matches(bool, Numeric, {})


def test_type_matches_only_with_consistent_typevar():
    T = TypeVar("T")
    ctx = {}
    assert not type_matches(dict[int, bool], dict[T, T], ctx)
    assert not type_matches(dict[str, str], dict[T, T], ctx)
