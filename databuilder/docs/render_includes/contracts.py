contract_template = """
## {name}

{docstring}

| Column name | Description | Type | Constraints |
| ----------- | ----------- | ---- | ----------- |
{columns}

{backend_support}
"""


def render_contracts(contracts_data):
    outputs = []

    for contract in contracts_data:
        hierarchy = [h.title() for h in contract["hierarchy"]]
        name = "/".join([*hierarchy, contract["name"]])
        docstring = "\n".join(contract["docstring"])
        columns = "\n".join(
            f"| {c['name']} | {c['description']} | {c['type']} | {', '.join(c['constraints']).capitalize()}. |"
            for c in contract["columns"]
        )

        output = contract_template.format(
            name=name,
            docstring=docstring,
            columns=columns,
            backend_support="",
        )

        outputs.append(output)

    return "\n".join(outputs).strip() + "\n"
