chapter_template = """
## {id} {title}{text}
"""

section_template = """
### {id} {title}{text}
"""


paragraph_template = """
#### {id} {title}{text}

This example makes use of {intro} containing the following data:

{input_tables}

```python
{series}
```
returns the following patient series:

| patient | value |
| - | - |
{output_rows}

"""


def build_rows(data):
    # create rows in the form " 1 | 2 | 3"
    # (cells may contain | characters which need escaping)
    rows = ["|".join(map(lambda x: x.replace("|", r"\|"), row)) for row in data]

    # add leading and trailing pipes
    rows = [f"| {row} |" for row in rows]

    return rows


def iter_input_tables_intro(names):
    name_lut = {
        "e": "an event-level",
        "p": "a patient-level",
    }

    for name in names:
        yield f"{name_lut[name]} table named `{name}`"


def iter_input_tables(tables):
    for name, raw_rows in tables.items():
        rows = build_rows(raw_rows)

        # only create as many columns as the data has
        columns = len(raw_rows[0])
        rows.insert(1, f"|{' - |' * columns}")

        yield "\n".join(rows)


def render_specs(specs_data):
    outputs = []
    for chapter in specs_data:  # 3
        add_descriptive_text(chapter)
        output = chapter_template.format(**chapter)
        outputs.append(output)

        for section in chapter["sections"]:  # 3.1
            add_descriptive_text(section)
            output = section_template.format(**section)
            outputs.append(output)

            for paragraph in section["paragraphs"]:  # 3.1.1
                intro = " and ".join(
                    iter_input_tables_intro(paragraph["tables"].keys())
                )
                input_tables = "\n\n".join(iter_input_tables(paragraph["tables"]))
                output_rows = "\n".join(build_rows(paragraph["output"]))
                add_descriptive_text(paragraph)

                output = paragraph_template.format(
                    **paragraph,
                    intro=intro,
                    input_tables=input_tables,
                    output_rows=output_rows,
                )
                outputs.append(output)

    return "\n".join(outputs).strip() + "\n"


def add_descriptive_text(data):
    data["text"] = "\n" + data["text"] if "text" in data else ""
