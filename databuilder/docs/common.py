def build_hierarchy(contract):
    # get the contract's hierarchy without the contracts path prefix
    hierarchy = contract.__module__.removeprefix("databuilder.contracts.")

    # split up on dots and let the docs plugin handle rendering
    return hierarchy.split(".")


def reformat_docstring(d):
    """Reformat docstring to make it easier to use in a markdown/HTML document."""
    if d is None:
        return []

    docstring = d.strip()

    return [line.strip() for line in docstring.splitlines()]
