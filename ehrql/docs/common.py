import inspect
import textwrap
from collections import ChainMap


def reformat_docstring(d):
    """Reformat docstring to make it easier to use in a markdown/HTML document."""
    if d is None:
        return ""
    # Note that before de-indenting we strip leading newlines but not leading whitespace
    # more generally. This means we can correctly handle docstrings like:
    #
    #   class Foo:
    #       """
    #       Blah blah
    #       blah
    #       """
    #
    return textwrap.dedent(d.lstrip("\n")).strip()


def get_class_attrs(cls):
    # We can't iterate the class attributes directly because that would invoke the
    # `Series` descriptors, and we can't use `inspect.getmembers_static` because that
    # loses the definition order which we want to retain. For the same reason we exclude
    # `object` as we want methods in the order _we_ define them, not those in which they
    # happen to be defined on `object`.
    return dict(ChainMap(*[vars(base) for base in cls.__mro__ if base is not object]))


def get_arguments(function, ignore_self=False):
    signature = inspect.signature(function)
    parameters = list(signature.parameters.values())
    if ignore_self:
        assert parameters[0].name == "self"
        parameters = parameters[1:]
    return {
        param.name: {
            "default": None if param.default is param.empty else repr(param.default),
            "repeatable": param.kind is param.VAR_POSITIONAL,
        }
        for param in parameters
    }
