SORT_ORDER = {k: i for i, k in enumerate(["core", "tpp"])}


def get_tables_with_dummy_data_constraints_in_schema(schema):
    return {
        table["name"]: columns
        for table in schema["tables"]
        if (columns := get_columns_with_dummy_data_constraints_in_table(table))
    }


def get_columns_with_dummy_data_constraints_in_table(table):
    return [
        (column["name"], column["dummy_data_constraints"])
        for column in table["columns"]
        if column.get("dummy_data_constraints")
    ]


def render_dummy_data_constraints(schemas):
    sections = []
    for schema in sorted(schemas, key=sort_key):
        tables = get_tables_with_dummy_data_constraints_in_schema(schema)
        if not tables:
            continue
        sections.append(
            f"### `{schema['dotted_path']}`\n\n{''.join(render_tables(tables))}"
        )
    return "\n".join(sections).strip() + "\n"


def render_tables(tables):
    return [
        f"#### `{table_name}`\n\n{''.join(render_columns(columns))}"
        for table_name, columns in sorted(tables.items())
    ]


def render_columns(columns):
    return [
        f'<div markdown="block" class="indent">\n'
        f"\n"
        f"`{column_name}`\n"
        f"\n"
        f"{render_bullets(constraints)}\n"
        f"\n"
        f"</div>\n"
        f"\n"
        for column_name, constraints in columns
    ]


def render_bullets(constraints):
    return "\n".join(f"* {c}" for c in constraints)


def sort_key(schema):
    k = schema["name"]
    return SORT_ORDER.get(k, float("+inf")), k
