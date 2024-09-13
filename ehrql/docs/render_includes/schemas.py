SCHEMA_INDEX_TEMPLATE = """\
## [{name}](schemas/{name}.md)
<small class="subtitle">
  <a href="./{name}/"> view details → </a>
</small>

{implemented_by_list}

{docstring}
"""


def render_schema_index(schemas):
    return "\n".join(
        SCHEMA_INDEX_TEMPLATE.format(
            **schema,
            implemented_by_list=implemented_by_list(schema["implemented_by"], depth=1),
        )
        for schema in schemas
    )


def implemented_by_list(backends, depth=1):
    assert len(backends) > 0
    if depth > 1:
        url_prefix = "/".join([".."] * (depth - 1)) + "/"
    else:
        url_prefix = ""
    backend_links = [
        f"[**{backend}**]({url_prefix}backends.md#{backend.lower()})"
        for backend in backends
    ]
    return f"Available on backends: {', '.join(backend_links)}"


SCHEMA_TEMPLATE = """\
# <strong>{name}</strong> schema

{implemented_by_list}

{docstring}

``` {{.python .copy title='To use this schema in an ehrQL file:'}}
from {dotted_path} import (
{table_imports}
)
```

{table_descriptions}
"""


def render_schema(schema):
    return SCHEMA_TEMPLATE.format(
        **schema,
        implemented_by_list=implemented_by_list(schema["implemented_by"], depth=2),
        table_imports=table_imports(schema["tables"]),
        table_descriptions=table_descriptions(schema["tables"]),
    )


def table_imports(tables):
    return "\n".join(f"    {table['name']}," for table in tables)


TABLE_TEMPLATE = """\
<p class="dimension-indicator"><code>{dimension}</code></p>
## {name}

{docstring}
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
{column_descriptions}
  </dl>
</div>
{helper_methods}
"""


def table_descriptions(tables):
    return "\n".join(
        TABLE_TEMPLATE.format(
            **table,
            column_descriptions=column_descriptions(table["name"], table["columns"]),
            dimension=(
                "one row per patient"
                if table["has_one_row_per_patient"]
                else "many rows per patient"
            ),
            helper_methods=helper_methods(table["name"], table["methods"]),
        )
        for table in tables
    )


COLUMN_TEMPLATE = """\
<div markdown="block">
  <dt id="{column_id}">
    <strong>{name}</strong>
    <a class="headerlink" href="#{column_id}" title="Permanent link">🔗</a>
    <code>{type}</code>
  </dt>
  <dd markdown="block">
{description_with_constraints}
  </dd>
</div>
"""


def column_descriptions(table_name, columns):
    return "\n".join(
        COLUMN_TEMPLATE.format(
            **column,
            column_id=f"{table_name}.{column['name']}",
            description_with_constraints=description_with_constraints(column),
        )
        for column in columns
    )


def description_with_constraints(column):
    return "\n".join(
        [column["description"], "", *[f" * {c}" for c in column["constraints"]]]
    )


HELPER_METHODS_TEMPLATE = """\
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Methods</div>
  <dl markdown="block">
{method_descriptions}
  </dl>
</div>
"""


def helper_methods(table_name, methods):
    if not methods:
        return ""
    return HELPER_METHODS_TEMPLATE.format(
        method_descriptions="\n".join(
            [method_description(table_name, method) for method in methods]
        )
    )


METHOD_DESCRIPTION_TEMPLATE = """\
<div markdown="block">
  <dt id="{method_id}">
    <strong>{name}(</strong>{argument_list}<strong>)</strong>
    <a class="headerlink" href="#{method_id}" title="Permanent link">🔗</a>
    <code></code>
  </dt>
  <dd markdown="block">
{docstring}
    <details markdown="block">
    <summary>View method definition</summary>
```py
{source}
```
    </details>
  </dd>
</div>
"""


def method_description(table_name, method):
    return METHOD_DESCRIPTION_TEMPLATE.format(
        **method,
        method_id=f"{table_name}.{method['name']}",
        argument_list=", ".join(method["arguments"]),
    )
