backend_template = """
Contracts implemented:

{contracts}

"""


def render_backend_old(backend_data):
    contracts = [
        (c, c.lower().replace("/", "")) for c in sorted(backend_data["contracts"])
    ]
    contracts = "\n".join(
        f"* [`{name}`](contracts-reference.md#{link})" for name, link in contracts
    )

    return (
        backend_template.format(
            name=backend_data["name"],
            contracts=contracts,
        ).strip()
        + "\n"
    )
