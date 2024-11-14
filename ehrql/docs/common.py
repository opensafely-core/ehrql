import ast
import datetime
import inspect
import textwrap
from collections import ChainMap

from ehrql.codes import BaseCode, BaseMultiCodeString
from ehrql.utils.string_utils import strip_indent


def get_class_attrs(cls):
    # We can't iterate the class attributes directly because that would invoke the
    # `Series` descriptors, and we can't use `inspect.getmembers_static` because that
    # loses the definition order which we want to retain. For the same reason we exclude
    # `object` as we want methods in the order _we_ define them, not those in which they
    # happen to be defined on `object`.
    return dict(ChainMap(*[vars(base) for base in cls.__mro__ if base is not object]))


def get_docstring(obj, default=None):
    docstring = obj.__doc__
    if not docstring:
        if default is None:
            raise ValueError(f"No docstring defined for public object {obj}")
        else:
            docstring = default
    return strip_indent(docstring)


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


def get_function_body(function):
    """
    Return the de-indented source code of the body of a function, excluding its
    declaration and any docstring
    """
    source = textwrap.dedent(inspect.getsource(function))
    parsed = ast.parse(source)
    assert isinstance(parsed, ast.Module)
    func_def = parsed.body[0]
    assert isinstance(func_def, ast.FunctionDef)
    first_elem = func_def.body[0]
    has_docstring = (
        isinstance(first_elem, ast.Expr)
        and isinstance(first_elem.value, ast.Constant)
        and isinstance(first_elem.value.value, str)
    )
    if not has_docstring:
        first_line = find_first_line_of_function_body(func_def)
    else:
        first_line = first_elem.end_lineno + 1
    body_lines = source.split("\n")[first_line - 1 :]
    return textwrap.dedent("\n".join(body_lines))


def find_first_line_of_function_body(func_def):
    # Getting the line number of the first code object in the function body misses out
    # any comments which come above that line. There doesn't seem to be a nicer way of
    # finding the last line of the declaration than finding the maximum line number over
    # all the components of the declaration.
    elements = [
        *func_def.args.args,
        *func_def.args.posonlyargs,
        *func_def.args.kwonlyargs,
        func_def.args.vararg,
        func_def.args.kwarg,
        func_def.returns,
    ]
    return max(el.end_lineno for el in elements if el is not None) + 1


def get_name_for_type(type_):
    if type_ is BaseCode:
        return "code"
    if issubclass(type_, BaseCode):
        return f"{type_.__doc__} code"
    if type_ is BaseMultiCodeString:
        return "multi code string"
    if issubclass(type_, BaseMultiCodeString):
        return f"{type_.__doc__}"
    return {
        bool: "boolean",
        int: "integer",
        float: "float",
        str: "string",
        datetime.date: "date",
    }[type_]
