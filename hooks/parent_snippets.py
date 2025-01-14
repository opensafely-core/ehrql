import re


def on_page_markdown(markdown, page, **kwargs):
    """
    parent_snippet markers are snippets that are intended to be replaced in the parent
    site with appropriate snippet notation.  The snippets themselves do not live in
    this repo.

    on_page_* methods are called for each Page in a mkdocs site and can modify the
    markdown they are given as input.  We're using this method to look for the
    parent_includes markers and replace them with a note box that indicates in the
    built docs that this snippet will be replaced in the full docs build.

    For example:
        !!! parent_snippet:'includes/glossary.md'

    will be replaced with:
        !!! note "TO BE REPLACED IN FULL DOCS BUILD
            This snippet will be replaced in the main docs with the parent file 'includes/glossary.md'

    This allows docs imported from other repos (e.g. ehrql) to reference snippets
    in the parent docs, such as the glossary.
    """
    parent_snippets = set(re.findall(r"!!! parent_snippet:.+\n", markdown))
    for parent_snippet in parent_snippets:
        markdown = markdown.replace(
            parent_snippet,
            '\n\n!!! note "TO BE REPLACED IN FULL DOCS BUILD"\n\n\tThis snippet will be replaced in the main docs '
            f"with the parent file {parent_snippet.lstrip('!!! parent_snippet:')}",
        )
    return markdown
