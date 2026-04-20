"""
To generate the relationship diagram:

    # Install the graphviz system binary (this is different from the graphviz python package)
    sudo apt install graphviz

    uv run python -m tests.backend_schemas.emisv2.schema_diagram

NOTE: The diagram is generated from the output of emisv2/script.py. To update the diagram with new schema information,
follow the instructions in emisv2/script.py first.
"""

# pragma: no cover file

from pathlib import Path

import pydot

from .script import get_schema_from_csv


DISTINCT_COLOURS = [
    "#e6194b",
    "#3cb44b",
    "#4363d8",
    "#f58231",
    "#911eb4",
    "#008080",
    "#9a6324",
    "#800000",
    "#808000",
    "#000075",
    "#e32636",
    "#0096ff",
    "#fabed4",
    "#008000",
    "#a9a9a9",
    "#000000",
    "#00827f",
    "#b8860b",
    "#4b0082",
    "#cc3300",
]


def get_colour(index):
    return DISTINCT_COLOURS[index % len(DISTINCT_COLOURS)]


def rename_schema_table(table_name_from_foreign_key_field):
    """
    Some table names are labelled incorrectly in the foreign key fields. This is known behaviour for two tables:
    1. mapping_dmdpreparation.dmd_product_code_id in the 'medication_drug_record' table
    2. mkb_mapping_attribute.code_id in the 'patient' table
    """
    corrections = {
        "mapping_dmdpreparation": "mkb_mapping_dmdpreparation",
        "mkb_mapping_attribute": "mkb_mapping_attributes",
    }
    return corrections.get(
        table_name_from_foreign_key_field, table_name_from_foreign_key_field
    )


def main():
    emis_schema = get_schema_from_csv()

    graph = pydot.Dot("my_graph", nodesep="2", ranksep="2", splines="compound")
    graph.set_type("digraph")

    # List of tuples which holds the foreign key links between tables
    foreign_key_links = []

    table_colours = {}

    for index, (table_name, table_content) in enumerate(emis_schema.items()):
        table_name = table_name.strip()
        table_items = [table_name]

        for row in table_content:
            column_name = row["Column"].strip()
            if row["Foreign Key"]:
                foreign_key = row["Foreign Key"].split(",")

                for key in foreign_key:
                    table, primary_key = key.split(".")
                    table = table.strip()

                    if table not in emis_schema:
                        table = rename_schema_table(table)

                    foreign_key_links.append(
                        (
                            f"{table_name}:{column_name}",
                            f"{table}:{primary_key.strip()}",
                        )
                    )

            table_items.append(f"<{column_name}> {column_name}")

        # Organises the columns from top to bottom in a stacked structure: "{A | B | C | D}"
        full_label = "{" + "|".join(table_items) + "}"

        colour = get_colour(index)
        table_colours[table_name] = colour
        my_node = pydot.Node(
            table_name,
            label=full_label,
            shape="record",
            color=colour,
            penwidth="4",
            fontsize="30",
        )
        graph.add_node(my_node)

    # Add foreign key links between tables
    for from_table, to_table in foreign_key_links:
        source_table = from_table.split(":")[0]
        my_edge = pydot.Edge(
            from_table, to_table, color=table_colours[source_table], penwidth="4"
        )
        graph.add_edge(my_edge)

    path = Path(__file__).parent / "schema_relationship_diagram.svg"
    graph.write_svg(path)
    print(f"Diagram saved to {path}")


if __name__ == "__main__":
    main()
