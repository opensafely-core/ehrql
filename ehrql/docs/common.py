import textwrap


def build_hierarchy(contract):
    # get the contract's hierarchy without the contracts path prefix
    hierarchy = contract.__module__.removeprefix("ehrql.contracts.")

    # split up on dots and let the docs plugin handle rendering
    return hierarchy.split(".")


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
