import ast
import inspect
import textwrap


def function_body_as_string(function):
    """
    Return the de-indented source code of the body of a function

    This is useful for being able to specify the contents of test fixtures without
    having to make them seperate files (which makes the tests harder to follow) or to
    declare them as string literals (where you lose the benefits of syntax highlighting
    and other tooling).

    Note that one downside of this vs string literals is that you can't use templating
    in the same way to dynamically generate the fixture. Instead, you need to find some
    way of specifying your placeholder values as valid Python and then call `.replace()`
    on the resulting string.
    """
    source = textwrap.dedent(inspect.getsource(function))
    parsed = ast.parse(source)
    assert isinstance(parsed, ast.Module)
    func_def = parsed.body[0]
    assert isinstance(func_def, ast.FunctionDef)
    first_line = func_def.body[0].lineno
    body_lines = source.split("\n")[first_line - 1 :]
    return textwrap.dedent("\n".join(body_lines))
