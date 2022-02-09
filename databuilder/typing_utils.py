"""
This module contains some utilities for doing runtime type-checking. It is in no sense
complete in that there are large areas of Python's type system which it doesn't attempt
to handle. Its aim is to implement just enough behaviour to provide the validation
needed by the Query Model.
"""
import typing
from collections.abc import Mapping, Set
from functools import singledispatch


def get_typevars(typespec):
    "Return set of all TypeVars nested anywhere inside `typespec`"
    if isinstance(typespec, typing.TypeVar):
        return {typespec}
    else:
        return set().union(*[get_typevars(arg) for arg in typing.get_args(typespec)])


def type_matches(type_, spec, typevar_context):
    """
    Checks that the type given by `type_` matches the specification given by `spec`

    For example:

        `dict[str, FileNotFoundError]` matches `dict[Any, OSError]`

    Because `str` matches `Any` and `FileNotFoundError` is a subclass of `OSError`.

    The specification may contain TypeVars. The first match for each variable will bind
    its value, recording it in the `typevar_context` dict. Subsequent uses of the
    variable will fail to match if they don't have the same type. By sharing the
    `typevar_context` dict across different calls to this function you can enforce
    consistent interpretation of the TypeVar.

    For example, both the below calls will match:

        T = TypeVar("T")
        type_matches(dict[int, int], dict[T, T], {})
        type_matches(dict[str, str], dict[T, T], {})

    But these will fail:

        ctx = {}
        type_matches(dict[int, bool], dict[T, T], ctx)
        type_matches(dict[str, str], dict[T, T], ctx)

    The first because the value of T is internally inconsistent; the second because
    although it is internally consistent it is inconsistent with the previous example
    whose context it shares.
    """
    # If `spec` is a type variable
    if isinstance(spec, typing.TypeVar):
        # Check the type constraints are met, if any
        if spec.__constraints__:
            if not any(
                type_matches(type_, subspec, typevar_context)
                for subspec in spec.__constraints__
            ):
                return False
        # If we've already assigned a value for this variable (and it wasn't the Any
        # type) then check it matches
        if spec in typevar_context and typevar_context[spec] != typing.Any:
            if typevar_context[spec] != type_:
                return False
        # Otherwise record this value as the value of the TypeVar
        else:
            typevar_context[spec] = type_
        return True

    # `Any` is the easy case: it just matches everything
    if type_ is typing.Any or spec is typing.Any:
        return True

    spec_origin = typing.get_origin(spec)
    spec_args = typing.get_args(spec)

    # If there's no origin type that means `spec` is an ordinary class
    if spec_origin is None:
        return type_ is not None and issubclass(type_, spec)
    elif spec_origin is typing.Union:
        # For union types we just need to match one of the arguments
        return any(type_matches(type_, arg, typevar_context) for arg in spec_args)
    else:
        # Otherwise we get origin and args for `type_` and check that each element
        # matches
        type_origin = typing.get_origin(type_)
        if not type_matches(type_origin, spec_origin, typevar_context):
            return False
        type_args = typing.get_args(type_)
        for type_arg, spec_arg in zip(type_args, spec_args):
            if not type_matches(type_arg, spec_arg, typevar_context):
                return False
        return True


@singledispatch
def get_typespec(value):
    """
    Return a type specification for the supplied value. In simple cases this is just
    like `type()` e.g.

        get_typespec(1) == int

    But this function knows how to destructure some container types so that e.g.

        get_typespec({1, 2, 3}) == Set[int]

    Additionally, through the magic of singledispatch, it can be taught to destructure
    other container types it doesn't yet know about.
    """
    return type(value)


@get_typespec.register(Set)
def get_typespec_for_set(value):
    member_types = {get_typespec(i) for i in value}
    if len(member_types) > 1:
        raise TypeError(f"Sets must be of homogeneous type: {value!r}")
    elif member_types:
        member_type = list(member_types)[0]
    else:
        # Allow empty sets
        member_type = typing.Any
    return type(value)[member_type]


@get_typespec.register(Mapping)
def get_typespec_for_mapping(value):
    key_types = {get_typespec(i) for i in value.keys()}
    value_types = {get_typespec(i) for i in value.values()}
    if len(key_types) > 1:
        raise TypeError(f"Mappings must be of homogeneous key type: {value!r}")
    elif len(value_types) > 1:
        raise TypeError(f"Mappings must be of homogeneous value type: {value!r}")
    elif key_types and value_types:
        key_type = list(key_types)[0]
        value_type = list(value_types)[0]
    else:
        # Allow empty mappings
        key_type = typing.Any
        value_type = typing.Any
    return type(value)[key_type, value_type]
