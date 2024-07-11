from typing import Any, TypeVar

import pytest

from ehrql.utils.typing_utils import get_typespec, get_typevars, type_matches


T = TypeVar("T")
V = TypeVar("V")
Numeric = TypeVar("Numeric", int, float)


@pytest.mark.parametrize(
    "typespec,typevars",
    [
        (T, {T}),
        (dict[T, list[set[V]]], {T, V}),
        (dict[tuple[T], set[T]], {T}),
    ],
)
def test_get_typevars(typespec, typevars):
    assert get_typevars(typespec) == typevars


@pytest.mark.parametrize(
    "value,typespec",
    [
        ("hello", str),
        ({"hello", "there"}, set[str]),
        ({"hello", 1}, set[str | int]),
        ({1: "one", 2: "two"}, dict[int, str]),
        ({1: {0.1, 0.2}, 2: {0.3, 0.4}}, dict[int, set[float]]),
        ({1: "one", "two": 2.0}, dict[int | str, str | float]),
        ({}, dict[Any, Any]),
        (frozenset(), frozenset[Any]),
        (int, type[int]),
    ],
)
def test_get_typespec(value, typespec):
    assert get_typespec(value) == typespec


def test_get_typespec_errors_on_unhandled_container_type():
    with pytest.raises(AssertionError):
        # We haven't taught it how to destructure lists so this should error
        get_typespec([1, 2, 3])


@pytest.mark.parametrize(
    "matches,typespec_a,typespec_b",
    [
        (True, list[str], list[int | str]),
        (True, dict[str, FileNotFoundError], dict[Any, OSError]),
        (True, int | str, str | int),
        (True, int | str, int | float | str),
        (True, FileNotFoundError | FileExistsError, OSError),
        (True, FileNotFoundError | UnicodeError, OSError | ValueError),
        (False, list[str], list[int]),
        (False, tuple[int], list[int]),
        (False, list[str], list[Numeric]),
        (False, list[float], list[int | str]),
        (False, list, list[int]),
        (False, bool, Numeric),
    ],
)
def test_type_matches(matches, typespec_a, typespec_b):
    assert type_matches(typespec_a, typespec_b, {}) == matches


def test_type_matches_and_sets_typevar():
    ctx = {}
    assert type_matches(dict[str, str], dict[T, T], ctx)
    assert type_matches(dict[int, int], dict[Numeric, Numeric], ctx)
    assert ctx[T] is str
    assert ctx[Numeric] is int


def test_type_matches_and_sets_typevar_with_any():
    ctx = {}
    assert type_matches(list[Any], list[T], ctx)
    assert ctx[T] is Any


def test_type_matches_and_sets_typevar_with_class_type():
    ctx = {}
    assert type_matches(type[int], type[T], ctx)
    assert ctx[T] is int


def test_type_matches_and_sets_typevar_with_any_and_concrete_type():
    ctx = {}
    assert type_matches(dict[Any, int], dict[T, T], ctx)
    assert ctx[T] is int


def test_any_matches_bound_type_var():
    ctx = {T: bool}
    assert type_matches(Any, T, ctx)


def test_type_matches_only_with_consistent_typevar():
    ctx = {}
    assert not type_matches(dict[int, bool], dict[T, T], ctx)
    assert not type_matches(dict[str, str], dict[T, T], ctx)
