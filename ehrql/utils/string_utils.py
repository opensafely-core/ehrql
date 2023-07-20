import textwrap


def strip_indent(s):
    """
    Remove indentation from a multiline string

    This is especially useful for taking docstrings and displaying them as markdown.
    Note that before de-indenting we strip leading newlines but not leading whitespace
    more generally. This allow us to have the opening quotes on a different line from
    the text body.
    """
    return textwrap.dedent(s.lstrip("\n")).strip()
