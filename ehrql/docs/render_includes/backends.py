BACKEND_TEMPLATE = """\
## {name}
<small class="subtitle">
  <a href="https://github.com/opensafely-core/ehrql/blob/main/{file_path}">
    <code>{dotted_path}</code>
  </a>
</small>

{docstring}

This backend implements the following table schemas:

{schema_list}
"""


def render_backends(backend_data):
    return "\n".join(
        BACKEND_TEMPLATE.format(
            **backend,
            schema_list="\n".join(
                f" * [{schema}](schemas/{schema}.md)"
                for schema in backend["implements"]
            ),
        )
        for backend in backend_data
    )
