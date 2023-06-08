import ast
import inspect
import textwrap


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
